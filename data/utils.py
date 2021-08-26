from asyncio import sleep
from collections import OrderedDict
from discord import Embed, Guild, Message, Member
from discord.ext.tasks import loop
from discord.ext.commands import Context, check
from discord.ext.commands.errors import BadArgument
from math import floor
from re import compile as re_compile
from time import time
from typing import Union

from bot import Omnitron


class Utils:
    def __init__(self, bot: Omnitron) -> None:
        self.bot = bot

    # The `args` are the arguments passed into the loop
    def task_launcher(self, function, param, **interval) -> loop:
        """Creates new instances of `tasks.Loop`"""
        # Creating the task
        # You can also pass a static interval and/or count
        new_task = loop(**interval)(function)
        # Starting the task
        new_task.start(*param)
        return new_task

    def is_mod(self, member: Member, bot: Omnitron) -> bool:
        return (
            set(member.roles) & set(bot.moderators[member.guild.id])
            or member.id in set(bot.moderators[member.guild.id])
            or member.guild_permissions.administrator
        )

    def is_dj(self, member: Member, bot: Omnitron) -> bool:
        return (
            not bot.djs[member.guild.id]
            or set(member.roles) & set(bot.djs[member.guild.id])
            or member.id in set(bot.djs[member.guild.id])
            or member.guild_permissions.administrator
        )

    async def check_invite(self, ctx: Context):
        """This method check if the user sent an invitation link to antoher discord server"""
        if self.is_mod(ctx.author, ctx.bot):
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

    def have_xp_bonus(self, member: Member) -> bool:
        if "boosteds" not in self.bot.configs[member.guild.id]["xp"]:
            return False
        return set([str(r.id) for r in member.roles]) & set(
            self.bot.configs[member.guild.id]["xp"]["boosteds"]
        ) or str(member.id) in set(self.bot.configs[member.guild.id]["xp"]["boosteds"])

    def get_embed_from_ctx(self, ctx: Context, title: str) -> Embed:
        em = Embed(
            colour=self.bot.color,
            title=title,
            description=f"Use the command format `{self.get_guild_pre(ctx.message)[0]}{ctx.command.qualified_name} <option>` to view more info about an option.",
        )

        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        em.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

        cmds = OrderedDict(
            sorted(
                {
                    c.name: {
                        "brief": c.brief,
                        "description": c.description,
                        "aliases": c.aliases,
                        "usage": c.usage,
                        "commands": c.commands
                        if "all_commands" in vars(c).keys() and c.commands
                        else None,
                    }
                    for c in set(ctx.command.commands)
                }.items()
            )
        )
        for name, cmd in cmds.items():
            em.add_field(
                name=f"{cmd['brief']} {name}",
                value=f"{cmd['description']}"
                + (
                    f"\n**Alias"
                    + ("es" if len(cmd["aliases"]) > 1 else "")
                    + "**: "
                    + ", ".join([f"`{a}`" for a in cmd["aliases"]])
                    if cmd["aliases"]
                    else ""
                )
                + (f"\n**Usage**: `{cmd['usage']}`" if cmd["usage"] else "")
                + (
                    f"\n**Sub-commands:** {', '.join([f'`{cmd.name}`' for cmd in cmd['commands']])}"
                    if cmd["commands"]
                    else ""
                ),
                inline=True,
            )

        return em

    async def parse_duration(
        self, _duration: int, type_duration: str, ctx: Context
    ) -> bool or int:
        type_duration = self.to_lower(type_duration)

        if _duration <= 0:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 0! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=15,
            )
            return False
        elif (
            ctx.command.parents[0].name if ctx.command.parents else ""
        ) == "poll" and (
            _duration <= 600
            and type_duration == "s"
            or _duration <= 10
            and type_duration == "m"
        ):
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 10 minutes to create a poll! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=15,
            )
            return False

        if type_duration == "s":
            return _duration * 1
        elif type_duration == "m":
            return _duration * 60
        elif type_duration == "h":
            return _duration * 3600
        elif type_duration == "j":
            return _duration * 86400
        else:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - Please provide a valid duration type! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=15,
            )
            return False

    def get_guild_pre(self, arg: Union[Message, Member], *args) -> list:
        try:
            prefix = self.configs[arg.guild.id]["prefix"]
        except Exception:
            prefix = self.bot.configs[arg.guild.id]["prefix"] or "o!"

        return [prefix, prefix.lower(), prefix.upper()]

    async def clear_playlist(self, guild: Guild):
        player = self.bot.lavalink.player_manager.get(guild.id)

        if player:
            # Clear the queue to ensure old tracks don't start playing
            # when someone else queues something.
            player.queue.clear()
            # Stop the current track so Lavalink consumes less resources.
            await player.stop()

            # Disconnect from the voice channel.
            await guild.change_voice_state(channel=None)
            self.bot.playlists[guild.id].clear()

    async def poll_completion(self, *args):
        await self.bot.wait_until_ready()
        guild = args[0]
        poll = args[1]

        if len(args) < 3 or len(args) > 2 and not args[2]:
            timeout = poll["duration_s"] - (time() - poll["created_at_ms"])

            if timeout <= 0:
                timeout = 2

            await sleep(timeout)

        poll = self.bot.poll_repo.get_poll(guild.id, poll["id"])

        if not poll:
            return

        poll_msg = (
            await self.bot.configs[guild.id]["polls_channel"].fetch_message(poll["id"])
        ) or None

        if poll_msg:
            completion_embed = poll_msg.embeds[0]
            maxi = max(poll["choices"].values())
            winners = []

            for key, value in poll["choices"].items():
                if value == maxi:
                    winners.append(key)

            fields = []

            for choice in poll["choices"]:
                fields.append(
                    f"{'❌' if choice not in winners else '✅'} - choice number {choice.split(' ')[0]} - '{' '.join(choice.split(' ')[2::])}' - {poll['choices'][choice]} votes"
                )

            if len(winners) > 1:
                completion_embed.description = "The poll has ended! **Equality!**"
            else:
                completion_embed.description = f"The poll has ended! **The choice number {winners[0].split(' ')[0]} : '{' '.join(winners[0].split(' ')[2::])}' wins!**"

            completion_embed.add_field(
                name="Results:", value="\n".join(fields), inline=False
            )
            await poll_msg.edit(content=None, embed=completion_embed, components=[])

        del self.bot.configs[guild.id]["polls"][poll["id"]]
        self.bot.poll_repo.delete_poll(guild.id, poll["id"])

    @staticmethod
    def to_lower(argument):
        if argument.isdigit():
            raise BadArgument
        if isinstance(argument, str):
            return argument.lower()
        elif isinstance(argument, list):
            return [arg.lower() for arg in argument]

    @staticmethod
    def resolve_guild_path(function):
        def check(self, guild_id: int, *args, **kwargs):
            self.path = f"guilds/{str(guild_id)}/{self.innerpath}"
            return function(self, guild_id, *args, **kwargs)

        return check

    @staticmethod
    def check_bot_starting():
        def predicate(ctx: Context, *args, **kwargs):
            return not ctx.bot.starting

        return check(predicate)

    @staticmethod
    def duration(s: int) -> str:
        seconds = s
        minutes = floor(seconds / 60)
        hours = 0
        days = 0

        if minutes >= 60:
            hours = floor(minutes / 60)
            minutes = minutes - hours * 60

        if hours >= 24:
            days = floor(hours / 24)
            hours = hours - days * 24

        seconds = floor(seconds % 60)
        response = ""
        seperator = ""

        if days > 0:
            plurial = "s" if days > 1 else ""
            response = f"{days} day{plurial}"
            seperator = ", "
            response += f", {hours}h" if hours > 0 else ""
        elif hours > 0:
            response = f"{hours}h"
            seperator = ", "

        if (days > 0 or hours > 0) and minutes > 0:
            response += f", {minutes}m"
        elif minutes > 0:
            response = f"{minutes}m"
            seperator = ", "

        if seconds > 0:
            response += f"{seperator}{seconds}s"

        return response

    @classmethod
    def init_guild(self, bot: Omnitron, guild: Guild):
        """DB USERS"""

        db_users = set(bot.user_repo.get_users(guild.id).keys())
        members = set(
            [m for m in guild.members if not m.bot and str(m.id) not in db_users]
        )
        for member in members:
            bot.user_repo.create_user(guild.id, member.id, f"{member}")

        """ INIT """

        bot.moderators[guild.id] = list(
            [int(k) for k in bot.config_repo.get_moderators(guild.id).keys()]
        )  # Initialize moderators list for every guilds

        """ CONFIG """

        bot.configs[guild.id] = {"prefix": bot.config_repo.get_prefix(guild.id)}

        xp = bot.config_repo.get_xp(guild.id)
        bot.configs[guild.id]["xp"] = dict(xp)

        if "boosteds" in xp:
            bot.configs[guild.id]["xp"]["boosteds"] = {
                key: int(value["bonus"]) for key, value in xp["boosteds"].items()
            }

        if "lvl2role" in xp:
            bot.configs[guild.id]["xp"]["lvl2role"] = {
                int(key): guild.get_role(value["role_id"])
                for key, value in xp["lvl2role"].items()
            }

        if "prestiges" in xp:
            bot.configs[guild.id]["xp"]["prestiges"] = {
                int(key[2]): guild.get_role(value["role_id"])
                for key, value in xp["prestiges"].items()
            }

        if "notify_channel" in xp:
            bot.configs[guild.id]["xp"]["notify_channel"] = guild.get_channel(
                xp["notify_channel"]
            )

        """ MUTE ON JOIN """

        mute_on_join = bot.config_repo.get_mute_on_join(guild.id)
        if mute_on_join:
            bot.configs[guild.id]["mute_on_join"] = {
                "duration": mute_on_join["duration"],
                "muted_role": guild.get_role(int(mute_on_join["muted_role_id"])),
            }
            if "notify_channel_id" in mute_on_join:
                bot.configs[guild.id]["mute_on_join"][
                    "notify_channel"
                ] = guild.get_channel(int(mute_on_join["notify_channel_id"]))

        """ PREVENT INVITES """

        prevent_invites = bot.config_repo.get_invit_prevention(guild.id)
        if prevent_invites:
            bot.configs[guild.id]["prevent_invites"] = (
                {
                    "notify_channel": guild.get_channel(
                        int(prevent_invites["notify_channel_id"])
                    )
                }
                if isinstance(prevent_invites, OrderedDict)
                else None
            )

        """ MUSIC MISC """

        bot.playlists[guild.id] = []

        bot.djs[guild.id] = list(
            [int(k) for k in bot.config_repo.get_djs(guild.id).keys()]
        )  # Initialize moderators list for every guilds

        """ COMMANDS CHANNELS """

        commands_channels = bot.config_repo.get_commands_channels(guild.id)
        if commands_channels:
            bot.configs[guild.id]["commands_channels"] = [
                int(c) for c in commands_channels.keys()
            ]

        """ MUSIC CHANNELS """

        music_channels = bot.config_repo.get_music_channels(guild.id)
        if music_channels:
            bot.configs[guild.id]["music_channels"] = [
                int(c) for c in music_channels.keys()
            ]

        """ XP GAIN """

        xp_gain_channels = bot.config_repo.get_xp_gain_channels(guild.id)
        if xp_gain_channels:
            text_channels = []
            voice_channels = []

            for k, v in xp_gain_channels.items():
                if v["type"] == "TextChannel":
                    text_channels.append(int(k))
                else:
                    voice_channels.append(int(k))

            bot.configs[guild.id]["xp_gain_channels"] = {
                "TextChannel": text_channels,
                "VoiceChannel": voice_channels,
            }

        """ POLLS """

        polls_channel = bot.config_repo.get_polls_channel(guild.id)
        if polls_channel:
            bot.configs[guild.id]["polls_channel"] = guild.get_channel(
                int(polls_channel)
            )

        polls = bot.poll_repo.get_polls(guild.id)
        if len(polls) > 1 and "old" in polls:
            bot.configs[guild.id]["polls"] = {}
            for poll in polls:
                if poll == "old":
                    continue
                bot.configs[guild.id]["polls"][
                    int(poll)
                ] = bot.utils_class.task_launcher(
                    bot.utils_class.poll_completion, (guild, polls[poll]), count=1
                )

        """ TICKETS """

        tickets = bot.config_repo.get_tickets(guild.id)
        if tickets:
            bot.configs[guild.id]["tickets"] = {
                "tickets_channel": guild.get_channel(
                    int(tickets["tickets_channel_id"])
                ),
                "tickets_category": guild.get_channel(
                    int(tickets["tickets_category_id"])
                ),
            }

        """ SELECT TO ROLE """

        select2role = bot.config_repo.get_select2role(guild.id)
        if select2role:
            bot.configs[guild.id]["select2role"] = {}

            if "selects" in select2role:
                bot.configs[guild.id]["select2role"]["selects"] = {
                    key: guild.get_role(value["role_id"])
                    for key, value in select2role["selects"].items()
                }

            if "channel_id" in select2role:
                bot.configs[guild.id]["select2role"]["channel"] = guild.get_channel(
                    int(select2role["channel_id"])
                )

                bot.configs[guild.id]["select2role"]["roles_msg_id"] = select2role[
                    "roles_msg_id"
                ]

        print(bot.configs[guild.id])

    @classmethod
    def check_moderator(self):
        def predicate(ctx: Context, *args, **kwargs):
            ctx.bot.last_check = "moderator"
            return self.is_mod(self, ctx.author, ctx.bot)

        return check(predicate)

    @classmethod
    def check_dj(self):
        def predicate(ctx: Context, *args, **kwargs):
            ctx.bot.last_check = "dj"
            return self.is_dj(self, ctx.author, ctx.bot)

        return check(predicate)
