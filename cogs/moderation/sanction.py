from math import ceil
from time import time
from typing import Union

from disnake import (
    ApplicationCommandInteraction,
    Embed,
    Forbidden,
    Member,
    User,
)
from disnake.ext.commands import (
    bot_has_permissions,
    bot_has_guild_permissions,
    BucketType,
    Cog,
    Context,
    group,
    guild_only,
    has_guild_permissions,
    max_concurrency,
    slash_command,
)

from bot import Omnitron
from data import DurationType, Utils


class Moderation(Cog, name="moderation.sanction"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ MAIN GROUP """

    @group(
        pass_context=True,
        name="sanction",
        aliases=["sanctions", "strike", "strikes"],
        usage="(sub-command)",
        description="This command manage the server's sanctions",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def sanction_group(self, ctx: Context):
        """
        This command group manages the server's sanctions

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's sanction feature"
                )
            )

    @slash_command(
        name="sanction",
        description="This command manage the server's sanctions",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def sanction_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's polls

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    """ MAIN GROUP'S GROUP(S) """

    @sanction_group.group(
        pass_context=True,
        name="warn",
        aliases=["warns"],
        brief="⚠️",
        usage="(sub-command)",
        description="Manages the server's warns",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_warn_group(self, ctx: Context):
        """
        This command group manages the server's warns

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's warns feature"
                )
            )

    @sanction_slash_group.sub_command_group(
        name="warn",
        description="Manages the server's warns",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_warn_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's warns

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @sanction_group.group(
        pass_context=True,
        name="mute",
        aliases=["mutes"],
        brief="🔕️",
        usage="(sub-command)",
        description="Manages the server's mutes",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_mute_group(self, ctx: Context):
        """
        This command group manages the server's mutes

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's mute feature"
                )
            )

    @sanction_slash_group.sub_command_group(
        name="mute",
        description="Manages the server's mutes",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_mute_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's mutes

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @sanction_group.group(
        pass_context=True,
        name="ban",
        aliases=["bans"],
        brief="🔨",
        usage="(sub-command)",
        description="Manages the server's bans",
    )
    async def sanction_ban_group(self, ctx: Context):
        """
        This command group manages the server's bans

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's sanction ban feature"
                )
            )

    @sanction_slash_group.sub_command_group(
        name="ban",
        description="Manages the server's bans",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_ban_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's bans

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    """ MAIN GROUP'S COMMAND(S) """

    """ KICK """

    @sanction_group.command(
        name="kick",
        brief="⚡",
        usage='@member ("reason")',
        description="Kicks a member from the server with a reason attached if specified",
    )
    @has_guild_permissions(kick_members=True)
    @bot_has_guild_permissions(kick_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_kick_command(
        self, ctx: Context, member: Member, *, reason: str = None
    ):
        """
        This command kicks a member from the server with a reason attached if specified

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to kick
        reason: :class:`str` optional
            The reason attached to the kick
        """
        await self.handle_kick(ctx, member, reason)

    @sanction_slash_group.sub_command(
        name="kick",
        description="Kick a member from the server with a reason attached if specified",
    )
    @has_guild_permissions(kick_members=True)
    @bot_has_guild_permissions(kick_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_kick_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member, reason: str = None
    ):
        """
        This command kicks a member from the server with a reason attached if specified

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to kick
        reason: :class:`str` optional
            The reason attached to the kick
        """
        await self.handle_kick(inter, member, reason)

    async def handle_kick(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
        reason: str = None,
    ):
        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Kick",
            description=f"The member {member} has been kicked by {source.author.mention}",
        )

        em = self.configure_embed(source, em)

        if reason:
            em.add_field(name="raison:", value=reason, inline=False)

        try:
            await member.kick(
                reason=f"The member {member} has been kicked by {source.author} {f'for the reason: {reason}' if reason else ''}"
            )
        except Forbidden:
            if isinstance(source, Context):
                return await source.reply(
                    f"⛔ - {source.author.mention} - I can't kick the member `{member}`!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⛔ - {source.author.mention} - I can't kick the member `{member}`!",
                    ephemeral=True,
                )

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ MAIN GROUP'S WARN COMMAND(S) """

    """ WARN ADD """

    @sanction_warn_group.command(
        name="add",
        brief="⚠️",
        usage='@member ("reason")',
        description="Warns a member with a reason attached if specified",
    )
    @max_concurrency(1, per=BucketType.member)
    async def sanction_warn_add_command(
        self, ctx: Context, member: Member, *, reason: str = None
    ):
        """
        This command warns a member with a reason attached if specified

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to warn
        reason: :class:`str` optional
            The reason attached to the warn
        """
        await self.handle_warn_add(ctx, member, reason)

    @sanction_warn_slash_group.sub_command(
        name="add",
        description="Warns a member with a reason attached if specified",
    )
    @max_concurrency(1, per=BucketType.member)
    async def sanction_warn_add_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member, reason: str = None
    ):
        """
        This slash command warns a member with a reason attached if specified

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to warn
        reason: :class:`str` optional
            The reason attached to the warn
        """
        await self.handle_warn_add(inter, member, reason)

    async def handle_warn_add(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
        reason: str = None,
    ):
        if "muted_role" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}config muted_role` to set one!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.author)[0]}config muted_role` to set one!",
                    ephemeral=True,
                )

        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Warn",
            description=f"The user `{member}` has been warned by {source.author.mention}",
        )

        em = self.configure_embed(source, em)

        if reason:
            em.add_field(name="reason:", value=reason, inline=False)

        self.bot.user_repo.warn_user(
            source.guild.id, member.id, time(), f"{source.author}", reason
        )
        warns = len(self.bot.user_repo.get_warns(source.guild.id, member.id))
        em.add_field(
            name=f"**Number of warnings of {member}:**",
            value=f"{warns}",
            inline=False,
        )

        if warns == 2 or warns == 4:
            if source.channel.permissions_for(source.guild.me).manage_roles:
                em.add_field(
                    name="sanction",
                    value=f"🔇 - Muted {'3H' if warns == 2 else '24H'} - 🔇",
                    inline=False,
                )

                try:
                    await member.add_roles(
                        self.bot.configs[source.guild.id]["muted_role"]
                    )
                except Forbidden as f:
                    f.text = f"⚠️ - I don't have the right permissions to add the role `{self.bot.configs[source.guild.id]['muted_role']}` to {member}! (maybe the role is above mine)"
                    raise

                self.bot.user_repo.mute_user(
                    source.guild.id,
                    member.id,
                    10800 if warns == 2 else 86400,
                    time(),
                    f"{self.bot.user}",
                    f"{'2nd' if warns == 2 else '4th'} warn",
                )
                self.bot.tasks[source.guild.id]["mute_completions"][
                    member.id
                ] = self.bot.utils_class.task_launcher(
                    self.bot.utils_class.mute_completion,
                    (
                        self.bot.user_repo.get_user(member.guild.id, member.id),
                        member.guild.id,
                    ),
                    count=1,
                )
            else:
                await self.bot.utils_class.send_message_to_mods(
                    f"⚠️ - I don't have the right permissions to manage roles in this server (i tried to add the muted role to {member} after his {'2nd' if warns == 2 else '4th'} warn)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                    source.guild.id,
                )
        elif warns == 5:
            em.add_field(name="sanction", value="⚠️ - Warning - ⚠", inline=False)

            try:
                await member.send(
                    f"⚠ - ️️{member.mention} You are on your 5th warn! The next time you're warn, you will be kicked from this server {source.guild}! - ⚠️"
                )
            except Forbidden:
                if isinstance(source, Context):
                    await source.send(
                        f"❌ - ️️{source.author.mention} - Couldn't send the message to {member}, please inform him that on the next warn he will be kicked from the server!"
                    )
                else:
                    await source.response.send_message(
                        f"❌ - ️️{source.author.mention} - Couldn't send the message to {member}, please inform him that on the next warn he will be kicked from the server!"
                    )
        elif warns > 5:
            em.add_field(name="sanction", value="🚫 - kick - 🚫", inline=False)

            try:
                await member.kick(reason="6th warn")
            except Forbidden:
                if isinstance(source, Context):
                    await source.send(
                        f"❌ - {source.author.mention} - I don't have the permission to kick members (or I couldn't kick him myself)! (try kicking him yourself then!)"
                    )
                else:
                    await source.response.send_message(
                        f"❌ - {source.author.mention} - I don't have the permission to kick members (or I couldn't kick him myself)! (try kicking him yourself then!)"
                    )

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ WARN LIST """

    @sanction_warn_group.command(
        name="list",
        brief="ℹ️",
        usage="(@member)",
        description="Shows the list of a member's warns or yours!",
    )
    async def sanction_warn_list_command(self, ctx: Context, member: Member = None):
        """
        This command shows the list of a member's warns or yours!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to list warns
        """
        await self.handle_warn_list(ctx, member)

    @sanction_warn_slash_group.sub_command(
        name="list",
        description="Shows the list of a member's warns or yours!",
    )
    async def sanction_warn_list_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member = None
    ):
        """
        This slash command shows the list of a member's warns or yours!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to list warns
        """
        await self.handle_warn_list(inter, member)

    async def handle_warn_list(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
    ):
        if not member:
            member = source.author

        em = Embed(
            colour=self.bot.color, title=f"⚠️ - list of previous warns from {member}"
        )

        em = self.configure_embed(source, em)

        warns = self.bot.user_repo.get_warns(source.guild.id, member.id)

        if not warns:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been warned.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been warned.",
                    ephemeral=True,
                )

        x = 0
        nl = "\n"
        while x < len(warns) and x <= 24:
            if x == 24:
                em.add_field(
                    name="**Too many warns to display them all**",
                    value="...",
                    inline=False,
                )
            else:
                em.add_field(
                    name=f"**{x + 1}:**",
                    value=f"**date :** {warns[x]['at']}{nl}**by :** {warns[x]['by']}{nl}**reason :** {warns[x]['reason'] if 'reason' in warns[x] else 'no reason specified'}",
                    inline=True,
                )
            x += 1

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ WARN CLEAR """

    @sanction_warn_group.command(
        name="clear",
        brief="🧹",
        usage="(@member)",
        description="Clears the warns of a member!",
    )
    async def sanction_warn_clear_command(self, ctx: Context, member: Member):
        """
        This command clears the warns of a member!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to clear warns
        """
        await self.handle_warn_clear(ctx, member)

    @sanction_warn_slash_group.sub_command(
        name="clear",
        description="Clears the warns of a member!",
    )
    async def sanction_warn_clear_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member
    ):
        """
        This slash command clears the warns of a member!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to clear warns
        """
        await self.handle_warn_clear(inter, member)

    async def handle_warn_clear(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
    ):
        warns = self.bot.user_repo.get_warns(source.guild.id, member.id)

        if not warns:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been warned.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been warned.",
                    ephemeral=True,
                )

        self.bot.user_repo.clear_warns(source.guild.id, member.id)

        if isinstance(source, Context):
            await source.send(f"ℹ️ - `{member}`'s warns have been cleared!")
        else:
            await source.response.send_message(
                f"ℹ️ - `{member}`'s warns have been cleared!"
            )

    """ MAIN GROUP'S MUTE COMMAND(S) """

    """ MUTE ADD """

    @sanction_mute_group.command(
        name="add",
        brief="🔇",
        usage='@member ("reason") (<duration_value> <duration_type>)',
        description="Mutes a member for a certain duration with a reason attached if specified! (default/minimum duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
    )
    @bot_has_permissions(manage_roles=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_mute_add_command(self, ctx: Context, member: Member, *args: str):
        """
        This command mutes a member for a certain duration with a reason attached if specified! (default/minimum duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to mute
        args: :class:`str` optional
            The other options including a reason if there is one and a duration
        """
        reason = None
        _duration = "10"
        type_duration = "m"

        if args and not "".join(args[0][:-1]).isdigit():
            reason = args[0]

        if reason:
            if len(args) > 2:
                _duration, type_duration = (*args[1::],)
            elif len(args) > 1:
                _duration = args[1][0:-1]
                type_duration = args[1][-1]
        elif args:
            if len(args) > 1:
                _duration, type_duration = (*args[0::],)
            else:
                _duration = args[0][0:-1]
                type_duration = args[0][-1]

        if not _duration.isdigit():
            try:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                    delete_after=15,
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)! Required perms: `{', '.join(['SEND_MESSAGES'])}`"
                raise
            return

        await self.handle_mute_add(ctx, member, reason, _duration, type_duration)

    @sanction_mute_slash_group.sub_command(
        name="add",
        description="Mutes a member for a certain duration with a reason attached if specified!",
    )
    @bot_has_permissions(manage_roles=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_mute_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member,
        reason: str = None,
        duration: int = 10,
        type_duration: DurationType = "m",
    ):
        """
        This slash command mutes a member for a certain duration with a reason attached if specified!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to mute
        reason: :class:`str` optional
            The reason attached to the mute
        duration: :class:`int` optional
            The mute's duration value (defaults to 10)
        type_duration: :class:`Utils.DurationType` optional
            the mute's duration type (defaults to "m")
        """
        await self.handle_mute_add(inter, member, reason, duration, type_duration)

    async def handle_mute_add(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
        reason: str,
        duration: int,
        type_duration: str,
    ):
        if "muted_role" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}config muted_role` to set one!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.author)[0]}config muted_role` to set one!",
                    ephemeral=True,
                )

        duration_s = await self.bot.utils_class.parse_duration(
            int(duration), type_duration, source
        )
        if not duration_s:
            return

        em = Embed(
            colour=self.bot.color,
            title=f"🔇 - Mute",
            description=f"The member `{member}` has been muted by {source.author.mention}",
        )

        em = self.configure_embed(source, em)

        if reason:
            em.add_field(name="reason:", value=reason, inline=False)

        db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

        if (
            self.bot.configs[source.guild.id]["muted_role"] not in member.roles
            or not db_user["muted"]
        ):
            em.description = f"The member `{member}` has been muted by {source.author.mention} for {self.bot.utils_class.duration(duration_s)}"
            await member.add_roles(
                self.bot.configs[source.guild.id]["muted_role"],
                reason="Muted from command sanction.",
            )
            self.bot.user_repo.mute_user(
                source.guild.id,
                member.id,
                duration_s,
                time(),
                f"{source.author}",
                reason,
            )
            self.bot.tasks[source.guild.id]["mute_completions"][
                member.id
            ] = self.bot.utils_class.task_launcher(
                self.bot.utils_class.mute_completion,
                (
                    self.bot.user_repo.get_user(source.guild.id, member.id),
                    source.guild.id,
                ),
                count=1,
            )
        else:
            last_mute = self.bot.user_repo.get_last_mute(source.guild.id, member.id)
            em.description = f"The member {member} is already muted"

            em.remove_field(0)

            em.add_field(name="**muted by:**", value=last_mute["by"], inline=True)
            em.add_field(name="**date:**", value=last_mute["at"], inline=True)
            em.add_field(name="**duration:**", value=last_mute["duration"], inline=True)
            em.add_field(
                name="**time remaining:**",
                value=self.bot.utils_class.duration(
                    last_mute["duration_s"] - (time() - last_mute["at_s"])
                ),
                inline=True,
            )

            if "reason" in last_mute:
                em.add_field(name="**reason:**", value=last_mute["reason"], inline=True)

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ MUTE LIST """

    @sanction_mute_group.command(
        name="list",
        brief="ℹ",
        usage="(@member)",
        description="Shows the list of a member's mutes or yours!",
    )
    async def sanction_mute_list_command(
        self,
        ctx: Context,
        member: Member = None,
    ):
        """
        This command shows the list of a member's mutes or yours!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to list the mutes
        """
        await self.handle_mute_list(ctx, member)

    @sanction_mute_slash_group.sub_command(
        name="list",
        description="Shows the list of a member's mutes or yours!",
    )
    async def sanction_mute_list_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
    ):
        """
        This slash command shows the list of a member's mutes or yours!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to list the mutes
        """
        await self.handle_mute_list(inter, member)

    async def handle_mute_list(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
    ):
        if not member:
            member = source.author

        em = Embed(
            colour=self.bot.color,
            title=f"🔇 - List of previous mutes of {member}",
        )

        em = self.configure_embed(source, em)

        db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

        if "mutes" not in db_user or len(db_user["mutes"]) < 1:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been muted."
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - {f'The member {member}' if member != source.author else 'You'} has never been muted."
                )

        x = 0
        nl = "\n"
        while x < len(db_user["mutes"]) and x <= 24:
            if x == 24:
                em.add_field(
                    name="**Too many mutes to display them all**.",
                    value="...",
                    inline=False,
                )
            else:
                em.add_field(
                    name=f"**{x + 1}:**",
                    value=f"**date :** {db_user['mutes'][x]['at']}{nl}**by :** {db_user['mutes'][x]['by']}{nl}**duration :** {db_user['mutes'][x]['duration']}{nl}**reason :** {db_user['mutes'][x]['reason'] if 'reason' in db_user['mutes'][x] else 'no reason specified'}",
                    inline=True,
                )
            x += 1

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ MUTE REMOVE """

    @sanction_mute_group.command(
        name="remove",
        brief="🔉",
        usage='@member ("reason")',
        description="Unmute a member with a reason attached if specified!",
    )
    @bot_has_permissions(manage_roles=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_mute_remove_command(
        self,
        ctx: Context,
        member: Member,
        *,
        reason: str = None,
    ):
        """
        This command unmute a member with a reason attached if specified!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to unmute
        reason: :class:`str` optional
            The reason attached to the unmute
        """
        await self.handle_mute_remove(ctx, member, reason)

    @sanction_mute_slash_group.sub_command(
        name="remove",
        description="Unmute a member with a reason attached if specified!",
    )
    @bot_has_permissions(manage_roles=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_mute_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member,
        *,
        reason: str = None,
    ):
        """
        This slash command unmute a member with a reason attached if specified!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to unmute
        reason: :class:`str` optional
            The reason attached to the unmute
        """
        await self.handle_mute_remove(inter, member, reason)

    async def handle_mute_remove(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
        reason: str = None,
    ):
        db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

        if (
            self.bot.configs[source.guild.id]["muted_role"] in member.roles
            or db_user["muted"]
        ):
            await member.remove_roles(
                self.bot.configs[source.guild.id]["muted_role"], reason=reason
            )
            self.bot.user_repo.unmute_user(source.guild.id, member.id)

            if (
                "reason" in db_user["mutes"][-1]
                and db_user["mutes"][-1]["reason"] != "joined the server"
            ):
                self.bot.tasks[source.guild.id]["mute_completions"][member.id].cancel()
                del self.bot.tasks[source.guild.id]["mute_completions"][member.id]

            resp = (
                f"🔊 - The member {member} has been unmuted by {source.author.mention}."
            )
        else:
            resp = f"🔊 - {source.author.mention} - The member {member} is not or no longer muted."

        if isinstance(source, Context):
            await source.send(resp)
        else:
            await source.response.send_message(resp)

    """ MAIN GROUP'S BAN COMMAND(S) """

    """ ADD """

    @sanction_ban_group.command(
        name="add",
        brief="🚷",
        usage='@member ("reason") (<duration_value> <duration_type>)',
        description="Bans a member for a certain duration with a reason attached if specified! (minimum duration = 1 day) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_add_command(self, ctx: Context, member: Member, *args: str):
        """
        This command bans a member for a certain duration with a reason attached if specified! (minimum duration = 1 day) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to ban
        args: :class:`str` optional
            The other options including a reason if there is one and a duration
        """
        reason = None
        _duration = None
        type_duration = None

        if args and not "".join(args[0][:-1]).isdigit():
            reason = args[0]

        if reason:
            if len(args) > 2:
                _duration, type_duration = (*args[1::],)
            elif len(args) > 1:
                _duration = args[1][0:-1]
                type_duration = args[1][-1]
        elif args:
            if len(args) > 1:
                _duration, type_duration = (*args[0::],)
            else:
                _duration = args[0][0:-1]
                type_duration = args[0][-1]

        if _duration and not _duration.isdigit():
            try:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                    delete_after=15,
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)! Required perms: `{', '.join(['SEND_MESSAGES'])}`"
                raise
            return

        await self.handle_ban_add(ctx, member, reason, _duration, type_duration)

    @sanction_ban_slash_group.sub_command(
        name="add",
        description="Bans a member for a certain duration with a reason attached if specified!",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member,
        reason: str = None,
        duration: int = 1,
        type_duration: DurationType = "d",
    ):
        """
        This slash command bans a member for a certain duration with a reason attached if specified!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to ban
        reason: :class:`str` optional
            The reason attached to the ban
        duration: :class:`int` optional
            The ban's duration value (defaults to 1)
        type_duration: :class:`Utils.DurationType` optional
            the ban's duration type (defaults to "d")
        """
        await self.handle_ban_add(inter, member, reason, duration, type_duration)

    async def handle_ban_add(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member,
        reason: str = None,
        duration: int = None,
        type_duration: str = None,
    ):
        duration_s = None

        if duration:
            duration_s = await self.bot.utils_class.parse_duration(
                int(duration), type_duration, source
            )
            if not duration_s:
                return

        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Ban",
            description=f"The member {member} has been banned by {source.author.mention}",
        )

        em = self.configure_embed(source, em)

        if reason:
            em.add_field(name="raison:", value=reason, inline=False)

        try:
            await member.ban(
                reason=f"The member {member} has been banned by {source.author}"
                + (
                    f" for {self.bot.utils_class.duration(duration_s)}"
                    if duration_s
                    else ""
                )
                + (f" for the reason: {reason}'" if reason else "")
            )
            self.bot.user_repo.ban_user(
                source.guild.id,
                member.id,
                duration_s,
                time(),
                f"{source.author}",
                reason,
            )

            if duration_s:
                em.description += f" for {self.bot.utils_class.duration(duration_s)}"
                self.bot.utils_class.task_launcher(
                    self.bot.utils_class.ban_completion,
                    (
                        self.bot.user_repo.get_user(source.guild.id, member.id),
                        source.guild.id,
                    ),
                    count=1,
                )
        except Forbidden:
            if isinstance(source, Context):
                return await source.reply(
                    f"⛔ - {source.author.mention} - I can't ban the member `{member}`!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⛔ - {source.author.mention} - I can't ban the member `{member}`!",
                    ephemeral=True,
                )
        except AttributeError:
            if isinstance(source, Context):
                return await source.reply(
                    f"⛔ - {source.author.mention} - I can't ban the member `{member}` because he is not present in the guild!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⛔ - {source.author.mention} - I can't ban the member `{member}` because he is not present in the guild!",
                    ephemeral=True,
                )

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)

    """ REMOVE """

    @sanction_ban_group.command(
        name="remove",
        brief="❤️‍🩹",
        usage='@user ("reason")',
        description="Unban a user from the server with a reason attached if specified!",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_remove_command(
        self, ctx: Context, user: User, *, reason: str = None
    ):
        """
        This command unban a user from the server with a reason attached if specified!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        user: :class:`disnake.User`
            The user you want to ban
        reason: :class:`str` optional
            The reason attached to the unban
        """
        await self.handle_ban_remove(ctx, user, reason)

    @sanction_ban_slash_group.sub_command(
        name="remove",
        description="Unban a user from the server with a reason attached if specified!",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_remove_slash_command(
        self, inter: ApplicationCommandInteraction, user: User, reason: str = None
    ):
        """
        This slash command unban a user from the server with a reason attached if specified!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        user: :class:`disnake.User`
            The user you want to ban
        reason: :class:`str` optional
            The reason attached to the unban
        """
        await self.handle_ban_remove(inter, user, reason)

    async def handle_ban_remove(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        user: User,
        reason: str = None,
    ):
        bans = await source.guild.bans()

        if not bans:
            if isinstance(source, Context):
                return await source.send(
                    f"ℹ - {source.author.mention} - There is no ban in this server!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ - {source.author.mention} - There is no ban in this server!",
                    ephemeral=True,
                )

        banned = False
        for ban in bans:
            if ban.user.id == user.id:
                banned = True

        if not banned:
            if isinstance(source, Context):
                return await source.send(
                    f"ℹ - {source.author.mention} - The user `{user}` is not banned from the server!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ - {source.author.mention} - The user `{user}` is not banned from the server!",
                    ephemeral=True,
                )

        self.bot.user_repo.unban_user(
            source.guild.id, user.id, time(), f"{source.author}", reason
        )
        await source.guild.unban(user, reason=reason)

        if isinstance(source, Context):
            await source.send(
                f"🚫 - The user `{user}` is no longer banned from the server.",
            )
        else:
            await source.response.send_message(
                f"🚫 - The user `{user}` is no longer banned from the server.",
            )

        if user.id in self.bot.tasks[source.guild.id]["ban_completions"]:
            del self.bot.tasks[source.guild.id]["ban_completions"][user.id]

    """ LIST """

    @sanction_ban_group.command(
        name="list",
        brief="🙅🏽‍♂️",
        usage="(@member)",
        description="Lists the server's bans or for a specific member!",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_list_command(self, ctx: Context, member: Member = None):
        """
        This command lists the bans from the server or for a specific member!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member you want to list bans
        """
        await self.handle_ban_list(ctx, member)

    @sanction_ban_slash_group.sub_command(
        name="list",
        description="Lists the server's bans or for a specific member!",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_list_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member = None
    ):
        """
        This slash command lists the bans from the server or for a specific member!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member you want to list bans
        """
        await self.handle_ban_list(inter, member)

    async def handle_ban_list(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
    ):
        if member:
            db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

            if "unban" not in db_user:
                if isinstance(source, Context):
                    return await source.send(
                        f"ℹ - {source.author.mention} - {member} has never been ban from the server!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ - {source.author.mention} - {member} has never been ban from the server!",
                        ephemeral=True,
                    )

            em = Embed(
                colour=self.bot.color,
                title=f"🔨 - {member}'s bans",
                description=f"The list of {member}'s old bans",
            )
            em = self.configure_embed(source, em, member)
            bans = db_user["unban"]
            x = 0

            while x < len(bans) and x <= 24:
                if x == 24:
                    em.add_field(
                        name="**Too many bans to display them all**",
                        value="...",
                        inline=False,
                    )
                else:
                    ban = bans[list(bans.keys())[x]]
                    em.add_field(
                        name=f"ban `{ceil(ban['original_ban']['at_s'] * 1000)}`:",
                        value=f"**date**: {ban['original_ban']['at']}\n**by**: `{ban['original_ban']['by']}`\n**duration**: {ban['original_ban']['duration']}"
                        + (
                            f"\n**reason**: {ban['original_ban']['reason']}"
                            if "reason" in ban["original_ban"]
                            else ""
                        )
                        + f"\n\n**unbanned date**: {ban['at']}\n**by**: `{ban['by']}"
                        + (f"\n**reason**: {ban['reason']}" if "reason" in ban else ""),
                        inline=True,
                    )
                x += 1

            if isinstance(source, Context):
                await source.send(embed=em)
            else:
                await source.response.send_message(embed=em)
        else:
            bans = await source.guild.bans()

            if not bans:
                if isinstance(source, Context):
                    return await source.send(
                        f"ℹ - {source.author.mention} - There is no ban in this server!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ - {source.author.mention} - There is no ban in this server!",
                        ephemeral=True,
                    )

            em = Embed(
                colour=self.bot.color,
                title=f"🔨 - Server's bans",
                description=f"The list of the server bans",
            )
            em = self.configure_embed(source, em)
            x = 0

            while x < len(bans) and x <= 24:
                if x == 24:
                    em.add_field(
                        name="**Too many bans to display them all**",
                        value="...",
                        inline=False,
                    )
                else:
                    ban = bans[x]
                    db_user = self.bot.user_repo.get_user(source.guild.id, ban.user.id)
                    em.add_field(
                        name=f"{ban.user}",
                        value=f"**date**: {db_user['ban']['at']}\n**by**: `{db_user['ban']['by']}`\n**duration**: {db_user['ban']['duration']}"
                        + (
                            f"\n**reason**: {db_user['ban']['reason']}"
                            if "reason" in db_user["ban"]
                            else ""
                        ),
                        inline=True,
                    )
                x += 1

            if isinstance(source, Context):
                await source.send(embed=em)
            else:
                await source.response.send_message(embed=em)

    """ METHODS """

    def configure_embed(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        em: Embed,
        member: Member = None,
    ) -> Embed:
        if not member:
            member = source.author

        if source.guild.icon:
            em.set_thumbnail(url=source.guild.icon.url)

        if member.avatar:
            em.set_author(
                name=f"{member}",
                icon_url=member.avatar.url,
            )
        else:
            em.set_author(
                name=f"{member}",
            )

        if self.bot.user.avatar:
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            em.set_footer(text=self.bot.user.name)

        return em


def setup(bot):
    bot.add_cog(Moderation(bot))
