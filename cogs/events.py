from asyncio import sleep
from collections import OrderedDict
from discord import (
    Guild,
    Member,
    Message,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    VoiceState,
)
from discord.ext.commands import Cog, Context
from logging import info
from re import compile as re_compile
from time import time

from bot import Omnitron
from data.utils import check_bot_starting, is_mod, task_launcher
from data.xp import Xp_class


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.limitation = []
        self.voice_intervals = {}
        self.xp_class = Xp_class(bot)

    """ EVENTS """

    @Cog.listener()
    async def on_ready(self):
        """Check on start if any guilds that the bot is in are not in the DB else initialise moderators list for every guild in the DB"""
        db_guilds = set([int(k) for k in self.bot.main_repo.get_guilds().keys()])
        guilds = set(self.bot.guilds)
        for guild in guilds:
            if guild.id not in db_guilds:
                self.bot.main_repo.create_guild(
                    guild.id, guild.name, f"{guild.owner}"
                )  # If guild is not in DB, create it

            db_users = set(self.bot.user_repo.get_users(guild.id).keys())
            members = set(
                [m for m in guild.members if not m.bot and str(m.id) not in db_users]
            )
            for member in members:
                self.bot.user_repo.create_user(guild.id, member.id, f"{member}")

            self.bot.moderators[guild.id] = list(
                [int(k) for k in self.bot.config_repo.get_moderators(guild.id).keys()]
            )  # Initialize moderators list for every guilds
            self.bot.configs[guild.id] = {
                "prefix": self.bot.config_repo.get_prefix(guild.id)
            }

            xp = self.bot.config_repo.get_xp(guild.id)
            self.bot.configs[guild.id]["xp"] = dict(xp)

            if "boosteds" in xp:
                self.bot.configs[guild.id]["xp"]["boosteds"] = {
                    key: int(value["bonus"]) for key, value in xp["boosteds"].items()
                }

            if "lvl2role" in xp:
                self.bot.configs[guild.id]["xp"]["lvl2role"] = {
                    int(key): guild.get_role(value["role_id"])
                    for key, value in xp["lvl2role"].items()
                }

            if "prestiges" in xp:
                self.bot.configs[guild.id]["xp"]["prestiges"] = {
                    int(key[2]): guild.get_role(value["role_id"])
                    for key, value in xp["prestiges"].items()
                }

            if "notify_channel" in xp:
                self.bot.configs[guild.id]["xp"]["notify_channel"] = guild.get_channel(
                    xp["notify_channel"]
                )

            mute_on_join = self.bot.config_repo.get_mute_on_join(guild.id)
            if mute_on_join:
                self.bot.configs[guild.id]["mute_on_join"] = {
                    "duration": mute_on_join["duration"],
                    "muted_role": guild.get_role(int(mute_on_join["muted_role_id"])),
                }
                if "notify_channel_id" in mute_on_join:
                    self.bot.configs[guild.id]["mute_on_join"][
                        "notify_channel"
                    ] = guild.get_channel(int(mute_on_join["notify_channel_id"]))

            prevent_invites = self.bot.config_repo.get_invit_prevention(guild.id)
            self.bot.configs[guild.id]["prevent_invites"] = (
                {
                    "notify_channel": guild.get_channel(
                        int(prevent_invites["notify_channel_id"])
                    )
                }
                if isinstance(prevent_invites, OrderedDict)
                else None
            )

        self.bot.starting = False

    @Cog.listener()
    @check_bot_starting()
    async def on_guild_join(self, guild: Guild):
        """When the bot joins a guild, add it to the database or set his presence to True if the guild was already stored in the database"""
        self.bot.main_repo.create_guild(guild.id, guild.name, f"{guild.owner}")
        info(f"Joined the guild {guild.name} ({guild.id}), created by {guild.owner}")

    @Cog.listener()
    @check_bot_starting()
    async def on_guild_update(self, before: Guild, after: Guild):
        """When a guild is updated, update the database"""
        updates = {}
        if before.name != after.name:
            updates["name"] = after.name
        if f"{before.owner}" != f"{after.owner}":
            updates["owner"] = f"{after.owner}"
        if updates:
            self.bot.main_repo.update_guild(after.id, updates)

    @Cog.listener()
    @check_bot_starting()
    async def on_guild_remove(self, guild: Guild):
        """When the bot get kicked from a guild, set his presence to False it from the database"""
        self.bot.main_repo.kicked_from_guild(guild.id)
        info(
            f"Kicked from the guild {guild.name} ({guild.id}), created by {guild.owner}"
        )

    @Cog.listener()
    @check_bot_starting()
    async def on_member_join(self, member: Member, tries: int = 0):
        """When a member joins a guild, add him to the database and if the mute_on_join option is on then mute him for a limited amount of time"""
        await self.bot.wait_until_ready()
        if member.bot:
            return
        self.bot.user_repo.create_user(member.guild.id, member.id, f"{member}")
        roles = []
        try:
            if "mute_on_join" in self.bot.configs[member.guild.id]:
                roles += [
                    self.bot.configs[member.guild.id]["mute_on_join"]["muted_role"]
                ]
                await member.add_roles(*roles, reason="Has just joined the server.")
                self.bot.user_repo.mute_user(
                    member.guild.id,
                    member.id,
                    self.bot.configs[member.guild.id]["mute_on_join"]["duration"],
                    time(),
                    f"{self.bot.user}",
                    "joined the server",
                )
                task_launcher(
                    self.mute_completion,
                    (
                        self.bot.user_repo.get_user(member.guild.id, member.id),
                        member.guild.id,
                    ),
                    count=1,
                )
        except KeyError:
            if tries < 3:
                await sleep(5)
                await self.on_member_join(member, tries=tries + 1)

    @Cog.listener()
    @check_bot_starting()
    async def on_message(self, message: Message, tries: int = 0):
        """When a message is sent, if the prevent_invites option is on check if there is an invitation link to another discord server in the message and is the xp is on then manage the user's xp"""
        if message.is_system() or message.author.bot or not message.guild:
            return
        ctx = await self.bot.get_context(message=message)
        try:
            if "prevent_invites" in self.bot.configs[message.guild.id]:
                await self.check_invite(ctx)
            if self.bot.configs[message.guild.id]["xp"]["is_on"]:
                _id = f"{message.guild.id}.{message.author.id}"
                if _id not in self.limitation:
                    await self.xp_class.manage_xp(message.author, "message")
                    self.limitation.append(_id)
                    await self.cooldown_messages(_id)
        except KeyError:
            if tries < 3:
                await sleep(5)
                await self.on_message(message, tries=tries + 1)

    @Cog.listener()
    @check_bot_starting()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        """When a message is edited, if the prevent_invites option is on check if there is an invitation link to another discord server in the message"""
        if "prevent_invites" in self.bot.configs[payload.guild_id]:
            if not payload.guild_id:
                return

            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if message.is_system() or message.author.bot:
                return

            ctx = await self.bot.get_context(message=message)
            await self.check_invite(ctx)

    @Cog.listener()
    @check_bot_starting()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """When a reaction is added, if the user have a prestige pending then handle it according to the reaction added"""
        if payload.member.bot:
            return
        db_user = self.bot.user_repo.get_user(payload.guild_id, payload.user_id)

        if (
            "prestige_pending" in db_user
            and payload.message_id == db_user["prestige_pending"]["confirmation_id"]
        ):
            if payload.emoji.name == "✅":
                await self.xp_class.manage_prestige(payload.member, "added_prestige")
                await payload.member.remove_roles(
                    *[
                        role
                        for role in payload.member.roles
                        if role
                        in (
                            set(
                                self.bot.configs[payload.guild_id]["xp"][
                                    "lvl2role"
                                ].values()
                            )
                            if "lvl2role" in self.bot.configs[payload.guild_id]["xp"]
                            else []
                        )
                        or role
                        in set(
                            self.bot.configs[payload.guild_id]["xp"][
                                "prestiges"
                            ].values()
                        )
                    ]
                )
                await payload.member.add_roles(
                    self.bot.configs[payload.guild_id]["xp"]["prestiges"][
                        (int(db_user["prestige"]) + 1) or 1
                    ]
                )
                self.bot.user_repo.cancel_prestige(payload.guild_id, payload.user_id)

                if "notify_channel" in self.bot.configs[payload.guild_id]["xp"]:
                    await self.bot.configs[payload.guild_id]["xp"][
                        "notify_channel"
                    ].send(
                        f"🎉 - {payload.member.mention} - You have just switched to prestige `{(int(db_user['prestige']) + 1) or 1}` - `{(self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]).name}` ! - 🎉"
                    )
            elif payload.emoji.name == "❌":
                self.bot.user_repo.cancel_prestige(payload.guild_id, payload.user_id)
            else:
                return
            message = await (
                await self.bot.fetch_channel(payload.channel_id)
            ).fetch_message(payload.message_id)
            await message.remove_reaction("✅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, _: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        _id = f"{member.guild.id}.{member.id}"

        if after.channel:
            if _id not in self.voice_intervals:
                self.voice_intervals[_id] = task_launcher(
                    self.vocal_interval, (member,), minutes=7
                )
            elif member.voice.channel.id == self.bot.afk_channel_id:
                self.voice_intervals.pop(_id).cancel()
        else:
            if _id in self.voice_intervals:
                self.voice_intervals.pop(_id).cancel()

    """ METHODS """

    async def mute_completion(self, db_user: OrderedDict, guild_id: int):
        """This method manage the mute completion"""
        await self.bot.wait_until_ready()
        mute = db_user["mutes"][-1]
        timeout = mute["duration_s"] - (time() - mute["at_ms"])
        if timeout <= 0:
            timeout = 2
        await sleep(timeout)
        self.bot.user_repo.unmute_user(guild_id, db_user["id"])
        member = await (await self.bot.fetch_guild(guild_id)).fetch_member(
            db_user["id"]
        )
        await member.remove_roles(
            self.bot.configs[member.guild.id]["mute_on_join"]["muted_role"]
        )
        if mute["reason"] == "joined the server":
            self.bot.user_repo.clear_mutes(guild_id, db_user["id"])
            if "notify_channel" in self.bot.configs[member.guild.id]["mute_on_join"]:
                await self.bot.configs[member.guild.id]["mute_on_join"][
                    "notify_channel"
                ].send(
                    f"🔊 - The member `{member}` has just finished being muted after joining the server! (ID: `{db_user['id']}`)"
                )
        else:
            if "notify_channel" in self.bot.configs[member.guild.id]["mute_on_join"]:
                await self.bot.configs[member.guild.id]["mute_on_join"][
                    "notify_channel"
                ].send(f"🔊 - The member {member.mention} is no longer muted.")

    async def check_invite(self, ctx: Context):
        """This method check if the user sent an invitation link to antoher discord server"""
        if is_mod(ctx.author, self.bot):
            return
        regex = re_compile(
            r"discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})"
        )
        if regex.findall(ctx.message.content):
            links = len(
                [
                    link
                    for link in self.bot.user_repo.get_invites(
                        ctx.guild.id, ctx.author.id
                    )
                ]
            )
            self.bot.user_repo.new_invite(
                ctx.guild.id, ctx.author.id, time(), ctx.message.clean_content
            )
            await ctx.message.delete()

            if "notify_channel" in self.bot.configs[ctx.guild.id]["prevent_invites"]:
                await self.bot.configs[ctx.guild.id]["prevent_invites"][
                    "notify_channel"
                ].send(
                    f"⚠️ - The member `{ctx.author}` tried to send an invitation link to another discord server in {ctx.channel.mention}! => {ctx.message.clean_content}"
                )

            if links > 1:
                self.bot.user_repo.warn_user(
                    ctx.guild.id,
                    ctx.author.id,
                    time(),
                    self.bot.user.display_name,
                    "Sent three invitation links to other servers.",
                )
                self.bot.user_repo.clear_invites(ctx.guild.id, ctx.author.id)
                await ctx.send(
                    f"⚠️ - {ctx.author.mention} - **You've received a warning because you've sent three consecutive invitation links to other discord servers!**",
                    delete_after=30,
                )
            else:
                await ctx.send(
                    f"⛔ - {ctx.author.mention} - **Invitation links to other discord servers are not allowed in this server!**, `{'first' if links == 0 else 'second'} warning`!"
                )

    async def cooldown_messages(self, _id: str):
        """This method manage the messages cooldown"""
        await sleep(5)
        del self.limitation[self.limitation.index(_id)]

    async def vocal_interval(self, member: Member):
        """This method manage the vocal xp cooldown"""
        await self.xp_class.manage_xp(member, "vocal")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
