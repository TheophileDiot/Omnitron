from discord import Embed, Member, NotFound
from discord.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    Context,
    group,
    max_concurrency,
)
from discord.ext.commands.errors import MissingRequiredArgument
from inspect import Parameter
from numpy import isnan
from pandas import DataFrame

from bot import Omnitron
from data import Utils, Xp_class


class Miscellaneous(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.xp_class = Xp_class(bot)

    """ GROUP(S) """

    @group(
        pass_context=True,
        name="xp",
        aliases=["experience"],
        usage="(sub-command)",
        description="This command contains every xp realted commands",
    )
    @Utils.check_bot_starting()
    @bot_has_permissions(send_messages=True)
    async def xp_group(self, ctx: Context):
        """Group containing every xp commands

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        """

        if ctx.invoked_subcommand is None:  # If no subcommand is passed
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's xp commands"
                )
            )

    """ GROUP'S COMMAND(S) """

    @xp_group.command(
        name="levels",
        aliases=["lvl", "lvls"],
        brief="🆙",
        usage="add|set|remove @member <number of levels>",
        description="This option manages member's levels",
    )
    @Utils.check_moderator()
    @max_concurrency(1, per=BucketType.guild)
    async def xp_levels_command(
        self, ctx: Context, option: Utils.to_lower, member: Member, value: int = None
    ):
        """Command that manages member's levels

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        option -- The option to be used
        member -- The member to manage the levels
        value -- The value that will be used
        """

        if member.bot:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - You can't manage the levels of a bot user!",
                delete_after=20,
            )
        elif isinstance(value, int) and value <= 0:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - The number of levels value must be greater than 0!",
                delete_after=20,
            )

        if option == "add":
            if not value:
                value = 1

            warn, true_value, nbr_lvls = self.bot.user_repo.add_levels(
                ctx.guild.id, member.id, value
            )  # Add the levels to the user in the database

            if warn:
                apostrophe = "'"
                if true_value == 0:
                    return await ctx.send(
                        f"ℹ️ - {member.mention} - {'The user you tried to give levels to is' if member.id != ctx.author.id else 'You are'} already max level, {f'he won{apostrophe}t be able to' if member.id != ctx.author.id else f'you won{apostrophe}t be able to'} gain levels!",
                        delete_after=20,
                    )
                await ctx.send(
                    f"ℹ️ - {member.mention} - {'The user you gave levels to is' if member.id != ctx.author.id else 'You are'} already level `{nbr_lvls - true_value}`, {f'he won{apostrophe}t be able to' if member.id != ctx.author.id else f'you won{apostrophe}t be able to'} gain `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                    delete_after=20,
                )

            if member.id == ctx.author.id:
                await ctx.send(
                    f"🆙 - {member.mention} - You have gained `{true_value}` levels ! You are now at level `{nbr_lvls}`!"
                )
            else:
                await ctx.send(
                    f"🆙 - {member.mention} - You have just gained `{true_value}` levels from `{ctx.author.display_name}`! You are now at level `{nbr_lvls}`!"
                )
        elif option == "set":
            if not value:
                raise MissingRequiredArgument(
                    param=Parameter(name="levels", kind=Parameter.KEYWORD_ONLY)
                )
            elif value > self.bot.configs[ctx.guild.id]["xp"]["max_lvl"]:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - You can't set a member's levels above the server's maximum level value! Server's maximum levels value: {self.bot.configs[ctx.guild.id]['xp']['max_lvl']}",
                    delete_after=20,
                )

            self.bot.user_repo.set_levels(
                ctx.guild.id, member.id, value
            )  # Set the levels to the user in the database

            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - {f'`{member}` is' if member.id != ctx.author.id else 'You are'} now level `{value}`!"
            )
        elif option == "remove":
            if not value:
                value = 1

            warn, true_value, nbr_lvls = self.bot.user_repo.remove_levels(
                ctx.guild.id, member.id, value
            )  # Remove the levels from the user in the database

            if warn:
                apostrophe = "'"
                if true_value == 0:
                    return await ctx.send(
                        f"ℹ️ - {member.mention} - {'The user you tried to remove levels to is' if member.id != ctx.author.id else 'You are'} already level `1`, {f'he won{apostrophe}t be able to' if member.id != ctx.author.id else f'you won{apostrophe}t be able to'} lose levels!",
                        delete_after=20,
                    )
                await ctx.send(
                    f"ℹ️ - {member.mention} - {'The user you removed levels to is' if member.id != ctx.author.id else 'You are'} already level `{nbr_lvls + true_value}`, {f'he won{apostrophe}t be able to' if member.id != ctx.author.id else f'you won{apostrophe}t be able to'} lose `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                    delete_after=20,
                )

            if member.id == ctx.author.id:
                await ctx.send(
                    f"🆙 - {member.mention} - You have lost `{true_value}` levels! You are now at level `{nbr_lvls}`!"
                )
            else:
                await ctx.send(
                    f"🆙 - {member.mention} - You have just lost `{true_value}` levels from `{ctx.author.display_name}`! You are now at level `{nbr_lvls}`!"
                )
        else:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` for more details!",
                delete_after=20,
            )

        await self.xp_class.manage_levels(
            member,
            self.bot.user_repo.get_user(ctx.guild.id, member.id)["level"],
            "set_lvl",
        )

    @xp_group.command(
        name="prestige",
        aliases=["prstg"],
        brief="🌟",
        description="Allows you to create a prestige level passage procedure! (one procedure at a time, server's max level required)",
    )
    @max_concurrency(1, per=BucketType.member)
    async def xp_prestige_command(self, ctx: Context):
        """Command that creates a prestige level passage procedure

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        """

        if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - No prestiges are available in this server yet!",
                delete_after=20,
            )

        db_user = self.bot.user_repo.get_user(ctx.guild.id, ctx.author.id)

        if db_user["level"] == self.bot.configs[ctx.guild.id]["xp"]["max_lvl"] and (
            db_user["prestige"] or 0
        ) < len(self.bot.configs[ctx.guild.id]["xp"]["prestiges"]):
            if "prestige_pending" in db_user:
                return await ctx.reply(
                    f"⛔ - {ctx.author.mention} - You cannot create two prestige pass-through procedures simultaneously. See `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` for more details!",
                    delete_after=20,
                )
            else:
                self.bot.user_repo.prepare_prestige(
                    ctx.guild.id, ctx.author.id, ctx.message.id
                )  # Create a pending prestige passage procedure
                await ctx.message.add_reaction("✅")  # Add a checkmark reaction
                await ctx.message.add_reaction("❌")  # Add a cross reaction
        elif (db_user["prestige"] or 0) != len(
            self.bot.configs[ctx.guild.id]["xp"]["prestiges"]
        ):
            return await ctx.reply(
                f"⛔ - {ctx.author.mention} - You are not yet level `{self.bot.configs[ctx.guild.id]['xp']['max_lvl']}`, so you can't pass a prestige level yet! (current level: `{db_user['level']}`) (next prestige level: `@{self.bot.configs[ctx.guild.id]['xp']['prestiges'][db_user['prestige'] + 1 or 1].name}`). `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` for more details!",
                delete_after=20,
            )
        else:
            return await ctx.reply(
                f"✅ - {ctx.author.mention} - You have reached the maximum prestige level, so you cannot gain any more prestige levels! Congratulations!"
            )

    @xp_group.command(
        name="info",
        aliases=["infos"],
        brief="ℹ️",
        usage="(@member)",
        description="Displays the current level and the number of xp remaining before the next level for yourself or someone on the server!",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def xp_rank_command(self, ctx: Context, member: Member = None):
        """Command that displays the current level and the number of xp remaining before the next level for the member that invoked the command or a specified member

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        member -- The member to display the info for (defaults to the author)
        """

        if not member:
            member = ctx.author
        elif member.bot:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - I can't display the current rank of a bot user!",
                delete_after=20,
            )
        db_user = self.bot.user_repo.get_user(ctx.guild.id, member.id)
        if db_user["level"] == int(self.bot.configs[member.guild.id]["xp"]["max_lvl"]):
            await ctx.send(
                f"ℹ️ - {member.mention} - {'You ' if member.id == ctx.author.id else ''}have already reached the maximum level "
                + (
                    f"for the prestige `{db_user['prestige'] or 0}`!"
                    if "prestiges" in self.bot.configs[ctx.guild.id]["xp"]
                    else "of the server!"
                )
            )  # If the member is at the max level, display the message
        else:
            await ctx.send(
                f"ℹ️ - {member.mention} - {'You only have' if member.id == ctx.author.id else 'Only'} `{(5 * (db_user['level'] ^ 2) + 50 * db_user['level'] + 100) - db_user['xp']}` of xp left before "
                + (
                    "you reach"
                    if member.id == ctx.author.id
                    else f"{member.display_name} reaches"
                )
                + f" the level `{db_user['level'] + 1}` "
                + (
                    f"of the prestige `{db_user['prestige']}`"
                    if "prestiges" in self.bot.configs[ctx.guild.id]["xp"]
                    and db_user["prestige"]
                    else (
                        "of the server"
                        if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]
                        else ""
                    )
                )
                + f"! {' Keep it up!' if member.id == ctx.author.id else ''}"
            )

    @xp_group.command(
        name="leaderboard",
        aliases=["ranking", "top"],
        brief="👑",
        usage="(me) (all)",
        description="Display the top 10 members of the server or your own rank (possibility to display the rank of the moderators)!",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def leaderboard_command(
        self, ctx: Context, *, options: Utils.to_lower = None
    ):
        """Command that displays the top 10 members of the server with the highest xp

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        options -- The options to display the top 10 members with (defaults to None)
        """

        async with ctx.typing():
            df_users = DataFrame.from_dict(
                data=self.bot.user_repo.get_users(ctx.guild.id),
                orient="index",
                columns=["name", "prestige", "level", "xp"],
            )
            df_users.index = df_users.index.astype(int)
            df_users = (
                df_users.sort_values(["xp"], ascending=False, kind="mergesort")
                .sort_values(["level"], ascending=False, kind="mergesort")
                .sort_values(
                    ["prestige"], ascending=False, na_position="last", kind="mergesort"
                )
            )  # Sort the dataframe by xp < level < prestige
            add = "of the server *(not including moderators)*"
            mods = False

            if options:
                options = options.split(" ")

            if options and options[0] == "me":
                if len(options) > 1 and options[1] == "all":
                    mods = True

                x = 1
                for df_user in df_users.index.values:
                    if mods or self.bot.utils_class.is_mod(ctx.author, self.bot):
                        if df_user == ctx.author.id:
                            if mods or self.bot.utils_class.is_mod(
                                ctx.author, self.bot
                            ):
                                add = "of the server *(including moderators)*"

                            await ctx.send(
                                f"{ctx.author.mention} - You are in the `{x}{'st' if x == 1 else ('nd' if x == 2 else 'th')}` place {add}! Keep it up! - **Prestige:** {df_users['prestige'][df_user] if not isnan(df_users['prestige'][df_user]) else 0} - **Level:** {df_users['level'][df_user]} - **XP:** {df_users['xp'][df_user]}"
                            )
                            break

                        x += 1
            else:
                if options and options[0] == "all":
                    mods = True
                    add = "of the server *(including moderators)*"

                em = Embed(colour=self.bot.color, title=f"Ranking {add}!")
                em.set_thumbnail(url=ctx.guild.icon_url)
                em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
                em.set_footer(
                    text=self.bot.user.name, icon_url=self.bot.user.avatar_url
                )

                x = 1
                for df_user in df_users.index.values:
                    if x > 10:
                        break

                    try:
                        member = await ctx.guild.try_member(int(df_user))
                    except NotFound:
                        continue

                    if mods or not self.bot.utils_class.is_mod(member, self.bot):
                        em.add_field(
                            name=f"{x} - {df_users['name'][df_user]}",
                            value=f"**Prestige:** {df_users['prestige'][df_user] if not isnan(df_users['prestige'][df_user]) else 0}\n**Level:** {df_users['level'][df_user]}\n**XP:** {df_users['xp'][df_user]}",
                            inline=True,
                        )

                    x += 1

                await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
