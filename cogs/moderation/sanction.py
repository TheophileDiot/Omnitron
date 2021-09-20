from disnake import Embed, Forbidden, Member, Permissions
from disnake.ext.commands import (
    bot_has_permissions,
    bot_has_guild_permissions,
    BucketType,
    Cog,
    Context,
    group,
    has_guild_permissions,
    max_concurrency,
)
from time import time

from bot import Omnitron
from data import Utils


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
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's sanction feature"
                )
            )

    """ MAIN GROUP'S GROUP(S) """

    @sanction_group.group(
        pass_context=True,
        name="warn",
        aliases=["warns"],
        brief="⚠️",
        usage="(sub-command)",
        description="This option manage the server's warns",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_warn_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's warns feature"
                )
            )

    @sanction_group.group(
        pass_context=True,
        name="mute",
        aliases=["mutes"],
        brief="🔕️",
        usage="(sub-command)",
        description="This option manage the server's mutes",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def sanction_mute_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's mute feature"
                )
            )

    """ MAIN GROUP'S COMMAND(S) """

    @sanction_group.group(
        pass_context=True,
        name="kick",
        brief="⚡",
        usage='@member ("reason")',
        description="Kick a member from the server with a reason attached if specified",
    )
    @has_guild_permissions(kick_members=True)
    @bot_has_guild_permissions(kick_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_kick_command(
        self, ctx: Context, member: Member, *, reason: str = None
    ):
        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Kick",
            description=f"The member {member} has been kicked by {ctx.author.mention}",
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        if reason:
            em.add_field(name="raison:", value=reason, inline=False)

        try:
            await member.kick(
                reason=f"The member {member} has been kicked by {ctx.author} {f'for the reason: {reason}' if reason else ''}"
            )
        except Forbidden:
            return await ctx.reply(
                f"⛔ - {ctx.author.mention} - I can't kick the member `{member}`!",
                delete_after=20,
            )

        await ctx.send(embed=em)

    @sanction_group.group(
        pass_context=True,
        name="ban",
        brief="🔨",
        usage='@member ("reason") (<duration_value> <duration_type>)',
        description="Ban a member for a certain duration with a reason attached if specified! (default/minimum duration = 1 day) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
    )
    @has_guild_permissions(ban_members=True)
    @bot_has_guild_permissions(ban_members=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_ban_command(self, ctx: Context, member: Member, *args: str):
        reason = None
        _duration = "1"
        type_duration = "d"

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
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)! Required perms: `{', '.join([Permissions.send_messages])}`"
                raise
            return

        duration_s = await self.bot.utils_class.parse_duration(
            int(_duration), type_duration, ctx
        )
        if not duration_s:
            return

        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Ban",
            description=f"The member {member} has been banned by {ctx.author.mention}",
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        if reason:
            em.add_field(name="raison:", value=reason, inline=False)

        try:
            await member.ban(
                reason=f"The member {member} has been banned by {ctx.author}"
                + (
                    f" for {self.bot.utils_class.duration(duration_s)}"
                    if duration_s
                    else ""
                )
                + (f" for the reason: {reason}'" if reason else "")
            )
            self.bot.user_repo.ban_user(
                ctx.guild.id,
                member.id,
                duration_s,
                time(),
                ctx.author.display_name,
                reason,
            )

            if duration_s:
                em.description += f" for {self.bot.utils_class.duration(duration_s)}"
                self.bot.utils_class.task_launcher(
                    self.bot.utils_class.ban_completion,
                    (
                        self.bot.user_repo.get_user(ctx.guild.id, member.id),
                        ctx.guild.id,
                    ),
                    count=1,
                )
        except Forbidden:
            return await ctx.reply(
                f"⛔ - {ctx.author.mention} - I can't ban the member `{member}`!",
                delete_after=20,
            )

        await ctx.send(embed=em)

    """ MAIN GROUP'S WARN COMMAND(S) """

    @sanction_warn_group.command(
        name="add",
        brief="⚠️",
        usage='@member ("reason")',
        description="Warn a member with a reason attached if specified",
    )
    @max_concurrency(1, per=BucketType.member)
    async def sanction_warn_add_command(
        self, ctx: Context, member: Member, *, reason: str = None
    ):
        if "muted_role" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}config muted_role` to set one!",
                delete_after=20,
            )

        em = Embed(
            colour=self.bot.color,
            title=f"🚫 - Warn",
            description=f"The user `{member}` has been warned by {ctx.author.mention}",
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        if reason:
            em.add_field(name="reason:", value=reason, inline=False)

        self.bot.user_repo.warn_user(
            ctx.guild.id, member.id, time(), ctx.author.display_name, reason
        )
        warns = len(self.bot.user_repo.get_warns(ctx.guild.id, member.id))
        em.add_field(
            name=f"**Number of warnings of {member.display_name}:**",
            value=f"{warns}",
            inline=False,
        )

        if warns == 2 or warns == 4:
            if ctx.channel.permissions_for(ctx.guild.me).manage_roles:
                em.add_field(
                    name="sanction",
                    value=f"🔇 - Muted {'3H' if warns == 2 else '24H'} - 🔇",
                    inline=False,
                )

                try:
                    await member.add_roles(self.bot.configs[ctx.guild.id]["muted_role"])
                except Forbidden as f:
                    f.text = f"⚠️ - I don't have the right permissions to add the role `{self.bot.configs[ctx.guild.id]['muted_role']}` to {member}! (maybe the role is above mine)"
                    raise

                self.bot.user_repo.mute_user(
                    ctx.guild.id,
                    member.id,
                    10800 if warns == 2 else 86400,
                    time(),
                    self.bot.user.display_name,
                    f"{'2nd' if warns == 2 else '4th'} warn",
                )
                self.bot.tasks[ctx.guild.id]["mute_completions"][
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
                    f"⚠️ - I don't have the right permissions to manage roles in this server (i tried to add the muted role to {member} after his {'2nd' if warns == 2 else '4th'} warn)! Required perms: `{', '.join([Permissions.manage_roles])}`",
                    ctx.guild.id,
                )
        elif warns == 5:
            em.add_field(name="sanction", value="⚠️ - Warning - ⚠", inline=False)

            try:
                await member.send(
                    f"⚠ - ️️{member.mention} You are on your 5th warn! The next time you're warn, you will be kicked from this server {ctx.guild}! - ⚠️"
                )
            except Forbidden:
                await ctx.send(
                    f"❌ - ️️{ctx.author.mention} - Couldn't send the message to {member}, please inform him that on the next warn he will be kicked from the server!"
                )
        elif warns > 5:
            em.add_field(name="sanction", value="🚫 - kick - 🚫", inline=False)

            if ctx.channel.permissions_for(ctx.guild.me).kick_members:
                await member.kick(reason="6th warn")
            else:
                await ctx.send(
                    f"❌ - {ctx.author.mention} - I don't have the permission to kick members! (try kicking him yourself then!)"
                )

        await ctx.send(embed=em)

    @sanction_warn_group.command(
        name="list",
        brief="ℹ️",
        usage="(@member)",
        description="Show the list of a member's warns or yours!",
    )
    async def sanction_warn_list_command(self, ctx: Context, member: Member = None):
        if not member:
            member = ctx.author

        em = Embed(
            colour=self.bot.color, title=f"⚠️ - list of previous warns from {member}"
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        warns = self.bot.user_repo.get_warns(ctx.guild.id, member.id)

        if not warns:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - {f'The member {member}' if member != ctx.author else 'You'} has never been warned."
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

        await ctx.send(embed=em)

    """ MAIN GROUP'S MUTE COMMAND(S) """

    @sanction_mute_group.command(
        name="add",
        brief="🔇",
        usage='@member ("reason") (<duration_value> <duration_type>)',
        description="Mute a member for a certain duration with a reason attached if specified! (default/minimum duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
    )
    @bot_has_permissions(manage_roles=True)
    @max_concurrency(1, per=BucketType.member)
    async def sanction_mute_add_command(self, ctx: Context, member: Member, *args: str):
        if "muted_role" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}config muted_role` to set one!",
                delete_after=20,
            )

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
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `⚠️ - {ctx.author.mention} - Please provide a valid duration! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.`)! Required perms: `{', '.join([Permissions.send_messages])}`"
                raise
            return

        duration_s = await self.bot.utils_class.parse_duration(
            int(_duration), type_duration, ctx
        )
        if not duration_s:
            return

        em = Embed(
            colour=self.bot.color,
            title=f"🔇 - Mute",
            description=f"The member `{member}` has been muted by {ctx.author.mention}",
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        if reason:
            em.add_field(name="reason:", value=reason, inline=False)

        db_user = self.bot.user_repo.get_user(ctx.guild.id, member.id)

        if (
            self.bot.configs[ctx.guild.id]["muted_role"] not in member.roles
            or not db_user["muted"]
        ):
            em.description = f"The member `{member}` has been muted by {ctx.author.mention} for {self.bot.utils_class.duration(duration_s)}"
            await member.add_roles(
                self.bot.configs[ctx.guild.id]["muted_role"],
                reason="Muted from command sanction.",
            )
            self.bot.user_repo.mute_user(
                ctx.guild.id,
                member.id,
                duration_s,
                time(),
                ctx.author.display_name,
                reason,
            )
            self.bot.tasks[ctx.guild.id]["mute_completions"][
                member.id
            ] = self.bot.utils_class.task_launcher(
                self.bot.utils_class.mute_completion,
                (
                    self.bot.user_repo.get_user(ctx.guild.id, member.id),
                    ctx.guild.id,
                ),
                count=1,
            )
        else:
            last_mute = self.bot.user_repo.get_last_mute(ctx.guild.id, member.id)
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

        await ctx.send(embed=em)

    @sanction_mute_group.command(
        name="list",
        brief="ℹ",
        usage="(@member)",
        description="Show the list of a member's mutes or yours!",
    )
    async def sanction_mute_list_command(
        self,
        ctx: Context,
        member: Member = None,
    ):
        if not member:
            member = ctx.author

        em = Embed(
            colour=self.bot.color,
            title=f"🔇 - List of previous mutes of {member}",
        )

        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        em.set_author(
            name=ctx.author.display_name,
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        db_user = self.bot.user_repo.get_user(ctx.guild.id, member.id)

        if "mutes" not in db_user or len(db_user["mutes"]) < 1:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - {f'The member {member}' if member != ctx.author else 'You'} has never been muted."
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

        await ctx.send(embed=em)

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
        db_user = self.bot.user_repo.get_user(ctx.guild.id, member.id)

        if (
            self.bot.configs[ctx.guild.id]["muted_role"] in member.roles
            or db_user["muted"]
        ):
            await member.remove_roles(
                self.bot.configs[ctx.guild.id]["muted_role"], reason=reason
            )
            self.bot.user_repo.unmute_user(ctx.guild.id, member.id)

            if (
                "reason" in db_user["mutes"][-1]
                and db_user["mutes"][-1]["reason"] != "joined the server"
            ):
                self.bot.tasks[ctx.guild.id]["mute_completions"][member.id].cancel()
                del self.bot.tasks[ctx.guild.id]["mute_completions"][member.id]

            await ctx.send(
                f"🔊 - The member {member} has been unmuted by {ctx.author.mention}."
            )
        else:
            await ctx.send(
                f"🔊 - {ctx.author.mention} - The member {member} is not or no longer muted."
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
