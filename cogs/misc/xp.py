from inspect import Parameter
from typing import Union

from disnake import (
    ApplicationCommandInteraction,
    Embed,
    Member,
    NotFound,
    Option,
    OptionType,
)
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    Context,
    group,
    max_concurrency,
    slash_command,
)
from disnake.ext.commands.errors import MissingRequiredArgument
from numpy import isnan
from pandas import DataFrame

from bot import Omnitron
from data import Utils, Xp_class


class Miscellaneous(Cog, name="misc.xp"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.xp_class = Xp_class(bot)

    """ GROUP(S) """

    @group(
        pass_context=True,
        name="xp",
        aliases=["experience"],
        usage="(sub-command)",
        description="This command contains every xp related commands",
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

    @slash_command(
        name="xp",
        description="This command contains every xp related commands",
    )
    @Utils.check_bot_starting()
    async def xp_slash_group(self, inter: ApplicationCommandInteraction):
        pass

    """ GROUP'S COMMAND(S) """

    """ LEVELS """

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
        await self.handle_levels(ctx, option, member, value)

    @xp_slash_group.sub_command_group(
        name="levels",
        description="This option manages member's levels",
    )
    async def xp_levels_slash_group(self, inter: ApplicationCommandInteraction):
        pass

    @xp_levels_slash_group.sub_command(
        name="add",
        description="Add levels to a specific member or yourself! (default levels added = 1)",
        options=[
            Option(
                name="member",
                description="The member to add levels to",
                type=OptionType.user,
                required=False,
            ),
            Option(
                name="value",
                description="The number of levels to add",
                type=OptionType.integer,
                required=False,
            ),
        ],
    )
    async def xp_levels_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
        value: int = 1,
    ):
        await self.handle_levels(
            inter, "add", member if member else inter.author, value
        )

    @xp_levels_slash_group.sub_command(
        name="set",
        description="Set the levels of a specific member or yourself!",
        options=[
            Option(
                name="value",
                description="The value of levels to set",
                type=OptionType.integer,
                required=True,
            ),
            Option(
                name="member",
                description="The member to set levels to",
                type=OptionType.user,
                required=False,
            ),
        ],
    )
    async def xp_levels_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        value: int,
        member: Member = None,
    ):
        await self.handle_levels(
            inter, "set", member if member else inter.author, value
        )

    @xp_levels_slash_group.sub_command(
        name="remove",
        description="Remove levels from a specific member or yourself! (default levels removed = 1)",
        options=[
            Option(
                name="member",
                description="The member to remove levels from",
                type=OptionType.user,
                required=False,
            ),
            Option(
                name="value",
                description="The number of levels to remove",
                type=OptionType.integer,
                required=False,
            ),
        ],
    )
    async def xp_levels_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
        value: int = 1,
    ):
        await self.handle_levels(
            inter, "remove", member if member else inter.author, value
        )

    async def handle_levels(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: Utils.to_lower,
        member: Member,
        value: Union[int, None] = None,
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
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - You can't manage the levels of a bot user!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - You can't manage the levels of a bot user!",
                    ephemeral=True,
                )
        elif isinstance(value, int) and value <= 0:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - The number of levels value must be greater than 0!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The number of levels value must be greater than 0!",
                    ephemeral=True,
                )

        if option == "add":
            if not value:
                value = 1

            warn, true_value, nbr_lvls = self.bot.user_repo.add_levels(
                source.guild.id, member.id, value
            )  # Add the levels to the user in the database

            if warn:
                apostrophe = "'"

                if true_value == 0:
                    if isinstance(source, Context):
                        return await source.send(
                            f"ℹ️ - {member.mention} - {'The user you tried to give levels to is' if member.id != source.author.id else 'You are'} already max level, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} gain levels!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {member.mention} - {'The user you tried to give levels to is' if member.id != source.author.id else 'You are'} already max level, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} gain levels!",
                            ephemeral=True,
                        )

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - {member.mention} - {'The user you gave levels to is' if member.id != source.author.id else 'You are'} already level `{nbr_lvls - true_value}`, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} gain `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                        delete_after=20,
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - {member.mention} - {'The user you gave levels to is' if member.id != source.author.id else 'You are'} already level `{nbr_lvls - true_value}`, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} gain `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                        ephemeral=True,
                    )

            if member.id == source.author.id:
                resp = f"🆙 - {member.mention} - You have gained `{true_value}` levels ! You are now at level `{nbr_lvls}`!"
            else:
                resp = f"🆙 - {member.mention} - You have just gained `{true_value}` levels from `{source.author.display_name}`! You are now at level `{nbr_lvls}`!"
        elif option == "set":
            if not value:
                raise MissingRequiredArgument(
                    param=Parameter(name="levels", kind=Parameter.KEYWORD_ONLY)
                )
            elif value > self.bot.configs[source.guild.id]["xp"]["max_lvl"]:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - You can't set a member's levels above the server's maximum level value! Server's maximum levels value: {self.bot.configs[source.guild.id]['xp']['max_lvl']}",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - You can't set a member's levels above the server's maximum level value! Server's maximum levels value: {self.bot.configs[source.guild.id]['xp']['max_lvl']}",
                        ephemeral=True,
                    )

            self.bot.user_repo.set_levels(
                source.guild.id, member.id, value
            )  # Set the levels to the user in the database

            resp = f"ℹ️ - {source.author.mention} - {f'`{member}` is' if member.id != source.author.id else 'You are'} now level `{value}`!"
        elif option == "remove":
            if not value:
                value = 1

            warn, true_value, nbr_lvls = self.bot.user_repo.remove_levels(
                source.guild.id, member.id, value
            )  # Remove the levels from the user in the database

            if warn:
                apostrophe = "'"

                if true_value == 0:
                    return await source.send(
                        f"ℹ️ - {member.mention} - {'The user you tried to remove levels to is' if member.id != source.author.id else 'You are'} already level `1`, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} lose levels!",
                        delete_after=20,
                    )

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - {member.mention} - {'The user you removed levels to is' if member.id != source.author.id else 'You are'} already level `{nbr_lvls + true_value}`, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} lose `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                        delete_after=20,
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - {member.mention} - {'The user you removed levels to is' if member.id != source.author.id else 'You are'} already level `{nbr_lvls + true_value}`, {f'he won{apostrophe}t be able to' if member.id != source.author.id else f'you won{apostrophe}t be able to'} lose `{value}` additional levels, so the value has been reduced to `{true_value}`!",
                        ephemeral=True,
                    )

            if member.id == source.author.id:
                resp = f"🆙 - {member.mention} - You have lost `{true_value}` levels! You are now at level `{nbr_lvls}`!"
            else:
                resp = f"🆙 - {member.mention} - You have just lost `{true_value}` levels from `{source.author.display_name}`! You are now at level `{nbr_lvls}`!"
        else:
            return await source.reply(
                f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` for more details!",
                delete_after=20,
            )

        if isinstance(source, Context):
            await source.send(resp)
        else:
            await source.response.send_message(resp)

        await self.xp_class.manage_levels(
            member,
            self.bot.user_repo.get_user(source.guild.id, member.id)["level"],
            "set_lvl",
        )

    """ PRESTIGE """

    @xp_group.command(
        name="prestige",
        aliases=["prstg"],
        brief="🌟",
        description="Allows you to create a prestige level passage procedure! (one procedure at a time, server's max level required)",
    )
    @max_concurrency(1, per=BucketType.member)
    async def xp_prestige_command(self, ctx: Context):
        await self.handle_prestige(ctx)

    @xp_slash_group.sub_command(
        name="prestige",
        description="Allows you to create a prestige level passage procedure!",
    )
    @max_concurrency(1, per=BucketType.member)
    async def xp_prestige_slash_command(self, inter: ApplicationCommandInteraction):
        await self.handle_prestige(inter)

    async def handle_prestige(
        self, source: Union[Context, ApplicationCommandInteraction]
    ):
        """Command that creates a prestige level passage procedure

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        """

        if "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - No prestiges are available in this server yet!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - No prestiges are available in this server yet!",
                    ephemeral=True,
                )

        db_user = self.bot.user_repo.get_user(source.guild.id, source.author.id)
        ephemeral = False

        if db_user["level"] == self.bot.configs[source.guild.id]["xp"]["max_lvl"] and (
            db_user["prestige"] or 0
        ) < len(self.bot.configs[source.guild.id]["xp"]["prestiges"]):
            if "prestige_pending" in db_user:
                resp = f"⛔ - {source.author.mention} - You cannot create two prestige pass-through procedures simultaneously."
                ephemeral = True
            else:
                if isinstance(source, ApplicationCommandInteraction):
                    await source.response.send_message(
                        "Prestige level passage procedure confirmation!"
                    )
                    msg = await source.original_message()
                else:
                    msg = source.message

                self.bot.user_repo.prepare_prestige(
                    source.guild.id, source.author.id, msg.id
                )  # Create a pending prestige passage procedure
                await msg.add_reaction("✅")  # Add a checkmark reaction
                return await msg.add_reaction("❌")  # Add a cross reaction
        elif (db_user["prestige"] or 0) != len(
            self.bot.configs[source.guild.id]["xp"]["prestiges"]
        ):
            resp = f"⛔ - {source.author.mention} - You are not yet level `{self.bot.configs[source.guild.id]['xp']['max_lvl']}`, so you can't pass a prestige level yet! (current level: `{db_user['level']}`) (next prestige level: `@{self.bot.configs[source.guild.id]['xp']['prestiges'][db_user['prestige'] + 1 or 1].name}`)."
            ephemeral = True
        else:
            resp = f"✅ - {source.author.mention} - You have reached the maximum prestige level, so you cannot gain any more prestige levels! Congratulations!"

        if isinstance(source, Context):
            await source.reply(resp, delete_after=20 if ephemeral else None)
        else:
            await source.response.send_message(resp, ephemeral=ephemeral)

    """ INFO """

    @xp_group.command(
        name="info",
        aliases=["infos"],
        brief="ℹ️",
        usage="(@member)",
        description="Displays the current level and the number of xp remaining before the next level for yourself or someone on the server!",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def xp_info_command(self, ctx: Context, member: Member = None):
        await self.handle_info(ctx, member)

    @xp_slash_group.sub_command(
        name="info",
        description="Displays information about the current level for yourself or someone on the server!",
        options=[
            Option(
                name="member",
                description="The member to get info from",
                type=OptionType.user,
                required=False,
            ),
        ],
    )
    @max_concurrency(1, per=BucketType.guild)
    async def xp_info_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member = None
    ):
        await self.handle_info(inter, member)

    async def handle_info(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Union[Member, None],
    ):
        """Command that displays the current level and the number of xp remaining before the next level for the member that invoked the command or a specified member

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        member -- The member to display the info for (defaults to the author)
        """

        if not member:
            member = source.author
        elif member.bot:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - I can't display the current rank of a bot user!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - I can't display the current rank of a bot user!",
                    ephemeral=True,
                )

        db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

        if db_user["level"] == int(self.bot.configs[member.guild.id]["xp"]["max_lvl"]):
            resp = (
                f"ℹ️ - {source.author.mention} - {'You' if member.id == source.author.id else f'{member.mention}'} have already reached the maximum level "
                + (
                    f"for the prestige `{db_user['prestige'] or 0}`!"
                    if "prestiges" in self.bot.configs[source.guild.id]["xp"]
                    else "of the server!"
                )
            )  # If the member is at the max level, display the message
        else:
            resp = (
                f"ℹ️ - {source.author.mention} - {'You only have' if member.id == source.author.id else 'Only'} `{(5 * (db_user['level'] ^ 2) + 50 * db_user['level'] + 100) - db_user['xp']}` of xp left before "
                + (
                    "you reach"
                    if member.id == source.author.id
                    else f"{member} reaches"
                )
                + f" the level `{db_user['level'] + 1}` "
                + (
                    f"of the prestige `{db_user['prestige']}`"
                    if "prestiges" in self.bot.configs[source.guild.id]["xp"]
                    and db_user["prestige"]
                    else (
                        "of the server"
                        if "prestiges" not in self.bot.configs[source.guild.id]["xp"]
                        else ""
                    )
                )
                + f"! {' Keep it up!' if member.id == source.author.id else ''}"
            )

        if isinstance(source, Context):
            await source.send(resp)
        else:
            await source.response.send_message(resp)

    """ LEADERBOARD """

    @xp_group.command(
        name="leaderboard",
        aliases=["ranking", "top"],
        brief="👑",
        usage="(me) (all)",
        description="Display the top 10 members of the server or your own rank (possibility to display the rank of the moderators)!",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def xp_leaderboard_command(
        self, ctx: Context, *, options: Utils.to_lower = None
    ):
        if options:
            options = options.split(" ")

        me = False
        mods = False

        if options and options[0] == "me":
            me = True
            if len(options) > 1 and options[1] == "all":
                mods = True
        else:
            if options and options[0] == "all":
                mods = True

        await self.handle_leaderboard(ctx, me, mods)

    @xp_slash_group.sub_command(
        name="leaderboard",
        description="Display the top 10 members of the server or your own rank!",
        options=[
            Option(
                name="me",
                description="Only display your ranking",
                type=OptionType.boolean,
                required=False,
            ),
            Option(
                name="mods",
                description="Also count the mods in the ranking",
                type=OptionType.boolean,
                required=False,
            ),
        ],
    )
    @max_concurrency(1, per=BucketType.guild)
    async def xp_leaderboard_command(
        self, inter: ApplicationCommandInteraction, me: bool = False, mods: bool = False
    ):
        await self.handle_leaderboard(inter, me, mods)

    async def handle_leaderboard(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        me: bool = False,
        mods: bool = False,
    ):
        """Command that displays the top 10 members of the server with the highest xp

        Keyword arguments:
        self -- The self variable
        ctx -- The context object
        options -- The options to display the top 10 members with (defaults to None)
        """

        df_users = DataFrame.from_dict(
            data=self.bot.user_repo.get_users(source.guild.id),
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

        if me:
            x = 1
            for df_user in df_users.index.values:
                if mods or self.bot.utils_class.is_mod(source.author, self.bot):
                    if df_user == source.author.id:
                        if mods or self.bot.utils_class.is_mod(source.author, self.bot):
                            add = "of the server *(including moderators)*"

                        if isinstance(source, Context):
                            await source.send(
                                f"{source.author.mention} - You are in the `{x}{'st' if x == 1 else ('nd' if x == 2 else 'th')}` place {add}! Keep it up! - **Prestige:** {df_users['prestige'][df_user] if not isnan(df_users['prestige'][df_user]) else 0} - **Level:** {df_users['level'][df_user]} - **XP:** {df_users['xp'][df_user]}"
                            )
                        else:
                            await source.response.send_message(
                                f"{source.author.mention} - You are in the `{x}{'st' if x == 1 else ('nd' if x == 2 else 'th')}` place {add}! Keep it up! - **Prestige:** {df_users['prestige'][df_user] if not isnan(df_users['prestige'][df_user]) else 0} - **Level:** {df_users['level'][df_user]} - **XP:** {df_users['xp'][df_user]}"
                            )

                        break

                    x += 1
        else:
            if mods:
                add = "of the server *(including moderators)*"

            em = Embed(colour=self.bot.color, title=f"Ranking {add}!")
            em.set_thumbnail(url=source.guild.icon.url if source.guild.icon else None)
            em.set_author(
                name=source.guild.name,
                icon_url=source.guild.icon.url if source.guild.icon else None,
            )
            em.set_footer(
                text=self.bot.user.name,
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
            )

            x = 1
            for df_user in df_users.index.values:
                if x > 10:
                    break

                try:
                    member = source.guild.get_member(
                        int(df_user)
                    ) or await source.guild.fetch_member(int(df_user))
                except NotFound:
                    continue

                if mods or not self.bot.utils_class.is_mod(member, self.bot):
                    em.add_field(
                        name=f"{x} - {df_users['name'][df_user]}",
                        value=f"**Prestige:** {df_users['prestige'][df_user] if not isnan(df_users['prestige'][df_user]) else 0}\n**Level:** {df_users['level'][df_user]}\n**XP:** {df_users['xp'][df_user]}",
                        inline=True,
                    )

                    x += 1

            if isinstance(source, Context):
                await source.send(embed=em)
            else:
                await source.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
