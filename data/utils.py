from asyncio import sleep
from collections import OrderedDict
from math import floor
from re import compile as re_compile
from time import time
from typing import Union

from discord import Embed, Forbidden, Guild, Message, Member, NotFound
from discord.ext.commands import Context, check
from discord.ext.commands.errors import BadArgument
from discord.ext.tasks import loop

from bot import Omnitron


class Utils:
    def __init__(self, bot: Omnitron) -> None:
        self.bot = bot

    async def check_invite(self, ctx: Context):
        """This method check if the user sent an invitation link to another discord server"""
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

            try:
                await ctx.message.delete()
            except Forbidden:
                await self.send_message_to_mods(
                    f"⚠️ - I don't have the right permissions to manage messages in the channel {ctx.channel.mention} (i tried to delete a message that have an invit to another discord server in it! -> {ctx.message.jump_url})!",
                    ctx.guild.id,
                )

            try:
                await self.bot.configs[ctx.guild.id]["prevent_invites"][
                    "notify_channel"
                ].send(
                    f"⚠️ - The member `{ctx.author}` tried to send an invitation link to another discord server in {ctx.channel.mention}! => {ctx.message.clean_content}"
                )
            except Forbidden:
                await self.send_message_to_mods(
                    f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[ctx.guild.id]['prevent_invites']['notify_channel'].mention} (message: `⚠️ - The member `{ctx.author}` tried to send an invitation link to another discord server in {ctx.channel.mention}! => {ctx.message.clean_content}`)!",
                    ctx.guild.id,
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

                try:
                    await ctx.send(
                        f"⚠️ - {ctx.author.mention} - **You've received a warning because you've sent three consecutive invitation links to other discord servers!**",
                        delete_after=30,
                    )
                except Forbidden as f:
                    f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - **You've received a warning because you've sent three consecutive invitation links to other discord servers!**`)!"
                    raise
            else:
                try:
                    await ctx.send(
                        f"⛔ - {ctx.author.mention} - **Invitation links to other discord servers are not allowed in this server!**, `{'first' if links == 0 else 'second'} warning`!"
                    )
                except Forbidden as f:
                    f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⛔ - {ctx.author.mention} - **Invitation links to other discord servers are not allowed in this server!**, `{'first' if links == 0 else 'second'} warning`!`)!"
                    raise

    async def mute_completion(self, db_user: OrderedDict, guild_id: int):
        """This method manage the mute completion"""
        await self.bot.wait_until_ready()
        mute = db_user["mutes"][-1]

        if (
            mute["reason"] == "joined the server"
            and db_user["id"] in self.bot.tasks[guild_id]["mute_completions"]
        ):
            self.bot.user_repo.clear_join_mutes(guild_id, db_user["id"])
            return

        timeout = mute["duration_s"] - (time() - mute["at_ms"])

        if timeout <= 0:
            timeout = 2

        await sleep(timeout)
        self.bot.user_repo.unmute_user(guild_id, db_user["id"])

        try:
            guild = await self.bot.fetch_guild(guild_id)
            member = await guild.try_member(int(db_user["id"]))
        except NotFound:
            member = db_user["name"]

        if not isinstance(member, str):
            try:
                if "muted_role" in self.bot.configs[guild_id]:
                    await member.remove_roles(self.bot.configs[guild_id]["muted_role"])
            except Forbidden:
                if db_user["id"] in self.bot.tasks[guild_id]["mute_completions"]:
                    del self.bot.tasks[guild_id]["mute_completions"][db_user["id"]]

                return await self.send_message_to_mods(
                    f"⚠️ - I don't have the right permissions to remove the role `@{self.bot.configs[guild_id]['muted_role'].name}` from the member `{member}`!",
                    guild_id,
                )

        if mute["reason"] == "joined the server":
            self.bot.user_repo.clear_join_mutes(guild_id, db_user["id"])

            if "notify_channel" in self.bot.configs[guild_id]["mute_on_join"]:
                try:
                    await self.bot.configs[guild_id]["mute_on_join"][
                        "notify_channel"
                    ].send(
                        f"🔊 - The member `{member}` has just finished being muted after joining the server! (ID: `{db_user['id']}`)"
                    )
                except Forbidden:
                    await self.send_message_to_mods(
                        f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[guild_id]['mute_on_join']['notify_channel'].mention} (message: `🔊 - The member `{member}` has just finished being muted after joining the server! (ID: `{db_user['id']}`)`)!",
                        guild_id,
                    )
        else:
            if "notify_channel" in self.bot.configs[guild_id]["mute_on_join"]:
                try:
                    await self.bot.configs[guild_id]["mute_on_join"][
                        "notify_channel"
                    ].send(f"🔊 - The member `{member}` is no longer muted.")
                except Forbidden:
                    await self.send_message_to_mods(
                        f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[guild_id]['mute_on_join']['notify_channel'].mention} (message: `🔊 - The member `{member}` is no longer muted.`)!",
                        guild_id,
                    )

        if db_user["id"] in self.bot.tasks[guild_id]["mute_completions"]:
            del self.bot.tasks[guild_id]["mute_completions"][db_user["id"]]

    async def send_message_to_mods(self, message: str, guild_id: int):
        """This method send a message to all mods"""
        guild = await self.bot.fetch_guild(guild_id)

        if "mods_channel" in self.bot.configs[guild_id]:
            try:
                return await self.bot.configs[guild_id]["mods_channel"].send(message)
            except Forbidden:
                message += f"\nAnd also in the channel {self.bot.configs[guild_id]['mods_channel'].mention}!"

        message += f"\n\nIn the guild -> `{guild}` (ID: `{guild_id}`)"

        if self.bot.moderators[guild_id]:
            for mod in self.bot.moderators[guild_id]:
                mod = guild.get_role(int(mod))

                if mod:
                    for m in set(mod.members):
                        try:
                            m.send(message)
                        except Forbidden:
                            pass
                else:
                    try:
                        mod = await guild.try_member(int(mod))
                        mod.send(message)
                    except Forbidden or NotFound:
                        pass

        else:
            try:
                guild_owner = guild.owner

                if not guild_owner:
                    guild_owner = await guild.fetch_member(int(guild.owner_id))

                await guild_owner.send(message)
            except Forbidden or NotFound:
                return await (await self.bot.fetch_user(self.bot.owner_id)).send(
                    f"{message}\nAnd couldn't send a message to the owner of the server!"
                )

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
    ) -> bool or int or None:
        type_duration = self.to_lower(type_duration)

        if _duration <= 0:
            try:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 0! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                    delete_after=15,
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 0! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)!"
                raise

            return False
        elif (
            ctx.command.parents[0].name if ctx.command.parents else ""
        ) == "poll" and (
            _duration <= 600
            and type_duration == "s"
            or _duration <= 10
            and type_duration == "m"
        ):
            try:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 10 minutes to create a poll! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                    delete_after=15,
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 10 minutes to create a poll! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)!"
                raise

            return False

        if type_duration == "s":
            return _duration * 1
        elif type_duration == "m":
            return _duration * 60
        elif type_duration == "h":
            return _duration * 3600
        elif type_duration == "d":
            return _duration * 86400
        else:
            try:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please provide a valid duration type! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                    delete_after=15,
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a valid duration type! `{self.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)!"
                raise

            return False

    def get_guild_pre(self, arg: Union[Message, Member, int]) -> list:
        try:
            if isinstance(arg, int):
                prefix = self.configs[arg]["prefix"]
            else:
                prefix = self.configs[arg.guild.id]["prefix"]
        except AttributeError:
            if isinstance(arg, int):
                prefix = self.bot.configs[arg]["prefix"]
            else:
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

        try:
            poll_msg = await self.bot.configs[guild.id]["polls_channel"].fetch_message(
                poll["id"]
            )
        except NotFound:
            poll_msg = None

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
        def check_guild_path(self, guild_id: int, *args, **kwargs):
            self.path = f"guilds/{str(guild_id)}/{self.innerpath}"
            return function(self, guild_id, *args, **kwargs)

        return check_guild_path

    @staticmethod
    def check_bot_starting():
        def predicate(ctx: Context):
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
        separator = ""

        if days > 0:
            plural = "s" if days > 1 else ""
            response = f"{days} day{plural}"
            separator = ", "
            response += f", {hours}h" if hours > 0 else ""
        elif hours > 0:
            response = f"{hours}h"
            separator = ", "

        if (days > 0 or hours > 0) and minutes > 0:
            response += f", {minutes}m"
        elif minutes > 0:
            response = f"{minutes}m"
            separator = ", "

        if seconds > 0:
            response += f"{separator}{seconds}s"

        return response

    def init_guild(self, guild: Guild):
        """DB USERS"""
        bot = self.bot

        db_users = bot.user_repo.get_users(guild.id)
        members = set(
            [
                m
                for m in guild.members
                if not m.bot and str(m.id) not in set(db_users.keys())
            ]
        )
        for member in members:
            bot.user_repo.create_user(guild.id, member.id, f"{member}")

        """ INIT """

        bot.moderators[guild.id] = list(
            [int(k) for k in bot.config_repo.get_moderators(guild.id).keys()]
        )  # Initialize moderators list for every guilds

        bot.tasks[guild.id] = {"mute_completions": {}}

        for db_user in db_users.values():
            if db_user["muted"]:
                if "mutes" in db_user:
                    self.task_launcher(
                        self.mute_completion,
                        (
                            db_user,
                            guild.id,
                        ),
                        count=1,
                    )
                else:
                    bot.user_repo.unmute_user(guild.id, db_user["id"])

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
            }
            if "notify_channel_id" in mute_on_join:
                bot.configs[guild.id]["mute_on_join"][
                    "notify_channel"
                ] = guild.get_channel(int(mute_on_join["notify_channel_id"]))

        """ PREVENT INVITES """

        prevent_invites = bot.config_repo.get_invite_prevention(guild.id)
        if prevent_invites:
            bot.configs[guild.id]["prevent_invites"] = {"is_on": True}

            if "notify_channel_id" in prevent_invites:
                bot.configs[guild.id]["prevent_invites"][
                    "notify_channel"
                ] = guild.get_channel(int(prevent_invites["notify_channel_id"]))

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
            bot.configs[guild.id]["xp_gain_channels"] = {}
            text_channels = []
            voice_channels = []

            for k, v in xp_gain_channels.items():
                if v["type"] == "TextChannel":
                    text_channels.append(int(k))
                else:
                    voice_channels.append(int(k))

            if text_channels:
                bot.configs[guild.id]["xp_gain_channels"]["TextChannel"] = text_channels

            if voice_channels:
                bot.configs[guild.id]["xp_gain_channels"][
                    "VoiceChannel"
                ] = voice_channels

        """ POLLS """

        polls_channel = bot.config_repo.get_polls_channel(guild.id)
        if polls_channel:
            bot.configs[guild.id]["polls_channel"] = guild.get_channel(
                int(polls_channel)
            )

        polls = bot.poll_repo.get_polls(guild.id)
        if len(polls) > 1 or polls and "old" not in polls:
            bot.configs[guild.id]["polls"] = {}
            for poll in polls:
                if poll == "old":
                    continue
                bot.configs[guild.id]["polls"][int(poll)] = self.task_launcher(
                    self.poll_completion, (guild, polls[poll]), count=1
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

        """ MUTED ROLE """

        muted_role = bot.config_repo.get_muted_role(guild.id)
        if muted_role:
            bot.configs[guild.id]["muted_role"] = guild.get_role(int(muted_role))

        """ MODS CHANNEL """

        mods_channel = bot.config_repo.get_mods_channel(guild.id)
        if mods_channel:
            bot.configs[guild.id]["mods_channel"] = guild.get_channel(int(mods_channel))

    @classmethod
    def check_moderator(cls):
        def predicate(ctx: Context):
            ctx.bot.last_check = "moderator"
            return cls.is_mod(ctx.author, ctx.bot)

        return check(predicate)

    @classmethod
    def check_dj(cls):
        def predicate(ctx: Context):
            ctx.bot.last_check = "dj"
            return cls.is_dj(ctx.author, ctx.bot)

        return check(predicate)

    # The `args` are the arguments passed into the loop
    @staticmethod
    def task_launcher(function, param, **interval) -> loop:
        """Creates new instances of `tasks.Loop`"""
        # Creating the task
        # You can also pass a static interval and/or count
        new_task = loop(**interval)(function)
        # Starting the task
        new_task.start(*param)
        return new_task

    @staticmethod
    def is_mod(member: Member, bot: Omnitron) -> bool:
        return (
            set(member.roles) & set(bot.moderators[member.guild.id])
            or member.id in set(bot.moderators[member.guild.id])
            or member.guild_permissions.administrator
        )

    @staticmethod
    def is_dj(member: Member, bot: Omnitron) -> bool:
        return (
            not bot.djs[member.guild.id]
            or set(member.roles) & set(bot.djs[member.guild.id])
            or member.id in set(bot.djs[member.guild.id])
            or member.guild_permissions.administrator
        )
