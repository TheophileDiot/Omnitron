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

        for cmd in ctx.command.commands:
            em.add_field(
                name=f"{cmd.brief} {cmd.name}",
                value=f"{cmd.description}"
                + (
                    f"\n**Alias"
                    + ("es" if len(cmd.aliases) > 1 else "")
                    + "**: "
                    + ", ".join([f"`{a}`" for a in cmd.aliases])
                    if cmd.aliases
                    else ""
                )
                + (f"\n**Usage**: `{cmd.usage}`" if cmd.usage else "")
                + (
                    f"\n**Sub-commands:** {', '.join([f'`{cmd.name}`' for cmd in cmd.commands])}"
                    if "all_commands" in vars(cmd).keys() and cmd.commands
                    else ""
                ),
                inline=True,
            )

        return em

    def duration(self, s: int) -> str:
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
