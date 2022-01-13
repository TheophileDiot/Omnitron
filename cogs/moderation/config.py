from inspect import Parameter
from time import time
from typing import List, Literal, Union

from disnake import (
    ApplicationCommandInteraction,
    ButtonStyle,
    CategoryChannel,
    Embed,
    Forbidden,
    Member,
    NotFound,
    Role,
    SelectOption,
    TextChannel,
    VoiceChannel,
    Message,
)
from disnake.abc import Snowflake
from disnake.ext.commands import (
    bot_has_permissions,
    Context,
    Cog,
    group,
    guild_only,
    Param,
    slash_command,
)
from disnake.ext.commands.errors import (
    BadArgument,
    BadUnionArgument,
    MissingRequiredArgument,
)
from disnake.ui import Button, Select, View

from bot import Omnitron
from data import DurationType, Utils, Xp_class

BOOL2VAL = {True: "ON", False: "OFF"}


class Moderation(Cog, name="moderation.config"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.xp_class = Xp_class(bot)

    """ MAIN GROUP """

    @group(
        pass_context=True,
        case_insensitive=True,
        name="config",
        aliases=["cfg"],
        usage="(sub-command)",
        description="This command manage the server's configuration",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def config_group(self, ctx: Context):
        """
        This command group manages the server's configuration

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's configuration"
                )
            )

    """ MAIN GROUP'S GROUP(S) """

    @config_group.group(
        pass_context=True,
        case_insensitive=True,
        name="security",
        aliases=["secu"],
        brief="🚓",
        usage="(sub-command)",
        description="Manages the server's security",
    )
    async def config_security_group(self, ctx: Context):
        """
        This command group manages the server's security

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's security configuration",
                )
            )

    @slash_command(
        name="security",
        description="Manages the server's security",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_security_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's security

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_group.group(
        pass_context=True,
        case_insensitive=True,
        name="xp",
        aliases=["experience"],
        brief="✨",
        usage="(sub-command)",
        description="Manages the server's experience feature",
    )
    async def config_xp_group(self, ctx: Context):
        """
        This command group manages the server's experience feature

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's experience configuration",
                )
            )

    @slash_command(
        name="config_xp",
        description="Manages the server's experience feature",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_xp_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's experience feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_group.group(
        pass_context=True,
        case_insensitive=True,
        name="channels",
        aliases=["channel"],
        brief="📻",
        usage="(sub-command)",
        description="Manages the server's special channels",
    )
    async def config_channels_group(self, ctx: Context):
        """
        This command group manages the server's special channels

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's channels configuration",
                )
            )

    @slash_command(
        name="channels",
        description="Manages the server's special channels",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_channels_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's special channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    """ MAIN GROUP'S COMMAND(S) """

    """ MODERATORS """

    @config_group.command(
        pass_context=True,
        name="moderators",
        aliases=["mods"],
        brief="🔨",
        description="Manages the server's moderators (role & members) (can add/remove multiple at a time)",
        usage="(add|remove|purge @role|@member)",
    )
    async def config_moderators_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *mods: Union[Role, Member],
    ):
        """
        This command manages the server's moderators (role & members) (can add/remove multiple at a time)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or remove or purge
        mods: :class:`typing.Union[disnake.Role, disnake.Member]` optional
            The moderators (that can be either roles or members) (mentions only)
        """
        if mods:
            await self.handle_moderators(ctx, option, *mods)
        else:
            await self.handle_moderators(ctx, option)

    @slash_command(
        name="moderators",
        description="Manages the server's moderators (role & members)",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_moderators_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's moderators (role & members)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_moderators_slash_group.sub_command(
        name="list",
        description="Lists members/roles in the server's moderators list",
    )
    async def config_moderators_list_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command lists members/roles in the server's moderators list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_moderators(inter)

    @config_moderators_slash_group.sub_command(
        name="add",
        description="Adds members/roles to the server's moderators list (can add multiple at a time)",
    )
    async def config_moderators_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        mods: List[Union[Member, Role]] = Param(
            None, converter=Utils.mentionable_converter
        ),
    ):
        """
        This slash command adds members/roles to the server's moderators list (can add multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        mods: :class:`typing.List[typing.Union[disnake.Member, disnake.Role]]` optional
            The moderators (that can be either roles or members) (mentions only)
        """
        if mods:
            await self.handle_moderators(inter, "add", *mods)

    @config_moderators_slash_group.sub_command(
        name="remove",
        description="Removes members/roles from the server's moderators list (can remove multiple at a time)",
    )
    async def config_moderators_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        mods: List[Union[Member, Role]] = Param(
            default=None, converter=Utils.mentionable_converter
        ),
    ):
        """
        Removes members/roles from the server's moderators list (can remove multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        mods: :class:`typing.List[typing.Union[disnake.Member, disnake.Role]]` optional
            The moderators (that can be either roles or members) (mentions only)
        """
        if mods:
            await self.handle_moderators(inter, "remove", *mods)

    @config_moderators_slash_group.sub_command(
        name="purge", description="Purges the server's moderators list"
    )
    async def config_moderators_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's moderators list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_moderators(inter, "purge")

    async def handle_moderators(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        *mods: Union[Member, Role],
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not mods:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="moderators", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    _mods = mods
                    mods = list(mods)
                    warning_mods = []
                    dropped_mods = []
                    bot_mods = []
                    for mod in _mods:
                        if option == "add":
                            if mod.id in set(self.bot.moderators[source.guild.id]):
                                del mods[mods.index(mod)]
                                dropped_mods.append(mod)
                                continue
                            elif mod.id in set(self.bot.djs[source.guild.id]):
                                del mods[mods.index(mod)]
                                warning_mods.append([mod, "dj"])
                                continue
                            elif (
                                "muted_role" in self.bot.configs[source.guild.id]
                                and self.bot.configs[source.guild.id]["muted_role"]
                                == mod
                            ):
                                del mods[mods.index(mod)]
                                warning_mods.append([mod, "muted_role"])
                                continue
                            elif mod in set(
                                self.bot.configs[source.guild.id]["xp"][
                                    "prestiges"
                                ].values()
                            ):
                                del mods[mods.index(mod)]
                                warning_mods.append([mod, "prestige"])
                                continue
                            elif "lvl2role" in self.bot.configs[source.guild.id][
                                "xp"
                            ] and mod in set(
                                self.bot.configs[source.guild.id]["xp"][
                                    "lvl2role"
                                ].values()
                            ):
                                del mods[mods.index(mod)]
                                warning_mods.append([mod, "lvl2role"])
                                continue
                            elif (
                                "select2role" in self.bot.configs[source.guild.id]
                                and "selects"
                                in self.bot.configs[source.guild.id]["select2role"]
                                and mod
                                in {
                                    v["role"]
                                    for v in self.bot.configs[source.guild.id][
                                        "select2role"
                                    ]["selects"].values()
                                }
                            ):
                                del mods[mods.index(mod)]
                                warning_mods.append([mod, "select2role"])
                                continue
                            elif isinstance(mod, Member) and mod.bot:
                                del mods[mods.index(mod)]
                                bot_mods.append(mod)
                                continue

                            self.bot.config_repo.add_moderator(
                                source.guild.id, mod.id, f"{mod}", type(mod).__name__
                            )
                            self.bot.moderators[source.guild.id].append(mod.id)
                        elif option == "remove":
                            if mod.id not in set(self.bot.moderators[source.guild.id]):
                                del mods[mods.index(mod)]
                                dropped_mods.append(mod)
                                continue

                            self.bot.config_repo.remove_moderator(
                                source.guild.id, mod.id
                            )
                            del self.bot.moderators[source.guild.id][
                                self.bot.moderators[source.guild.id].index(mod.id)
                            ]

                    resp = ""

                    if bot_mods:
                        resp += f"ℹ️ - {source.author.mention} - {', '.join([f'`@{mod}`' for mod in bot_mods])} {'is a' if len(bot_mods) == 1 else 'are'} bot user{'s' if len(bot_mods) > 1 else ''} so you can't add {'them' if len(bot_mods) > 1 else 'him'} in the moderators list!"

                    if dropped_mods:
                        resp += (
                            ("\n" if resp else f"ℹ️ - {source.author.mention} - ")
                            + f"{', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in dropped_mods])} {'is' if len(dropped_mods) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the moderators list!"
                        )

                    if warning_mods:
                        resp += (
                            ("\n" if resp else f"ℹ️ - {source.author.mention} - ")
                            + f"{', '.join([f'`@{mod[0]} ({type(mod[0]).__name__})` is already assigned to a {mod[1]} role' for mod in warning_mods])}!"
                        )

                    if resp:
                        if isinstance(source, Context):
                            await source.reply(resp, delete_after=20)
                        else:
                            await source.channel.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in mods])} {'to' if option == 'add' else 'from'} the moderators list!.",
                                delete_after=20,
                            )

                    if mods:
                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in mods])} {'to' if option == 'add' else 'from'} the moderators list!."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in mods])} {'to' if option == 'add' else 'from'} the moderators list!."
                            )
                elif option == "purge":
                    if not self.bot.moderators[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No moderators (members & roles) have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No moderators (members & roles) have been added to the list yet!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_moderators(source.guild.id)
                    self.bot.moderators[source.guild.id] = {}

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the moderators from the moderators list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the moderators from the moderators list."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while updating the moderators list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_mods = self.bot.config_repo.get_moderators(source.guild.id).values()

            if not server_mods:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No moderators (members & roles) have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No moderators (members & roles) have been added to the list yet!",
                        ephemeral=True,
                    )

            server_mods_roles = []
            server_mods_members = []

            for m in server_mods:
                if m["type"] == "Role":
                    server_mods_roles.append(m["name"])
                else:
                    server_mods_members.append(m["name"])

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's moderators:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m}`' for m in server_mods_members)}\n"
                        if server_mods_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r}`' for r in server_mods_roles)}\n"
                        if server_mods_roles
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's moderators:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m}`' for m in server_mods_members)}\n"
                        if server_mods_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r}`' for r in server_mods_roles)}\n"
                        if server_mods_roles
                        else ""
                    )
                )

    """ DJS """

    @config_group.command(
        pass_context=True,
        name="djs",
        aliases=["players"],
        brief="🧑‍🎤",
        description="Manages the server's djs (role & members) (if there is no dj then everyone can use music commands) (can add/remove multiple at a time)",
        usage="(add|remove|purge @role|@member)",
    )
    async def config_djs_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *djs: Union[Role, Member],
    ):
        """
        This command group manages the server's djs (role & members) (if there is no dj then everyone can use music commands) (can add/remove multiple at a time)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or remove or purge
        djs: :class:`typing.Union[disnake.Role, disnake.Member]` optional
            The djs (that can be either roles or members) (mentions only)
        """
        if djs:
            await self.handle_djs(ctx, option, *djs)
        else:
            await self.handle_djs(ctx, option)

    @slash_command(
        name="djs",
        description="Manages the server's djs (role & members)",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_djs_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's djs (role & members)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_djs_slash_group.sub_command(
        name="list",
        description="Lists members/roles in the server's djs list",
    )
    async def config_djs_list_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group lists members/roles in the server's djs list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_djs(inter)

    @config_djs_slash_group.sub_command(
        name="add",
        description="Adds members/roles to the server's djs list (can add multiple at a time)",
    )
    async def config_djs_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        djs: List[Union[Member, Role]] = Param(converter=Utils.mentionable_converter),
    ):
        """
        This slash command adds members/roles to the server's djs list (can add multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        djs: :class:`typing.List[typing.Union[disnake.Member, disnake.Role]]` optional
            The djs (that can be either roles or members) (mentions only)
        """
        if djs:
            await self.handle_djs(inter, "add", *djs)

    @config_djs_slash_group.sub_command(
        name="remove",
        description="Removes members/roles from the server's djs list (can remove multiple at a time)",
    )
    async def config_djs_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        djs: List[Union[Member, Role]] = Param(
            default=None, converter=Utils.mentionable_converter
        ),
    ):
        """
        This slash command removes members/roles from the server's djs list (can remove multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        djs: :class:`typing.List[typing.Union[disnake.Member, disnake.Role]]` optional
            The djs (that can be either roles or members) (mentions only)
        """
        if djs:
            await self.handle_djs(inter, "remove", *djs)

    @config_djs_slash_group.sub_command(
        name="purge", description="Purges the server's djs list"
    )
    async def config_djs_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's djs list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_djs(inter, "purge")

    async def handle_djs(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        *djs: Union[Member, Role],
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not djs:
                        raise MissingRequiredArgument(
                            param=Parameter(name="djs", kind=Parameter.KEYWORD_ONLY)
                        )

                    _djs = djs
                    djs = list(djs)
                    warning_djs = []
                    dropped_djs = []
                    bot_djs = []
                    for dj in _djs:
                        if option == "add":
                            if dj.id in set(self.bot.djs[source.guild.id]):
                                del djs[djs.index(dj)]
                                dropped_djs.append(dj)
                                continue
                            elif dj in set(
                                self.bot.configs[source.guild.id]["xp"][
                                    "prestiges"
                                ].values()
                            ):
                                del djs[djs.index(dj)]
                                warning_djs.append([dj, "prestige"])
                                continue
                            elif (
                                "muted_role" in self.bot.configs[source.guild.id]
                                and self.bot.configs[source.guild.id]["muted_role"]
                                == dj
                            ):
                                del djs[djs.index(dj)]
                                warning_djs.append([dj, "muted_role"])
                                continue
                            elif "lvl2role" in self.bot.configs[source.guild.id][
                                "xp"
                            ] and dj in set(
                                self.bot.configs[source.guild.id]["xp"][
                                    "lvl2role"
                                ].values()
                            ):
                                del djs[djs.index(dj)]
                                warning_djs.append([dj, "lvl2role"])
                                continue
                            elif (
                                "select2role" in self.bot.configs[source.guild.id]
                                and "selects"
                                in self.bot.configs[source.guild.id]["select2role"]
                                and dj
                                in {
                                    v["role"]
                                    for v in self.bot.configs[source.guild.id][
                                        "select2role"
                                    ]["selects"].values()
                                }
                            ):
                                del djs[djs.index(dj)]
                                warning_djs.append([dj, "select2role"])
                                continue
                            elif isinstance(dj, Member) and dj.bot:
                                del djs[djs.index(dj)]
                                bot_djs.append(dj)
                                continue

                            self.bot.config_repo.add_dj(
                                source.guild.id, dj.id, f"{dj}", type(dj).__name__
                            )
                            self.bot.djs[source.guild.id].append(dj.id)
                        elif option == "remove":
                            if dj.id not in set(self.bot.djs[source.guild.id]):
                                del djs[djs.index(dj)]
                                dropped_djs.append(dj)
                                continue

                            self.bot.config_repo.remove_dj(source.guild.id, dj.id)
                            del self.bot.djs[source.guild.id][
                                self.bot.djs[source.guild.id].index(dj.id)
                            ]

                            try:
                                if isinstance(source, Context):
                                    await source.send(
                                        f"ℹ️ - Removed `@{source.guild.get_member(int(dj.id)) or await source.guild.fetch_member(int(dj.id)) if isinstance(dj, Member) else source.guild.get_role(int(dj.id))}` {'role' if isinstance(dj, Role) else 'member'} from the djs list!."
                                    )
                                else:
                                    await source.channel.send(
                                        f"ℹ️ - Removed `@{source.guild.get_member(int(dj.id)) or await source.guild.fetch_member(int(dj.id)) if isinstance(dj, Member) else source.guild.get_role(int(dj.id))}` {'role' if isinstance(dj, Role) else 'member'} from the djs list!."
                                    )
                            except NotFound:
                                pass

                    resp = ""

                    if bot_djs:
                        resp += f"ℹ️ - {source.author.mention} - {', '.join([f'`@{dj}`' for dj in bot_djs])} {'is a' if len(bot_djs) == 1 else 'are'} bot user{'s' if len(bot_djs) > 1 else ''} so you can't add {'them' if len(bot_djs) > 1 else 'him'} in the djs list!"

                    if dropped_djs:
                        resp += (
                            ("\n" if resp else f"ℹ️ - {source.author.mention} - ")
                            + f"{', '.join([f'`@{dj} ({type(dj).__name__})`' for dj in dropped_djs])} {'is' if len(dropped_djs) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the djs list!"
                        )

                    if warning_djs:
                        resp += (
                            ("\n" if resp else f"ℹ️ - {source.author.mention} - ")
                            + f"{', '.join([f'`@{dj[0]} ({type(dj[0]).__name__})` is already assigned to a {dj[1]} role' for dj in warning_djs])}!"
                        )

                    if resp:
                        if isinstance(source, Context):
                            await source.reply(resp, delete_after=20)
                        else:
                            await source.channel.send(resp, delete_after=20)

                    if djs:
                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{dj} ({type(dj).__name__})`' for dj in djs])} {'to' if option == 'add' else 'from'} the djs list!."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{dj} ({type(dj).__name__})`' for dj in djs])} {'to' if option == 'add' else 'from'} the djs list!."
                            )
                elif option == "purge":
                    if not self.bot.djs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No djs (members & roles) have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No djs (members & roles) have been added to the list yet!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_djs(source.guild.id)
                    self.bot.djs[source.guild.id] = {}

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the djs from the djs list!."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the djs from the djs list!."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} `@{dj}` {'role' if isinstance(dj, Role) else 'member'} to the djs list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_djs = self.bot.config_repo.get_djs(source.guild.id).values()

            if not server_djs:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No djs (members & roles) have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No djs (members & roles) have been added to the list yet!",
                        ephemeral=True,
                    )

            server_djs_roles = []
            server_djs_members = []

            for m in server_djs:
                if m["type"] == "Role":
                    server_djs_roles.append(m["name"])
                else:
                    server_djs_members.append(m["name"])

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's djs:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m}`' for m in server_djs_members)}\n"
                        if server_djs_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r}`' for r in server_djs_roles)}\n"
                        if server_djs_roles
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's djs:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m}`' for m in server_djs_members)}\n"
                        if server_djs_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r}`' for r in server_djs_roles)}\n"
                        if server_djs_roles
                        else ""
                    )
                )

    """ PREFIX """

    @config_group.command(
        pass_context=True,
        name="prefix",
        aliases=["prfx"],
        brief="❗",
        description="Manages the server's prefix",
        usage="(set|reset) (<prefix>)",
    )
    async def config_prefix_command(
        self, ctx: Context, option: Utils.to_lower = None, prefix: str = None
    ):
        """
        This command manages the server's prefix

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or reset
        prefix: :class:`str` optional
            The prefix to set if the option set is chosen
        """
        await self.handle_prefix(ctx, option, prefix)

    @slash_command(
        name="prefix",
        description="Manages the server's prefix",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_prefix_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command manages the server's prefix

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_prefix_slash_group.sub_command(
        name="display",
        description="Displays the current server's prefix",
    )
    async def config_prefix_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command display the current server's prefix

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prefix(inter)

    @config_prefix_slash_group.sub_command(
        name="set",
        description="Sets the current server's prefix",
    )
    async def config_prefix_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        prefix: str,
    ):
        """
        This slash command display the current server's prefix

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        prefix: :class:`str`
            The new prefix to set
        """
        await self.handle_prefix(inter, "set", prefix)

    @config_prefix_slash_group.sub_command(
        name="reset",
        description="Reset the current server's prefix (o!)",
    )
    async def config_prefix_reset_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command reset the current server's prefix (o!)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prefix(inter, "reset")

    async def handle_prefix(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        prefix: str = None,
    ):
        if option:
            try:
                if option == "set":
                    if not prefix:
                        raise MissingRequiredArgument(
                            param=Parameter(name="prefix", kind=Parameter.KEYWORD_ONLY)
                        )

                    self.bot.config_repo.set_prefix(source.guild.id, prefix)
                    self.bot.configs[source.guild.id]["prefix"] = prefix

                    if isinstance(source, Context):
                        await source.send(f"ℹ️ - Bot prefix updated to `{prefix}`.")
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Bot prefix updated to `{prefix}`."
                        )
                elif option == "reset":
                    self.bot.config_repo.set_prefix(source.guild.id)
                    self.bot.configs[source.guild.id]["prefix"] = "o!"

                    if isinstance(source, Context):
                        await source.send(f"ℹ️ - Bot prefix has been reset to `o!`.")
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Bot prefix has been reset to `o!`."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'resetting the prefix' if option == 'reset' else f'setting the prefix to `{prefix}`'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                msg = await source.send(
                    f"ℹ️ - {source.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(source.author)[0]}`!"
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(source.author)[0]}`!"
                )
                msg = await source.original_message()

            try:
                await msg.add_reaction("👀")
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to add reactions in the channel {source.channel.mention} (message: {msg.jump_url}, reaction: 👀)! Required perms: `{', '.join(['ADD_REACTIONS'])}`"
                raise

    """ TICKETS """

    @config_group.command(
        pass_context=True,
        name="tickets",
        aliases=["ticket"],
        brief="📥",
        description="Manages the server's tickets channel and category",
        usage="(on|update|resolve|off) (#channel) (#category)",
    )
    async def config_tickets_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        tickets_channel: Union[TextChannel, CategoryChannel] = None,
        tickets_category: CategoryChannel = None,
    ):
        """
        This command manages the server's tickets channel and category

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> on or update or resolve or off
        tickets_channel: :class:`typing.Union[disnake.TextChannel, disnake.CategoryChannel]` optional
            The tickets channel or category passed (is accepted if the option is on or update)
        tickets_category: :class:`disnake.CategoryChannel` optional
            The tickets category
        """
        await self.handle_tickets(ctx, option, tickets_channel, tickets_category)

    @slash_command(
        name="tickets",
        description="Manages the server's tickets channel and category",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_tickets_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's tickets channel and category

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_tickets_slash_command.sub_command(
        name="display",
        description="Displays the state of the server's tickets feature",
    )
    async def config_tickets_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the state of the server's tickets feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_tickets(inter)

    @config_tickets_slash_command.sub_command(
        name="on",
        description="Turns the server's tickets feature on",
    )
    async def config_tickets_on_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        tickets_channel: TextChannel,
        tickets_category: CategoryChannel,
    ):
        """
        This slash command turns the server's tickets feature on

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        tickets_channel: :class:`disnake.TextChannel` optional
            The channel where the ticket message will be sent
        tickets_category: :class:`disnake.CategoryChannel` optional
            The category where the tickets channels will be created
        """
        await self.handle_tickets(inter, "on", tickets_channel, tickets_category)

    @config_tickets_slash_command.sub_command(
        name="update",
        description="Updates the server's tickets feature",
    )
    async def config_tickets_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        tickets_channel: TextChannel = None,
        tickets_category: CategoryChannel = None,
    ):
        """
        This slash command updates the server's tickets feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        tickets_channel: :class:`disnake.TextChannel` optional
            The channel where the ticket message will be sent
        tickets_category: :class:`disnake.CategoryChannel` optional
            The category where the tickets channels will be created
        """
        if not tickets_channel and tickets_category:
            tickets_channel = tickets_category
            tickets_category = None

        await self.handle_tickets(inter, "update", tickets_channel, tickets_category)

    @config_tickets_slash_command.sub_command(
        name="resolve",
        description="Resolves the server's tickets feature",
    )
    async def config_tickets_resolve_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command resolves the server's tickets feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_tickets(inter, "resolve")

    @config_tickets_slash_command.sub_command(
        name="off",
        description="Turns the server's tickets feature off",
    )
    async def config_tickets_off_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command turns the server's tickets feature off

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_tickets(inter, "off")

    async def handle_tickets(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        tickets_channel: Union[TextChannel, CategoryChannel] = None,
        tickets_category: CategoryChannel = None,
    ):
        if option:
            try:
                val = False
                if option in ("on", "update", "resolve"):
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "tickets" in self.bot.configs[source.guild.id]
                ) == val and option not in ("update", "resolve"):
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The tickets are already set to `{BOOL2VAL[val]}`!"
                            + (
                                " Parameters: "
                                + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                                + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                                if "tickets" in self.bot.configs[source.guild.id]
                                else ""
                            )
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The tickets are already set to `{BOOL2VAL[val]}`!"
                            + (
                                " Parameters: "
                                + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                                + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                                if "tickets" in self.bot.configs[source.guild.id]
                                else ""
                            )
                        )

                if val:
                    if "tickets" not in self.bot.configs[
                        source.guild.id
                    ] and option in (
                        "update",
                        "resolve",
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The tickets are set to `OFF`! Please activate them before {'updating' if option == 'update' else 'resolving'}."
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The tickets are set to `OFF`! Please activate them before {'updating' if option == 'update' else 'resolving'}."
                            )
                    elif option == "resolve":
                        if (
                            "tickets_channel"
                            not in self.bot.configs[source.guild.id]["tickets"]
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - There is no tickets_channel configure! Please configure one before resolving."
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - There is no tickets_channel configure! Please configure one before resolving."
                                )

                        if [
                            m
                            for m in set(
                                await self.bot.configs[source.guild.id]["tickets"][
                                    "tickets_channel"
                                ]
                                .history(limit=10)
                                .flatten()
                            )
                            if m.author.id == self.bot.user.id
                        ]:
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - There is no need for the ticket message to be resolved."
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - There is no need for the ticket message to be resolved."
                                )

                        tickets_channel = self.bot.configs[source.guild.id]["tickets"][
                            "tickets_channel"
                        ]
                    elif not tickets_channel:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="tickets_channel", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif option != "update" and isinstance(
                        tickets_channel, CategoryChannel
                    ):
                        raise BadArgument
                    elif not tickets_category and option != "update":
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="tickets_category", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    if option == "update":
                        self.bot.config_repo.set_tickets(
                            source.guild.id,
                            val,
                            tickets_channel.id
                            if isinstance(tickets_channel, TextChannel)
                            else self.bot.configs[source.guild.id]["tickets"][
                                "tickets_channel"
                            ].id,
                            tickets_channel.id
                            if isinstance(tickets_channel, CategoryChannel)
                            else tickets_category
                            if isinstance(tickets_channel, CategoryChannel)
                            else self.bot.configs[source.guild.id]["tickets"][
                                "tickets_category"
                            ].id,
                        )

                        if isinstance(tickets_channel, TextChannel):
                            perms = self.bot.configs[source.guild.id]["tickets"][
                                "tickets_channel"
                            ].permissions_for(source.guild.me)

                            if perms.read_message_history and perms.manage_messages:
                                await self.bot.configs[source.guild.id]["tickets"][
                                    "tickets_channel"
                                ].purge(check=lambda m: m.author.id == self.bot.user.id)
                            else:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention}! Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                                    source.guild.id,
                                )

                        self.bot.configs[source.guild.id]["tickets"] = {
                            "tickets_channel": tickets_channel
                            if isinstance(tickets_channel, TextChannel)
                            else self.bot.configs[source.guild.id]["tickets"][
                                "tickets_channel"
                            ],
                            "tickets_category": tickets_channel
                            if isinstance(tickets_channel, CategoryChannel)
                            else tickets_category
                            if isinstance(tickets_channel, CategoryChannel)
                            else self.bot.configs[source.guild.id]["tickets"][
                                "tickets_category"
                            ],
                        }

                    elif option != "resolve":
                        self.bot.config_repo.set_tickets(
                            source.guild.id,
                            val,
                            tickets_channel.id,
                            tickets_category.id,
                        )
                        self.bot.configs[source.guild.id]["tickets"] = {
                            "tickets_channel": tickets_channel,
                            "tickets_category": tickets_category,
                        }

                    if isinstance(tickets_channel, TextChannel):
                        em = Embed(
                            colour=self.bot.color,
                            title="📥 - Ticket",
                            description="**To create a ticket please click on the button 📥**\n\nAfter clicking on the button, a private room will be created at the bottom of the ticket category.\n\nYou can only create one ticket at a time.",
                        )

                        if source.guild.icon:
                            em.set_thumbnail(url=source.guild.icon.url)

                        if self.bot.user.avatar:
                            em.set_footer(
                                text=self.bot.user.name,
                                icon_url=self.bot.user.avatar.url,
                            )
                        else:
                            em.set_footer(text=self.bot.user.name)

                        if (
                            self.bot.configs[source.guild.id]["tickets"][
                                "tickets_channel"
                            ]
                            .permissions_for(source.guild.me)
                            .send_messages
                        ):
                            view = View(timeout=None)
                            view.add_item(
                                Button(
                                    style=ButtonStyle.primary,
                                    emoji="📥",
                                    custom_id=f"{self.bot.configs[source.guild.id]['tickets']['tickets_channel'].id}.ticket_create",
                                )
                            )
                            await self.bot.configs[source.guild.id]["tickets"][
                                "tickets_channel"
                            ].send(
                                embed=em,
                                view=view,
                            )
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention} (i tried to send the message that allow users to create tickets so please reactivate this feature after changing the permissions)! Required perms: `{', '.join(['SEND_MESSAGE'])}`",
                                source.guild.id,
                            )
                else:
                    perms = self.bot.configs[source.guild.id]["tickets"][
                        "tickets_channel"
                    ].permissions_for(source.guild.me)

                    if perms.read_message_history and perms.manage_messages:
                        await self.bot.configs[source.guild.id]["tickets"][
                            "tickets_channel"
                        ].purge(check=lambda m: m.author.id == self.bot.user.id)
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention}! Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                            source.guild.id,
                        )

                    channels = set(
                        self.bot.configs[source.guild.id]["tickets"][
                            "tickets_category"
                        ].channels
                    )

                    if (
                        self.bot.configs[source.guild.id]["tickets"]["tickets_category"]
                        .permissions_for(source.guild.me)
                        .manage_channels
                    ):

                        for channel in channels:
                            await channel.delete(
                                reason=f"Tickets turned off by {source.author}!"
                            )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to delete channels from the category {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention}! Required perms: `{', '.join(['MANAGE_CHANNELS'])}`",
                            source.guild.id,
                        )

                    self.bot.ticket_repo.purge_tickets(source.guild.id)
                    self.bot.config_repo.remove_tickets(source.guild.id)
                    del self.bot.configs[source.guild.id]["tickets"]

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The tickets are now `{BOOL2VAL[val] if option not in ('update', 'resolve') else ('UPDATED' if option == 'update' else 'RESOLVED')}` in this guild!"
                        + (
                            " Parameters: "
                            + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                            + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                            if "tickets" in self.bot.configs[source.guild.id]
                            and option != "resolve"
                            else ""
                        )
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The tickets are now `{BOOL2VAL[val] if option not in ('update', 'resolve') else ('UPDATED' if option == 'update' else 'RESOLVED')}` in this guild!"
                        + (
                            " Parameters: "
                            + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                            + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                            if "tickets" in self.bot.configs[source.guild.id]
                            and option != "resolve"
                            else ""
                        )
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {f'setting the tickets `{BOOL2VAL[val]}`' if option != 'update' else 'updating the tickets'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {source.author.mention} - The tickets are currently `{BOOL2VAL['tickets' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + (
                        " Parameters: "
                        + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                        + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                        if "tickets" in self.bot.configs[source.guild.id]
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The tickets are currently `{BOOL2VAL['tickets' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + (
                        " Parameters: "
                        + f"\n'tickets_channel': {self.bot.configs[source.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[source.guild.id]['tickets'] else '`No channel specified.`'}"
                        + f"\n'tickets_category': {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[source.guild.id]['tickets'] else '`No category specified.`'}"
                        if "tickets" in self.bot.configs[source.guild.id]
                        else ""
                    )
                )

    """ SELECT TO ROLE """

    @config_group.command(
        pass_context=True,
        name="select_to_role",
        aliases=["select_2_role", "select2role"],
        brief="🥸",
        description="Manages the server's select_2_role feature",
        usage='(add|update|resolve|remove|purge "Title" @role <"description">)',
    )
    async def config_select_2_role_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        title: str = None,
        role: Role = None,
        *,
        description: str = "",
    ):
        """
        This command manages the server's select_2_role feature

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or update or resolve or remove or purge
        title: :class:`str` optional
            The title of the choice
        role: :class:`disnake.Role` optional
            The role that is attached to the title
        description: :class:`str` optional
            The description of the role/title
        """
        await self.handle_select_to_role(ctx, option, title, role, description)

    @slash_command(
        name="select_to_role",
        description="Manages the server's select_2_role feature",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_select_2_role_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's select_2_role feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_select_2_role_slash_group.sub_command(
        name="list",
        description="Lists all the select to roles",
    )
    async def config_select_2_role_list_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command lists all the select to roles

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_select_to_role(inter)

    @config_select_2_role_slash_group.sub_command(
        name="add",
        description="Adds a new select to role",
    )
    async def config_select_2_role_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        title: str,
        role: Role,
        description: str,
    ):
        """
        This slash command adds a new select to role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        title: :class:`str`
            The title of the choice
        role: :class:`disnake.Role`
            The role that is attached to the title
        description: :class:`str`
            The description of the role/title
        """
        await self.handle_select_to_role(inter, "add", title, role, description)

    @config_select_2_role_slash_group.sub_command(
        name="update",
        description="Updates a select to role",
    )
    async def config_select_2_role_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        title: str,
        role: Role = None,
        description: str = "",
    ):
        """
        This slash command updates a select to role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        title: :class:`str`
            The title of the choice
        role: :class:`disnake.Role` optional
            The new role that is attached to the title (if empty nothing's changed)
        description: :class:`str` optional
            The new description of the role/title (if empty nothing's changed)
        """
        await self.handle_select_to_role(inter, "update", title, role, description)

    @config_select_2_role_slash_group.sub_command(
        name="resolve",
        description="Resolves the select to role feature",
    )
    async def config_select_2_role_resolve_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command resolves the select to role feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_select_to_role(inter, "resolve")

    @config_select_2_role_slash_group.sub_command(
        name="remove",
        description="Removes a select to role",
    )
    async def config_select_2_role_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        title: str,
    ):
        """
        This slash command removes a select to role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        title: :class:`str`
            The title of the choice to remove
        """
        await self.handle_select_to_role(inter, "remove", title)

    @config_select_2_role_slash_group.sub_command(
        name="purge",
        description="Purges the select to role feature",
    )
    async def config_select_2_role_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the select to role feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_select_to_role(inter, "purge")

    async def handle_select_to_role(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        title: str = None,
        role: Role = None,
        description: str = None,
    ):
        if option:
            try:
                if option in ("add", "update", "remove"):
                    if not title:
                        raise MissingRequiredArgument(
                            param=Parameter(name="title", kind=Parameter.KEYWORD_ONLY)
                        )

                    if option == "add" or option == "update":
                        if not role:
                            raise MissingRequiredArgument(
                                param=Parameter(
                                    name="role", kind=Parameter.KEYWORD_ONLY
                                )
                            )

                        if (
                            "select2role" in self.bot.configs[source.guild.id]
                            and "selects"
                            in self.bot.configs[source.guild.id]["select2role"]
                            and title
                            in set(
                                self.bot.configs[source.guild.id]["select2role"][
                                    "selects"
                                ]
                            )
                            and option != "update"
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - The title `{title}` is already assigned to a role! Value: `@{self.bot.configs[source.guild.id]['select2role']['selects'][title]}`",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - The title `{title}` is already assigned to a role! Value: `@{self.bot.configs[source.guild.id]['select2role']['selects'][title]}`",
                                    ephemeral=True,
                                )
                        elif await self.check_role_duplicates(source, role):
                            return

                        self.bot.config_repo.add_select2role(
                            source.guild.id, title, f"{role}", role.id, description
                        )

                        if "select2role" not in self.bot.configs[source.guild.id]:
                            self.bot.configs[source.guild.id]["select2role"] = {
                                "selects": {}
                            }
                        elif (
                            "selects"
                            not in self.bot.configs[source.guild.id]["select2role"]
                        ):
                            self.bot.configs[source.guild.id]["select2role"][
                                "selects"
                            ] = {}

                        self.bot.configs[source.guild.id]["select2role"]["selects"][
                            title
                        ] = {"role": role, "description": description}

                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the title `{title}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the select to role list."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the title `{title}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the select to role list."
                            )
                    elif option == "remove":
                        if (
                            "select2role" not in self.bot.configs[source.guild.id]
                            or "selects"
                            not in self.bot.configs[source.guild.id]["select2role"]
                            or title
                            not in set(
                                self.bot.configs[source.guild.id]["select2role"][
                                    "selects"
                                ]
                            )
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - The title `{title}` is already not in the select to role list!",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - The title `{title}` is already not in the select to role list!",
                                    ephemeral=True,
                                )

                        self.bot.config_repo.remove_select2role(source.guild.id, title)
                        role = self.bot.configs[source.guild.id]["select2role"][
                            "selects"
                        ].pop(title)

                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - Removed the title `{title}` which was corresponding to the role `@{role}` from the select to role list."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - Removed the title `{title}` which was corresponding to the role `@{role}` from the select to role list."
                            )

                        if not self.bot.configs[source.guild.id]["select2role"][
                            "selects"
                        ]:
                            del self.bot.configs[source.guild.id]["select2role"][
                                "selects"
                            ]

                        members = set(source.guild.members)
                        if source.channel.permissions_for(source.guild.me).manage_roles:
                            for member in members:
                                if member.bot or role not in member.roles:
                                    continue

                                try:
                                    await member.remove_roles(role)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove this role `@{role.name}` from {member} (maybe the role is above mine)"
                                    raise
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to manage this role `@{role.name}` (i tried to remove the old select to role role from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                                source.guild.id,
                            )
                elif option == "resolve":
                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Resolved the select2role message successfully."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Resolved the select2role message successfully."
                        )
                elif option == "purge":
                    if (
                        "select2role" not in self.bot.configs[source.guild.id]
                        or "selects"
                        not in self.bot.configs[source.guild.id]["select2role"]
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The select to role list is already empty!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The select to role list is already empty!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_select2role(source.guild.id)
                    roles = set(
                        self.bot.configs[source.guild.id]["select2role"][
                            "selects"
                        ].values()
                    )
                    del self.bot.configs[source.guild.id]["select2role"]["selects"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the titles from the select to role list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the titles from the select to role list."
                        )

                    members = set(source.guild.members)

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        for member in members:
                            if member.bot or not roles & set(member.roles):
                                continue

                            try:
                                await member.remove_roles(*roles)
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in roles])} from {member} (maybe one of them is above mine)"
                                raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{role.name}` (i tried to remove the old level role from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if "channel" in self.bot.configs[source.guild.id]["select2role"]:
                    roles_msg = None

                    if (
                        "roles_msg_id"
                        in self.bot.configs[source.guild.id]["select2role"]
                    ):
                        try:
                            roles_msg = await self.bot.configs[source.guild.id][
                                "select2role"
                            ]["channel"].fetch_message(
                                self.bot.configs[source.guild.id]["select2role"][
                                    "roles_msg_id"
                                ]
                            )
                        except NotFound:
                            perms = self.bot.configs[source.guild.id]["select2role"][
                                "channel"
                            ].permissions_for(source.guild.me)
                            if perms.read_message_history and perms.manage_messages:
                                await self.bot.configs[source.guild.id]["select2role"][
                                    "channel"
                                ].purge(check=lambda m: m.author.id == self.bot.user.id)
                            else:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to purge messages in the (select_to_role) channel {self.bot.configs[source.guild.id]['select2role']['channel'].mention}! Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                                    source.guild.id,
                                )
                            pass

                    em = Embed(
                        colour=self.bot.color,
                        title="Roles",
                        description="Here are the server's select to role available, choose one or more roles you wish to be assigned.\n\n**If you want the role to be removed, deselect the corresponding role!**",
                    )

                    if source.guild.icon:
                        em.set_thumbnail(url=source.guild.icon.url)

                    if self.bot.user.avatar:
                        em.set_footer(
                            text=self.bot.user.name, icon_url=self.bot.user.avatar.url
                        )
                    else:
                        em.set_footer(text=self.bot.user.name)

                    em.set_author(
                        name=source.guild.name,
                        icon_url=source.guild.icon.url if source.guild.icon else None,
                    )

                    options = []
                    if (
                        "select2role" in self.bot.configs[source.guild.id]
                        and "selects"
                        in self.bot.configs[source.guild.id]["select2role"]
                    ):
                        values = []
                        for title, value in self.bot.configs[source.guild.id][
                            "select2role"
                        ]["selects"].items():
                            values.append(f"{title}: `@{value['role'].name}`")

                            options.append(
                                SelectOption(
                                    label=title,
                                    description=value["description"],
                                    value=title,
                                    default=False,
                                )
                            )

                        em.add_field(
                            name="Available roles:",
                            value="\n".join(values),
                        )
                    else:
                        em.add_field(
                            name="Information", value="For now no roles are available!"
                        )

                    view = None

                    if options:
                        view = View(timeout=None)
                        view.add_item(
                            Select(
                                options=options,
                                custom_id=f"{self.bot.configs[source.guild.id]['select2role']['channel'].id}",
                                placeholder="Choose one or more role!",
                                min_values=0,
                                max_values=len(options),
                            )
                        )

                    if roles_msg:
                        await roles_msg.edit(
                            embed=em,
                            view=view,
                        )
                    else:
                        if (
                            self.bot.configs[source.guild.id]["select2role"]["channel"]
                            .permissions_for(source.guild.me)
                            .send_messages
                        ):
                            self.bot.configs[source.guild.id]["select2role"][
                                "roles_msg_id"
                            ] = (
                                await self.bot.configs[source.guild.id]["select2role"][
                                    "channel"
                                ].send(embed=em, view=view)
                            ).id
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[source.guild.id]['select2role']['channel'].mention} (i tried to send the message that allow users to select a role so please reactivate this feature after changing the permissions)! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                source.guild.id,
                            )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except Forbidden as f:
                raise f
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the value `{title}` {'to' if option != 'update' else 'from'} the select to role message! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if (
                "select2role" not in self.bot.configs[source.guild.id]
                or "selects" not in self.bot.configs[source.guild.id]["select2role"]
            ):
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No select to role have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No select to role have been added to the list yet!",
                        ephemeral=True,
                    )

            server_select_2_role = self.bot.configs[source.guild.id]["select2role"][
                "selects"
            ]
            roles_mess = ""
            for key in sorted(server_select_2_role):
                roles_mess += (
                    f"`{key}` => `@{server_select_2_role[key]['role']}`"
                    + (
                        f", description = `{server_select_2_role[key]['description']}`"
                        if server_select_2_role[key]["description"]
                        else ""
                    )
                    + "\n"
                )

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's select to role:**\n\n{roles_mess}"
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's select to role:**\n\n{roles_mess}"
                )

    """ MUTED ROLE """

    @config_group.command(
        pass_context=True,
        name="muted_role",
        aliases=["mute_role"],
        brief="🤐",
        description="Manages the server's muted role",
        usage="(set|remove @role)",
    )
    async def config_muted_role_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        muted: Role = None,
    ):
        """
        This command manages the server's muted role

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        muted: :class:`disnake.Role` optional
            The muted role
        """
        await self.handle_muted_role(ctx, option, muted)

    @slash_command(
        name="muted_role",
        description="Manages the server's muted role",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def config_muted_role_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's muted role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_muted_role_slash_group.sub_command(
        name="display",
        description="Displays the server's muted role",
    )
    async def config_muted_role_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's muted role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_muted_role(inter)

    @config_muted_role_slash_group.sub_command(
        name="set",
        description="Sets the server's muted role",
    )
    async def config_muted_role_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        role: Role,
    ):
        """
        This slash command sets the server's muted role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        role: :class:`disnake.Role`
            The muted role
        """
        await self.handle_muted_role(inter, "set", role)

    @config_muted_role_slash_group.sub_command(
        name="remove",
        description="Removes the server's muted role",
    )
    async def config_muted_role_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command removes the server's muted role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_muted_role(inter, "remove")

    async def handle_muted_role(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        muted: Role = None,
    ):
        if option:
            try:
                if option == "set":
                    if not muted:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="muted_role", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif await self.check_role_duplicates(source, muted):
                        return

                    old_role = None
                    if "muted_role" in self.bot.configs[source.guild.id]:
                        old_role = self.bot.configs[source.guild.id]["muted_role"]

                    self.bot.config_repo.set_muted_role(source.guild.id, muted.id)
                    self.bot.configs[source.guild.id]["muted_role"] = muted

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The muted role is now `@{muted}` in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The muted role is now `@{muted}` in this guild!"
                        )

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        db_users = self.bot.user_repo.get_users(source.guild.id)

                        for db_user in db_users.values():
                            if db_user["muted"]:
                                try:
                                    member = source.guild.get_member(
                                        int(db_user["id"])
                                    ) or await source.guild.fetch_member(
                                        int(db_user["id"])
                                    )
                                except NotFound:
                                    continue

                                if old_role:
                                    try:
                                        if old_role in member.roles:
                                            await member.remove_roles(old_role)
                                    except Forbidden as f:
                                        f.text = f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)"
                                        raise

                                try:
                                    await member.add_roles(muted)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to add the role `{muted}` to {member} (maybe the role is above mine)"
                                    raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles {f'`@{old_role.name}` ' if old_role else ''}`@{muted.name}` (i tried to replace the old muted role with the new one from muted members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                elif option == "remove":
                    if "muted_role" not in self.bot.configs[source.guild.id]:
                        return await source.reply(
                            f"ℹ️ - The server already doesn't have a muted role configured!",
                            delete_after=20,
                        )

                    old_role = self.bot.configs[source.guild.id]["muted_role"]
                    self.bot.config_repo.set_muted_role(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["muted_role"]
                    msg = f"ℹ️ - The muted role is now removed from this guild!"

                    if "mute_on_join" in self.bot.configs[source.guild.id]:
                        self.bot.config_repo.remove_mute_on_join(source.guild.id)
                        del self.bot.configs[source.guild.id]["mute_on_join"]
                        msg += "\nThe mute_on_join feature was activated, therefore it is now set to off!"

                    if isinstance(source, Context):
                        await source.send(msg)
                    else:
                        await source.response.send_message(msg)

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        db_users = self.bot.user_repo.get_users(source.guild.id)

                        for db_user in db_users.values():
                            if db_user["muted"]:
                                try:
                                    member = source.guild.get_member(
                                        int(db_user["id"])
                                    ) or await source.guild.fetch_member(
                                        int(db_user["id"])
                                    )
                                except NotFound:
                                    continue

                                try:
                                    if old_role in member.roles:
                                        await member.remove_roles(*old_role)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)"
                                    raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{old_role.name}` (i tried to remove the old muted role from muted members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except Forbidden as f:
                raise f
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while configuring the muted_role! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - The current server's muted role is: `@{self.bot.configs[source.guild.id]['muted_role']}`"
                    if "muted_role" in self.bot.configs[source.guild.id]
                    else f"ℹ️ - The server doesn't have a muted role yet!"
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - The current server's muted role is: `@{self.bot.configs[source.guild.id]['muted_role']}`"
                    if "muted_role" in self.bot.configs[source.guild.id]
                    else f"ℹ️ - The server doesn't have a muted role yet!"
                )

    """ MAIN GROUP'S SECURITY COMMAND(S) """

    """ PREVENT INVITES """

    @config_security_group.command(
        pass_context=True,
        name="prevent_invites",
        aliases=["prev_i"],
        brief="✉️",
        description="Manages if users are allowed to send other servers invites or not (specify a channel to be notified when someone tries to send an invitation link)",
        usage="(on|update|off) (#channel)",
    )
    async def config_security_prevent_invites_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        notify_channel: TextChannel = None,
    ):
        """
        This command manages if users are allowed to send other servers invites or not (specify a channel to be notified when someone tries to send an invitation link)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> on or update or off
        notify_channel: :class:`disnake.TextChannel` optional
            The channel where the events will be sent
        """
        await self.handle_prevent_invites(ctx, option, notify_channel)

    @config_security_slash_group.sub_command_group(
        name="prevent_invites",
        description="Manages the server's prevent invites feature",
    )
    async def config_security_prevent_invites_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's prevent invites feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_security_prevent_invites_slash_group.sub_command(
        name="display",
        description="Displays the state of the server's prevent invites feature",
    )
    async def config_security_prevent_invites_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the state of the server's prevent invites feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prevent_invites(inter)

    @config_security_prevent_invites_slash_group.sub_command(
        name="on",
        description="Turns the server's prevent invites feature on",
    )
    async def config_security_prevent_invites_on_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        notify_channel: TextChannel = None,
    ):
        """
        This slash command turns the server's prevent invites feature on

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        notify_channel: :class:`disnake.TextChannel` optional
            The channel where the events will be sent
        """
        await self.handle_prevent_invites(inter, "on", notify_channel)

    @config_security_prevent_invites_slash_group.sub_command(
        name="update",
        description="Updates the server's prevent invites feature",
    )
    async def config_security_prevent_invites_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        notify_channel: TextChannel,
    ):
        """
        This slash command updates the server's prevent invites feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        notify_channel: :class:`disnake.TextChannel`
            The channel where the events will be sent
        """
        await self.handle_prevent_invites(inter, "update", notify_channel)

    @config_security_prevent_invites_slash_group.sub_command(
        name="off",
        description="Turns the server's prevent invites feature off",
    )
    async def config_security_prevent_invites_off_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command turns the server's prevent invites feature off

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prevent_invites(inter, "off")

    async def handle_prevent_invites(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        notify_channel: TextChannel = None,
    ):
        if option:
            try:
                val = False
                if option in ("on", "update"):
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "prevent_invites" in self.bot.configs[source.guild.id]
                ) == val and option != "update":
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The invites prevention is already set to `{BOOL2VAL[val]}`!"
                            + f" Parameters: 'notify_channel': {self.bot.configs[source.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                            if "prevent_invites" in self.bot.configs[source.guild.id]
                            else ""
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The invites prevention is already set to `{BOOL2VAL[val]}`!"
                            + f" Parameters: 'notify_channel': {self.bot.configs[source.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                            if "prevent_invites" in self.bot.configs[source.guild.id]
                            else ""
                        )

                if val:
                    self.bot.config_repo.set_invite_prevention(
                        source.guild.id, notify_channel.id if notify_channel else None
                    )
                    self.bot.configs[source.guild.id]["prevent_invites"] = {
                        "is_on": True
                    }

                    if notify_channel:
                        self.bot.configs[source.guild.id]["prevent_invites"][
                            "notify_channel"
                        ] = notify_channel
                else:
                    self.bot.config_repo.remove_invite_prevention(source.guild.id)
                    del self.bot.configs[source.guild.id]["prevent_invites"]

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The invites prevention is now `{BOOL2VAL[val] if option != 'update' else 'UPDATED'}` in this guild!"
                        + (
                            f" Parameters: 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
                            if val
                            else ""
                        )
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The invites prevention is now `{BOOL2VAL[val] if option != 'update' else 'UPDATED'}` in this guild!"
                        + (
                            f" Parameters: 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
                            if val
                            else ""
                        )
                    )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {f'setting the invites prevention `{BOOL2VAL[val]}`' if option != 'update' else 'updating the invites prevention'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {source.author.mention} - The invites prevention is currently `{BOOL2VAL['prevent_invites' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + f" Parameters: 'notify_channel': {self.bot.configs[source.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                    if "prevent_invites" in self.bot.configs[source.guild.id]
                    else ""
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The invites prevention is currently `{BOOL2VAL['prevent_invites' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + f" Parameters: 'notify_channel': {self.bot.configs[source.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                    if "prevent_invites" in self.bot.configs[source.guild.id]
                    else ""
                )

    """ MUTED ON JOIN """

    @config_security_group.command(
        pass_context=True,
        name="mute_on_join",
        aliases=["m_on_j"],
        brief="🔇",
        description="Manages if users are muted during a certain amount of time when joining the server and then notify it at the end if a channel is specified! (default duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
        usage="(on|update|off) (<duration_value> <duration_type> #channel)",
    )
    async def config_security_mute_on_join_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        duration: int = None,
        duration_type: str = None,
        notify_channel: TextChannel = None,
    ):
        """
        This command manages if users are muted during a certain amount of time when joining the server and then notify it at the end if a channel is specified! (default duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> on or update or off
        duration: :class:`int` optional
            The mute's duration value
        duration_type: :class:`Utils.to_lower` optional
            The mute's duration type (d == days, h == hours, m == minutes, s == seconds)
        notify_channel: :class:`disnake.TextChannel` optional
            The channel where the events will be sent
        """
        await self.handle_mute_on_join(
            ctx, option, duration, duration_type, notify_channel
        )

    @config_security_slash_group.sub_command_group(
        name="mute_on_join",
        description="Manages the server's mute_on_join feature",
    )
    async def config_security_mute_on_join_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's mute_on_join feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_security_mute_on_join_slash_group.sub_command(
        name="display",
        description="Displays the state of the mute on join feature",
    )
    async def config_security_mute_on_join_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the state of the mute on join feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_mute_on_join(inter)

    @config_security_mute_on_join_slash_group.sub_command(
        name="on",
        description="Turns the mute on join feature on (default duration = 10 min)",
    )
    async def config_security_mute_on_join_on_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        duration: int = 10,
        duration_type: DurationType = "m",
        notify_channel: TextChannel = None,
    ):
        """
        This slash command turns the mute on join feature on (default duration = 10 min)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        duration: :class:`int` optional
            The mute's duration value (default: 10)
        duration_type: :class:`Utils.DurationType` optional
            The mute's duration type (d == days, h == hours, m == minutes, s == seconds) (default: "m")
        notify_channel: :class:`disnake.TextChannel` optional
            The channel where the events will be sent
        """
        await self.handle_mute_on_join(
            inter, "on", duration, duration_type, notify_channel
        )

    @config_security_mute_on_join_slash_group.sub_command(
        name="update",
        description="Updates the mute on join feature",
    )
    async def config_security_mute_on_join_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        duration: int = None,
        duration_type: DurationType = None,
        notify_channel: TextChannel = None,
    ):
        """
        This slash command updates the mute on join feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        duration: :class:`int` optional
            The mute's duration value
        duration_type: :class:`Utils.DurationType` optional
            The mute's duration type (d == days, h == hours, m == minutes, s == seconds)
        notify_channel: :class:`disnake.TextChannel` optional
            The channel where the events will be sent
        """
        await self.handle_mute_on_join(
            inter, "update", duration, duration_type, notify_channel
        )

    @config_security_mute_on_join_slash_group.sub_command(
        name="off",
        description="Turns the mute on join feature off",
    )
    async def config_security_mute_on_join_off_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command turns the mute on join feature off

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_mute_on_join(inter, "off")

    async def handle_mute_on_join(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        _duration: int = None,
        duration_type: str = None,
        notify_channel: TextChannel = None,
    ):
        if "muted_role" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.author)[0]}config muted_role` to set one!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(source.author)[0]}config muted_role` to set one!",
                    ephemeral=True,
                )

        if option:
            try:
                val = False
                if option in ("on", "update"):
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "mute_on_join" in self.bot.configs[source.guild.id]
                ) == val and option != "update":
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The mute on join is already `{BOOL2VAL[val]}`!"
                            + (
                                f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[source.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[source.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                                if "mute_on_join" in self.bot.configs[source.guild.id]
                                else ""
                            ),
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The mute on join is already `{BOOL2VAL[val]}`!"
                            + (
                                f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[source.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[source.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                                if "mute_on_join" in self.bot.configs[source.guild.id]
                                else ""
                            ),
                            ephemeral=True,
                        )

                if val:
                    if not _duration:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="duration", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif not duration_type:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="duration_type", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    old_duration = f"{_duration} {duration_type}"
                    _duration = await self.bot.utils_class.parse_duration(
                        _duration, duration_type, source
                    )
                    if not _duration:
                        return

                    self.bot.config_repo.set_mute_on_join(
                        source.guild.id,
                        _duration,
                        notify_channel.id if notify_channel else None,
                    )
                    self.bot.configs[source.guild.id]["mute_on_join"] = {
                        "duration": _duration,
                    }

                    if notify_channel:
                        self.bot.configs[source.guild.id]["mute_on_join"][
                            "notify_channel"
                        ] = notify_channel
                else:
                    self.bot.config_repo.remove_mute_on_join(source.guild.id)
                    del self.bot.configs[source.guild.id]["mute_on_join"]

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The mute on join is now `{BOOL2VAL[val] if option != 'update' else 'UPDATED'}` in this guild!"
                        + (
                            f" Parameters: 'duration': `{old_duration}`, 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
                            if val
                            else ""
                        )
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The mute on join is now `{BOOL2VAL[val] if option != 'update' else 'UPDATED'}` in this guild!"
                        + (
                            f" Parameters: 'duration': `{old_duration}`, 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
                            if val
                            else ""
                        )
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {f'setting the mute on join `{BOOL2VAL[val]}`' if option != 'update' else 'updating the mute on join'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {source.author.mention} - The mute on join is currently `{BOOL2VAL['mute_on_join' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + (
                        f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[source.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[source.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                        if "mute_on_join" in self.bot.configs[source.guild.id]
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The mute on join is currently `{BOOL2VAL['mute_on_join' in self.bot.configs[source.guild.id]]}` in this guild!"
                    + (
                        f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[source.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[source.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[source.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                        if "mute_on_join" in self.bot.configs[source.guild.id]
                        else ""
                    )
                )

    """ MAIN GROUP'S XP COMMAND(S) """

    """ SWITCH """

    @config_xp_group.command(
        pass_context=True,
        name="state",
        brief="➕",
        description="Turns the server's experience feature on or off",
        usage="(on|off)",
    )
    async def config_xp_switch_command(
        self, ctx: Context, option: Utils.to_lower = None
    ):
        """
        This command turns the server's experience feature on or off

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> on or off
        """
        await self.handle_switch(ctx, option)

    @config_xp_slash_group.sub_command(
        name="state",
        description="Manages the server's experience feature",
    )
    async def config_xp_state_slash_command(
        self, inter: ApplicationCommandInteraction, option: Literal["on", "off"] = None
    ):
        """
        This slash command manages the server's experience feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        option: :class:`typing.Literal` optional
            Turns the feature on or off (if nothing's precised then it shows the feature's state )
        """
        await self.handle_switch(inter, option)

    async def handle_switch(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
    ):
        if option:
            try:
                val = False
                if option == "on":
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if self.bot.configs[source.guild.id]["xp"]["is_on"] == val:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The xp is already `{BOOL2VAL[val]}`!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The xp is already `{BOOL2VAL[val]}`!",
                            ephemeral=True,
                        )

                self.bot.config_repo.set_xp(source.guild.id, val)
                self.bot.configs[source.guild.id]["xp"]["is_on"] = val

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The xp is now `{BOOL2VAL[val]}` in this guild!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The xp is now `{BOOL2VAL[val]}` in this guild!"
                    )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while setting the xp `{BOOL2VAL[val]}`! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {source.author.mention} - The xp is currently `{BOOL2VAL[self.bot.configs[source.guild.id]['xp']['is_on']]}` in this guild!"
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The xp is currently `{BOOL2VAL[self.bot.configs[source.guild.id]['xp']['is_on']]}` in this guild!"
                )

    """ BOOST """

    @config_xp_group.command(
        pass_context=True,
        name="boost",
        aliases=["boosts", "boosted", "boosteds"],
        brief="🔋",
        description="Manages the server's boosted roles | members, you can precise what xp bonus they'll get (default = 20%)",
        usage="(add|update|remove|purge @role|@member (<bonus>))",
    )
    async def config_xp_boost_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        boosted: Snowflake = None,
        bonus: int = 20,
    ):
        """
        This command manages the server's boosted roles | members, you can precise what xp bonus they'll get (default = 20%)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`typing.Literal` optional
            The options -> add or update or remove or purge
        boosted: :class:`disnake.Snowflake` optional
            The role / member that is boosted
        bonus: :class:`int` optional
            The xp amount boosted (%) (default: 20)
        """
        await self.handle_boost(ctx, option, boosted, bonus)

    @config_xp_slash_group.sub_command_group(
        name="boost",
        description="Manages the server's boosted roles | members",
    )
    async def config_xp_boost_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command manages the server's boosted roles | members

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_xp_boost_slash_group.sub_command(
        name="display",
        description="Displays the state of the server's boosted roles | members feature",
    )
    async def config_xp_boost_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the state of the server's boosted roles | members feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_boost(inter)

    @config_xp_boost_slash_group.sub_command(
        name="add",
        description="Adds a boosted role / member to server's boosted roles|members list! (default bonus = 20%)",
    )
    async def config_xp_boost_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        boosted: Snowflake,
        bonus: int = 20,
    ):
        """
        This slash command adds a boosted role / member to server's boosted roles|members list! (default bonus = 20%)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        boosted: :class:`disnake.Snowflake`
             The role / member that will be boosted
        bonus: :class:`int` optional
            The xp amount boosted (%) (default: 20)
        """
        await self.handle_boost(inter, "add", boosted, bonus)

    @config_xp_boost_slash_group.sub_command(
        name="update",
        description="Updates a boosted role/member from the server's boosted roles | members list",
    )
    async def config_xp_boost_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        boosted: Snowflake,
        bonus: int,
    ):
        """
        This slash command updates a boosted role/member from the server's boosted roles | members list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        boosted: :class:`disnake.Snowflake`
             The role / member that is boosted
        bonus: :class:`int`
            The xp amount boosted (%) (default: 20)
        """
        await self.handle_boost(inter, "update", boosted, bonus)

    @config_xp_boost_slash_group.sub_command(
        name="remove",
        description="Removes a boosted role / member from the server's boosted roles | members list",
    )
    async def config_xp_boost_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        boosted: Snowflake,
    ):
        """
        This slash command removes a boosted role / member from the server's boosted roles | members list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        boosted: :class:`disnake.Snowflake`
             The role / member that is boosted
        """
        await self.handle_boost(inter, "remove", boosted)

    @config_xp_boost_slash_group.sub_command(
        name="purge",
        description="Purges the server's boosted roles | members list",
    )
    async def config_xp_boost_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's boosted roles | members list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_boost(inter, "purge")

    async def handle_boost(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        boosted: Snowflake = None,
        bonus: int = None,
    ):
        if option:
            try:
                if option in ("add", "update", "remove"):
                    if not boosted:
                        raise MissingRequiredArgument(
                            param=Parameter(name="boosted", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif isinstance(boosted, Member) and boosted.bot:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - You can't add a bot user to the boosted xp list!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - You can't add a bot user to the boosted xp list!",
                                ephemeral=True,
                            )

                    if option == "add" or option == "update":
                        if (
                            "boosteds" in self.bot.configs[source.guild.id]["xp"]
                            and str(boosted.id)
                            in set(self.bot.configs[source.guild.id]["xp"]["boosteds"])
                            and option != "update"
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already in the boosted xp list!",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already in the boosted xp list!",
                                    ephemeral=True,
                                )
                        elif await self.check_role_duplicates(source, boosted):
                            return

                        if bonus <= 0:
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - The bonus value must be greater than 0!",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - The bonus value must be greater than 0!",
                                    ephemeral=True,
                                )

                        self.bot.config_repo.add_xp_boosted(
                            source.guild.id,
                            boosted.id,
                            f"{boosted}",
                            bonus,
                            type(boosted).__name__,
                        )

                        if "boosteds" not in self.bot.configs[source.guild.id]["xp"]:
                            self.bot.configs[source.guild.id]["xp"]["boosteds"] = {}

                        self.bot.configs[source.guild.id]["xp"]["boosteds"][
                            str(boosted.id)
                        ] = bonus

                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option == 'add' else 'from'} the boosted xp list. Bonus: `{bonus}%`"
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option == 'add' else 'from'} the boosted xp list. Bonus: `{bonus}%`"
                            )
                    elif option == "remove":
                        if "boosteds" not in self.bot.configs[source.guild.id][
                            "xp"
                        ] or str(boosted.id) not in set(
                            self.bot.configs[source.guild.id]["xp"]["boosteds"]
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already not in the boosted xp list!",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already not in the boosted xp list!",
                                    ephemeral=True,
                                )

                        self.bot.config_repo.remove_xp_boosted(
                            source.guild.id, boosted.id
                        )
                        del self.bot.configs[source.guild.id]["xp"]["boosteds"][
                            str(boosted.id)
                        ]

                        try:
                            if isinstance(source, Context):
                                await source.send(
                                    f"ℹ️ - Removed `@{source.guild.get_member(int(boosted.id)) or await source.guild.fetch_member(int(boosted.id)) if isinstance(boosted, Member) else source.guild.get_role(int(boosted.id))}` {'role' if isinstance(boosted, Role) else 'member'} from the boosted xp list."
                                )
                            else:
                                await source.response.send_message(
                                    f"ℹ️ - Removed `@{source.guild.get_member(int(boosted.id)) or await source.guild.fetch_member(int(boosted.id)) if isinstance(boosted, Member) else source.guild.get_role(int(boosted.id))}` {'role' if isinstance(boosted, Role) else 'member'} from the boosted xp list."
                                )
                        except NotFound:
                            if isinstance(source, Context):
                                await source.send(
                                    f"ℹ️ - Removed the boost from the boosted xp list."
                                )
                            else:
                                await source.response.send_message(
                                    f"ℹ️ - Removed the boost from the boosted xp list."
                                )

                        if not self.bot.configs[source.guild.id]["xp"]["boosteds"]:
                            del self.bot.configs[source.guild.id]["xp"]["boosteds"]
                elif option == "purge":
                    if "boosteds" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The boosteds list is already empty!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The boosteds list is already empty!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_xp_boosted(source.guild.id)
                    del self.bot.configs[source.guild.id]["xp"]["boosteds"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the Roles & Members from the boosteds list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the Roles & Members from the boosteds list."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.response.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option != 'update' else 'from'} the boosters list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_boosteds = self.bot.config_repo.get_xp_boosted(
                source.guild.id
            ).values()

            if not server_boosteds:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No boosted (members & roles) have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No boosted (members & roles) have been added to the list yet!",
                        ephemeral=True,
                    )

            server_boosteds_roles = []
            server_boosteds_members = []

            for m in server_boosteds:
                if m["type"] == "Role":
                    server_boosteds_roles.append([m["name"], m["bonus"]])
                else:
                    server_boosteds_members.append([m["name"], m["bonus"]])

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's boosteds:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m[0]} (boost: {m[1]}%)`' for m in server_boosteds_members)}\n"
                        if server_boosteds_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r[0]} (boost: {r[1]}%)`' for r in server_boosteds_roles)}\n"
                        if server_boosteds_roles
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's boosteds:**\n\n"
                    + (
                        f"Members: {', '.join(f'`{m[0]} (boost: {m[1]}%)`' for m in server_boosteds_members)}\n"
                        if server_boosteds_members
                        else ""
                    )
                    + (
                        f"Roles: {', '.join(f'`{r[0]} (boost: {r[1]}%)`' for r in server_boosteds_roles)}\n"
                        if server_boosteds_roles
                        else ""
                    )
                )

    """ MAX LVL """

    @config_xp_group.command(
        pass_context=True,
        name="max_lvl",
        aliases=["mx_lvl"],
        brief="🛑",
        description="Manages the server's max level",
        usage="(<number of levels>)",
    )
    async def config_xp_max_lvl_command(self, ctx: Context, max_lvl: int = None):
        """
        This slash manages the server's max level

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        max_lvl: :class:`int` optional
            The maximum level value
        """
        await self.handle_max_lvl(ctx, max_lvl)

    @config_xp_slash_group.sub_command(
        name="max_lvl",
        description="Manages the server's max level",
    )
    async def config_xp_max_lvl_slash_command(
        self, inter: ApplicationCommandInteraction, max_lvl: int = None
    ):
        """
        This slash command manages the server's max level

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        max_lvl: :class:`int` optional
            The maximum level value
        """
        await self.handle_max_lvl(inter, max_lvl)

    async def handle_max_lvl(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        max_lvl: int = None,
    ):
        try:
            if max_lvl:
                if max_lvl <= 0:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The max level value must be greater than 0!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The max level value must be greater than 0!",
                            ephemeral=True,
                        )
                elif max_lvl == self.bot.configs[source.guild.id]["xp"]["max_lvl"]:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - The max level value is already the one configured for this server! Value: `{max_lvl}`",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - The max level value is already the one configured for this server! Value: `{max_lvl}`",
                            ephemeral=True,
                        )

                self.bot.config_repo.set_xp_max_lvl(source.guild.id, max_lvl)
                self.bot.configs[source.guild.id]["xp"]["max_lvl"] = max_lvl

                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The max level is now `{max_lvl}` in this guild!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The max level is now `{max_lvl}` in this guild!"
                    )

                members = set(source.guild.members)
                for member in members:
                    db_user = self.bot.user_repo.get_user(source.guild.id, member.id)
                    if int(db_user["level"]) > max_lvl:
                        self.bot.user_repo.set_levels(
                            source.guild.id, member.id, max_lvl
                        )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's max level is: `{self.bot.configs[source.guild.id]['xp']['max_lvl']}`"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's max level is: `{self.bot.configs[source.guild.id]['xp']['max_lvl']}`"
                    )
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the server's max level! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ LEVEL TO ROLE """

    @config_xp_group.command(
        pass_context=True,
        name="level_to_role",
        aliases=["level_2_role", "lvl_to_role", "lvl_2_role", "l_2_r"],
        brief="🎭",
        description="Manages the server's level to role",
        usage="(add|update|remove|purge <level value> @role)",
    )
    async def config_xp_lvl2role_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        lvl: int = None,
        role: Role = None,
    ):
        """
        This command manages the server's level to role

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or update or remove or purge
        lvl: :class:`int` optional
            The level that will have the role linked to it
        role: :class:`disnake.Role` optional
            The role linked to the level
        """
        await self.handle_select_to_role(ctx, option, lvl, role)

    @config_xp_slash_group.sub_command_group(
        name="level_to_role",
        description="Manages the server's level to role feature",
    )
    async def config_xp_lvl2role_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's level to role

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_xp_lvl2role_slash_group.sub_command(
        name="display",
        description="Displays the state of the server's level to role feature",
    )
    async def config_xp_lvl2role_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the state of the server's level to role feature

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_level_to_role(inter)

    @config_xp_lvl2role_slash_group.sub_command(
        name="add",
        description="Adds a level to role to the server's level to role list",
    )
    async def config_xp_lvl2role_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        lvl: int,
        role: Role,
    ):
        """
        This slash command adds a level to role to the server's level to role list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        lvl: :class:`int`
            The level that will have the role linked to it
        role: :class:`disnake.Role`
            The role linked to the level
        """
        await self.handle_level_to_role(inter, "add", lvl, role)

    @config_xp_lvl2role_slash_group.sub_command(
        name="update",
        description="Updates a level to role from the server's level to role list",
    )
    async def config_xp_lvl2role_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        lvl: int,
        role: Role,
    ):
        """
        This slash command updates a level to role from the server's level to role list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        lvl: :class:`int`
            The level that have a role linked to it
        role: :class:`disnake.Role`
            The new role linked to the level
        """
        await self.handle_level_to_role(inter, "update", lvl, role)

    @config_xp_lvl2role_slash_group.sub_command(
        name="remove",
        description="Removes a level to role from the server's level to role list",
    )
    async def config_xp_lvl2role_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        lvl: int,
    ):
        """
        This slash command removes a level to role from the server's level to role list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        lvl: :class:`int`
            The level that have a role linked to it
        """
        await self.handle_level_to_role(inter, "remove", lvl)

    @config_xp_lvl2role_slash_group.sub_command(
        name="purge",
        description="Purges the server's level to role list",
    )
    async def config_xp_lvl2role_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's level to role list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_level_to_role(inter, "purge")

    async def handle_level_to_role(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        lvl: int = None,
        role: Role = None,
    ):
        if option:
            try:
                if option in ("add", "update", "remove"):
                    if not lvl:
                        raise MissingRequiredArgument(
                            param=Parameter(name="level", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif lvl <= 0:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The level value must be greater than 0!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The level value must be greater than 0!",
                                ephemeral=True,
                            )

                    if option == "add" or option == "update":
                        if not role:
                            raise MissingRequiredArgument(
                                param=Parameter(
                                    name="role", kind=Parameter.KEYWORD_ONLY
                                )
                            )

                        if (
                            "lvl2role" in self.bot.configs[source.guild.id]["xp"]
                            and lvl
                            in set(self.bot.configs[source.guild.id]["xp"]["lvl2role"])
                            and option != "update"
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - The level `{lvl}` is already assigned to a role! Value: `@{self.bot.configs[source.guild.id]['xp']['lvl2role'][lvl]}`",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - The level `{lvl}` is already assigned to a role! Value: `@{self.bot.configs[source.guild.id]['xp']['lvl2role'][lvl]}`",
                                    ephemeral=True,
                                )
                        elif await self.check_role_duplicates(source, role):
                            return

                        self.bot.config_repo.add_xp_lvl2role(
                            source.guild.id, lvl, f"{role}", role.id
                        )

                        if "lvl2role" not in self.bot.configs[source.guild.id]["xp"]:
                            self.bot.configs[source.guild.id]["xp"]["lvl2role"] = {}

                        self.bot.configs[source.guild.id]["xp"]["lvl2role"][lvl] = role

                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the level `{lvl}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the level to role list."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the level `{lvl}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the level to role list."
                            )

                        db_users = self.bot.user_repo.get_users(source.guild.id)
                        members = set(source.guild.members)

                        for member in members:
                            if member.bot:
                                continue

                            await self.xp_class.manage_levels(
                                member,
                                db_users[str(member.id)]["level"],
                                "new_r_2_l",
                            )
                    elif option == "remove":
                        if "lvl2role" not in self.bot.configs[source.guild.id][
                            "xp"
                        ] or lvl not in set(
                            self.bot.configs[source.guild.id]["xp"]["lvl2role"]
                        ):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - The level `{lvl}` is already not in the level to role list!",
                                    delete_after=20,
                                )
                            else:
                                return await source.response.send_message(
                                    f"ℹ️ - {source.author.mention} - The level `{lvl}` is already not in the level to role list!",
                                    ephemeral=True,
                                )

                        self.bot.config_repo.remove_xp_lvl2role(source.guild.id, lvl)
                        role = self.bot.configs[source.guild.id]["xp"]["lvl2role"].pop(
                            lvl
                        )

                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - Removed the level `{lvl}` which was corresponding to the role `@{role}` from the level to role list."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - Removed the level `{lvl}` which was corresponding to the role `@{role}` from the level to role list."
                            )

                        if not self.bot.configs[source.guild.id]["xp"]["lvl2role"]:
                            del self.bot.configs[source.guild.id]["xp"]["lvl2role"]

                        if source.channel.permissions_for(source.guild.me).manage_roles:
                            members = set(source.guild.members)

                            for member in members:
                                if member.bot or role not in member.roles:
                                    continue

                                try:
                                    await member.remove_roles(role)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove this role `@{role.name}` from {member} (maybe the role is above mine)"
                                    raise
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to manage this role `@{role.name}` (i tried to remove the old level role from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                                source.guild.id,
                            )
                elif option == "purge":
                    if "lvl2role" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The level to role list is already empty!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The level to role list is already empty!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_xp_lvl2role(source.guild.id)
                    roles = set(
                        self.bot.configs[source.guild.id]["xp"]["lvl2role"].values()
                    )
                    del self.bot.configs[source.guild.id]["xp"]["lvl2role"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the levels from the level to role list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the levels from the level to role list."
                        )

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        members = set(source.guild.members)

                        for member in members:
                            if member.bot or not roles & set(member.roles):
                                continue

                            try:
                                await member.remove_roles(*roles)
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in roles])} from {member} (maybe one of them is above mine)"
                                raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles {', '.join([f'`@{role.name}`' for role in roles])} (i tried to remove the old level roles from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Forbidden as f:
                raise f
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the level `{lvl}` {'to' if option != 'update' else 'from'} the level to role list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if "lvl2role" not in self.bot.configs[source.guild.id]["xp"]:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No levels to role have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No levels to role have been added to the list yet!",
                        ephemeral=True,
                    )

            server_lvls_2_role = self.bot.configs[source.guild.id]["xp"]["lvl2role"]
            roles_mess = ""

            for key in sorted(server_lvls_2_role):
                roles_mess += f"level `{key}` = `@{server_lvls_2_role[key]}`\n"

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's levels to role:**\n\n{roles_mess}"
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's levels to role:**\n\n{roles_mess}"
                )

    """ PRESTIGES """

    @config_xp_group.command(
        pass_context=True,
        name="prestiges",
        aliases=["prestg", "prestige"],
        brief="💫",
        description="Manages the server's prestiges",
        usage="(add|update|remove|purge @role <prestige_value>)",
    )
    async def config_xp_prestiges_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        role: Role = None,
        prestige: int = None,
    ):
        """
        This command manages the server's prestiges

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            the option -> add or update or remove or purge
        role: :class:`disnake.Role` optional
            The role that have or will have a prestige linked to it
        prestige: :class:`int` optional
            The (new) prestige linked to the role
        """
        await self.handle_prestiges(ctx, option, role, prestige)

    @config_xp_slash_group.sub_command_group(
        name="prestiges",
        description="Manages the server's prestiges",
    )
    async def config_xp_prestiges_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's prestiges

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_xp_slash_group.sub_command_group(
        name="display",
        description="Displays the server's prestiges",
    )
    async def config_xp_prestiges_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's prestiges

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prestiges(inter)

    @config_xp_slash_group.sub_command_group(
        name="add",
        description="Adds a new prestige to the server's prestiges list",
    )
    async def config_xp_prestiges_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        role: Role,
    ):
        """
        This slash command adds a new prestige to the server's prestiges list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        role: :class:`disnake.Role`
            The role that will be linked to the new prestige
        """
        await self.handle_prestiges(inter, "add", role)

    @config_xp_slash_group.sub_command_group(
        name="update",
        description="Updates a prestige from the server's prestiges list",
    )
    async def config_xp_prestiges_update_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        role: Role,
        prestige: int,
    ):
        """
        This slash command updates a prestige from the server's prestiges list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        role: :class:`disnake.Role`
            The role that have a prestige linked to it
        prestige: :class:`int`
            The prestige value
        """
        await self.handle_prestiges(inter, "update", role, prestige)

    @config_xp_slash_group.sub_command_group(
        name="remove",
        description="Removes the last prestige from the server's prestiges list",
    )
    async def config_xp_prestiges_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command removes the last prestige from the server's prestiges list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prestiges(inter, "remove")

    @config_xp_slash_group.sub_command_group(
        name="purge",
        description="Purges the server's prestiges list",
    )
    async def config_xp_prestiges_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's prestiges list

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_prestiges(inter, "purge")

    async def handle_prestiges(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        role: Role = None,
        prestige: int = None,
    ):
        if option:
            try:
                if option == "add":
                    if not role:
                        raise MissingRequiredArgument(
                            param=Parameter(name="role", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif await self.check_role_duplicates(source, role):
                        return

                    if "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
                        self.bot.configs[source.guild.id]["xp"]["prestiges"] = {}

                    prestige = (
                        len(self.bot.configs[source.guild.id]["xp"]["prestiges"]) + 1
                    )

                    self.bot.config_repo.add_xp_prestiges(
                        source.guild.id, f"p_{prestige}", f"{role}", role.id
                    )

                    self.bot.configs[source.guild.id]["xp"]["prestiges"][
                        prestige
                    ] = role

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Added the prestige `{prestige}` corresponding to the `@{role}` role to the prestiges list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Added the prestige `{prestige}` corresponding to the `@{role}` role to the prestiges list."
                        )
                elif option == "update":
                    if not role:
                        raise MissingRequiredArgument(
                            param=Parameter(name="role", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif not prestige:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="prestige", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!",
                                ephemeral=True,
                            )
                    elif (
                        role
                        in set(
                            self.bot.configs[source.guild.id]["xp"][
                                "prestiges"
                            ].values()
                        )
                        and prestige
                        == list(
                            self.bot.configs[source.guild.id]["xp"]["prestiges"].keys()
                        )[
                            list(
                                self.bot.configs[source.guild.id]["xp"][
                                    "prestiges"
                                ].values()
                            ).index(role)
                        ]
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The prestige `{prestige}` already have the role `@{role}` assigned!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The prestige `{prestige}` already have the role `@{role}` assigned!",
                                ephemeral=True,
                            )
                    elif await self.check_role_duplicates(source, role):
                        return

                    old_role = self.bot.configs[source.guild.id]["xp"]["prestiges"][
                        prestige
                    ]

                    self.bot.config_repo.add_xp_prestiges(
                        source.guild.id, f"p_{prestige}", f"{role}", role.id
                    )
                    self.bot.configs[source.guild.id]["xp"]["prestiges"][
                        prestige
                    ] = role

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Updated the prestige `{prestige}` corresponding to the `@{role}` role from the prestiges list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Updated the prestige `{prestige}` corresponding to the `@{role}` role from the prestiges list."
                        )

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        members = set(source.guild.members)

                        for member in members:
                            if member.bot or old_role not in member.roles:
                                continue

                            try:
                                await member.remove_roles(old_role)
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)"
                                raise

                            try:
                                await member.add_roles(role)
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to add the role `{role}` to {member} (maybe the role is above mine)"
                                raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles `@{old_role.name}`, `@{role.name}` (i tried to replace the old prestige role with the new one from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                elif option == "remove":
                    if "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!"
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!"
                            )

                    prestige = len(self.bot.configs[source.guild.id]["xp"]["prestiges"])
                    old_role = self.bot.configs[source.guild.id]["xp"]["prestiges"][
                        prestige
                    ]
                    self.bot.config_repo.remove_xp_prestiges(source.guild.id)

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed the prestige `{prestige}` which was corresponding to the `@{self.bot.configs[source.guild.id]['xp']['prestiges'].pop(len(self.bot.configs[source.guild.id]['xp']['prestiges']))}` role from the prestiges list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed the prestige `{prestige}` which was corresponding to the `@{self.bot.configs[source.guild.id]['xp']['prestiges'].pop(len(self.bot.configs[source.guild.id]['xp']['prestiges']))}` role from the prestiges list."
                        )

                    if not self.bot.configs[source.guild.id]["xp"]["prestiges"]:
                        del self.bot.configs[source.guild.id]["xp"]["prestiges"]

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        members = set(source.guild.members)

                        for member in members:
                            if member.bot or old_role not in member.roles:
                                continue

                            try:
                                await member.remove_roles(old_role)
                            except Forbidden:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)",
                                    source.guild.id,
                                )

                            await self.xp_class.manage_prestige(
                                member, "removed_prestige"
                            )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{old_role.name}` (i tried to remove the old prestige role from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                elif option == "purge":
                    if "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - The prestiges list is already empty!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - The prestiges list is already empty!",
                                ephemeral=True,
                            )

                    old_roles = self.bot.configs[source.guild.id]["xp"][
                        "prestiges"
                    ].values()
                    self.bot.config_repo.purge_xp_prestiges(source.guild.id)
                    del self.bot.configs[source.guild.id]["xp"]["prestiges"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the prestiges from the prestiges list."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the prestiges from the prestiges list."
                        )

                    if source.channel.permissions_for(source.guild.me).manage_roles:
                        members = set(source.guild.members)

                        for member in members:
                            if member.bot or not set(member.roles) & set(old_roles):
                                continue

                            try:
                                await member.remove_roles(*old_roles)
                            except Forbidden:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in old_roles])} from {member} (maybe one of these roles is above mine)",
                                    source.guild.id,
                                )

                            await self.xp_class.manage_prestige(
                                member, "purged_prestiges"
                            )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles {', '.join([f'`@{role.name}`' for role in old_roles])} (i tried to remove the prestige level roles from members)! Required perms: `{', '.join(['MANAGE_ROLES'])}`",
                            source.guild.id,
                        )
                else:
                    await source.send(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Forbidden as f:
                raise f
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the prestige `{prestige}` {'to' if option != 'update' else 'from'} the prestiges list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if "prestiges" not in self.bot.configs[source.guild.id]["xp"]:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No prestiges have been added to the list yet!",
                        ephemeral=True,
                    )

            server_prestiges = self.bot.configs[source.guild.id]["xp"]["prestiges"]
            roles_mess = ""

            for key in sorted(server_prestiges):
                roles_mess += f"prestige `{key}` = `@{server_prestiges[key]}`\n"

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's prestiges:**\n\n{roles_mess}"
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's prestiges:**\n\n{roles_mess}"
                )

    """ MAIN GROUP'S CHANNELS COMMANDS """

    @config_channels_group.command(
        pass_context=True,
        name="commands_channels",
        aliases=["command_channels", "command_channel", "cmds_chans"],
        brief="🕹️",
        description="Manages the server's commands channels (if there is no commands channel then commands can be used everywhere) (can add/remove multiple at a time)",
        usage="(add|remove|purge (#channels))",
    )
    async def config_channels_commands_channels_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *channels: TextChannel,
    ):
        """
        This command manages the server's commands channels (if there is no commands channel then commands can be used everywhere) (can add/remove multiple at a time)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or remove or purge
        channels: :class:`disnake.TextChannel` optional
            The channels that will be added to the server's commands channels (mentions or IDs)
        """
        if channels:
            await self.handle_commands_channels(ctx, option, *channels)
        else:
            await self.handle_commands_channels(ctx, option)

    @config_channels_slash_group.sub_command_group(
        name="commands_channels",
        description="Manages the server's commands channels (if there is no commands channel then commands can be used everywhere)",
    )
    async def config_channels_commands_channels_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's commands channels (if there is no commands channel then commands can be used everywhere)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_commands_channels_slash_group.sub_command(
        name="display",
        description="Displays the server's commands channels",
    )
    async def config_channels_commands_channels_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's commands channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_commands_channels(inter)

    @config_channels_commands_channels_slash_group.sub_command(
        name="add",
        description="Adds channels to the server's commands channels (can add multiple at a time)",
    )
    async def config_channels_commands_channels_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[TextChannel] = Param(None, converter=Utils.channel_converter),
    ):
        """
        This slash command adds channels to the server's commands channels (can add multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[disnake.TextChannel]` optional
            The channels that will be added to the server's commands channels (mentions or IDs)
        """
        if channels:
            await self.handle_commands_channels(inter, "add", *channels)

    @config_channels_commands_channels_slash_group.sub_command(
        name="remove",
        description="Removes channels from the server's commands channels (can remove multiple at a time)",
    )
    async def config_channels_commands_channels_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[TextChannel] = Param(None, converter=Utils.channel_converter),
    ):
        """
        This slash command removes channels from the server's commands channels (can remove multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[disnake.TextChannel]` optional
            The channels that will be removed from the server's commands channels (mentions or IDs)
        """
        if channels:
            await self.handle_commands_channels(inter, "remove", *channels)

    @config_channels_commands_channels_slash_group.sub_command(
        name="purge",
        description="Purges the server's commands channels",
    )
    async def config_channels_commands_channels_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's commands channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_commands_channels(inter, "purge")

    async def handle_commands_channels(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        *channels: TextChannel,
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not channels:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="channels", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    _channels = channels
                    channels = list(channels)
                    dropped_channels = []
                    for channel in _channels:
                        if option == "add":
                            if "commands_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id in set(
                                self.bot.configs[source.guild.id]["commands_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.add_commands_channel(
                                source.guild.id, channel.id, f"{channel}"
                            )

                            if (
                                "commands_channels"
                                not in self.bot.configs[source.guild.id]
                            ):
                                self.bot.configs[source.guild.id][
                                    "commands_channels"
                                ] = []

                            self.bot.configs[source.guild.id][
                                "commands_channels"
                            ].append(channel.id)
                        elif option == "remove":
                            if "commands_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[source.guild.id]["commands_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_commands_channel(
                                source.guild.id, channel.id
                            )
                            del self.bot.configs[source.guild.id]["commands_channels"][
                                self.bot.configs[source.guild.id][
                                    "commands_channels"
                                ].index(channel.id)
                            ]

                    if dropped_channels:
                        if isinstance(source, Context):
                            await source.reply(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the commands channels list!",
                                delete_after=20,
                            )
                        elif not channels:
                            await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the commands channels list!",
                                ephemeral=True,
                            )
                        else:
                            await source.channel.send(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the commands channels list!",
                                delete_after=20,
                            )

                    if channels:
                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the commands channels list!."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the commands channels list!."
                            )

                    if not self.bot.configs[source.guild.id]["commands_channels"]:
                        del self.bot.configs[source.guild.id]["commands_channels"]
                elif option == "purge":
                    if "commands_channels" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No commands channels have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No commands channels have been added to the list yet!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_commands_channels(source.guild.id)
                    del self.bot.configs[source.guild.id]["commands_channels"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the commands channels from the list!."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the commands channels from the list!."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} channels to the commands channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_commands_channels = self.bot.config_repo.get_commands_channels(
                source.guild.id
            ).keys()

            if not server_commands_channels:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No commands channels have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No commands channels have been added to the list yet!",
                        ephemeral=True,
                    )

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's commands channels:** {', '.join([source.guild.get_channel(int(c)).mention for c in server_commands_channels])}"
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's commands channels:** {', '.join([source.guild.get_channel(int(c)).mention for c in server_commands_channels])}"
                )

    """ MUSIC CHANNELS """

    @config_channels_group.command(
        pass_context=True,
        name="music_channels",
        aliases=["music_channel", "music_chans"],
        brief="🎶",
        description="Manages the server's music channels (if there is no music channel then music can be listened everywhere) (can add/remove multiple at a time)",
        usage="(add|remove|purge (#voice_channels))",
    )
    async def config_channels_music_channels_command(
        self, ctx: Context, option: Utils.to_lower = None, *channels: VoiceChannel
    ):
        """
        This command manages the server's music channels (if there is no music channel then music can be listened everywhere) (can add/remove multiple at a time)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or remove or purge
        channels: :class:`disnake.VoiceCHannel` optional
            The channels that will be added / removed to / from the server's music channels list (mentions or IDs)
        """
        if channels:
            await self.handle_music_channels(ctx, option, *channels)
        else:
            await self.handle_music_channels(ctx, option)

    @config_channels_slash_group.sub_command_group(
        name="music_channels",
        description="Manages the server's music channels (if there is no music channel then music can be listened everywhere)",
    )
    async def config_channels_music_channels_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's music channels (if there is no music channel then music can be listened everywhere)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_music_channels_slash_group.sub_command(
        name="display",
        description="Displays the server's music channels",
    )
    async def config_channels_music_channels_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's music channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_music_channels(inter)

    @config_channels_music_channels_slash_group.sub_command(
        name="add",
        description="Adds channels to the server's music channels (can add multiple at a time)",
    )
    async def config_channels_music_channels_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[VoiceChannel] = Param(None, converter=Utils.channel_converter),
    ):
        """
        This slash command adds channels to the server's music channels (can add multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[disnake.VoiceChannel]` optional
            The channels that will be added to the server's music channels list (mentions or IDs)
        """
        if channels:
            await self.handle_music_channels(inter, "add", *channels)

    @config_channels_music_channels_slash_group.sub_command(
        name="remove",
        description="Removes channels from the server's music channels (can remove multiple at a time)",
    )
    async def config_channels_music_channels_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[VoiceChannel] = Param(None, converter=Utils.channel_converter),
    ):
        """
        This slash command removes channels from the server's music channels (can remove multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[disnake.VoiceChannel]` optional
            The channels that will be removed from the server's music channels list (mentions or IDs)
        """
        if channels:
            await self.handle_music_channels(inter, "remove", *channels)

    @config_channels_music_channels_slash_group.sub_command(
        name="purge",
        description="Purges the server's music channels",
    )
    async def config_channels_music_channels_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's music channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_music_channels(inter, "purge")

    async def handle_music_channels(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        *channels: VoiceChannel,
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not channels:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="voice_channels", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    _channels = channels
                    channels = list(channels)
                    dropped_channels = []
                    afk_channel = None
                    for channel in _channels:
                        if option == "add":
                            if "music_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id in set(
                                self.bot.configs[source.guild.id]["music_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue
                            elif channel == source.guild.afk_channel:
                                del channels[channels.index(channel)]
                                afk_channel = channel
                                continue

                            self.bot.config_repo.add_music_channel(
                                source.guild.id, channel.id, f"{channel}"
                            )

                            if (
                                "music_channels"
                                not in self.bot.configs[source.guild.id]
                            ):
                                self.bot.configs[source.guild.id]["music_channels"] = []

                            self.bot.configs[source.guild.id]["music_channels"].append(
                                channel.id
                            )
                        elif option == "remove":
                            if "music_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[source.guild.id]["music_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_music_channel(
                                source.guild.id, channel.id
                            )
                            del self.bot.configs[source.guild.id]["music_channels"][
                                self.bot.configs[source.guild.id][
                                    "music_channels"
                                ].index(channel.id)
                            ]

                    if afk_channel:
                        if isinstance(source, Context):
                            await source.reply(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the music channels list!",
                                delete_after=20,
                            )
                        elif not dropped_channels and not channels:
                            await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the music channels list!",
                                ephemeral=True,
                            )
                        else:
                            await source.channel.send(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the music channels list!",
                                delete_after=20,
                            )

                    if dropped_channels:
                        if isinstance(source, Context):
                            await source.reply(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the music channels list!",
                                delete_after=20,
                            )
                        elif not afk_channel and not channels:
                            await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the music channels list!",
                                ephemeral=True,
                            )
                        else:
                            await source.channel.send(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the music channels list!",
                                delete_after=20,
                            )

                    if channels:
                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the music channels list!."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the music channels list!."
                            )

                    if not self.bot.configs[source.guild.id]["music_channels"]:
                        del self.bot.configs[source.guild.id]["music_channels"]
                elif option == "purge":
                    if "music_channels" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No music channels have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No music channels have been added to the list yet!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_music_channels(source.guild.id)
                    del self.bot.configs[source.guild.id]["music_channels"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the music channels from the list!."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the music channels from the list!."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} {channel.mention} to the music channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_music_channels = self.bot.config_repo.get_music_channels(
                source.guild.id
            ).keys()

            if not server_music_channels:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No music channels have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No music channels have been added to the list yet!",
                        ephemeral=True,
                    )

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's music channels:** {', '.join([source.guild.get_channel(int(c)).mention for c in server_music_channels])}"
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's music channels:** {', '.join([source.guild.get_channel(int(c)).mention for c in server_music_channels])}"
                )

    """ XP GAIN CHANNELS """

    @config_channels_group.command(
        pass_context=True,
        name="xp_gain_channels",
        aliases=["xp_gain_channel"],
        brief="🌌",
        description="Manages the server's xp gain channels (voice & text) (if there is no xp gain channels then xp can be gained everywhere) (can add/remove multiple at a time)",
        usage="(add|remove|purge (#voice_channels|#text_channels))",
    )
    async def config_channels_xp_gain_channels_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *channels: Union[VoiceChannel, TextChannel],
    ):
        """
        This command manages the server's xp gain channels (voice & text) (if there is no xp gain channels then xp can be gained everywhere) (can add/remove multiple at a time)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> add or remove or purge
        channels: :class:`typing.Union[disnake.VoiceChannel, disnake.TextChannel]` optional
            The channels that will be added / removed to / from the server's xp gain channels list (mentions or IDs)
        """
        if channels:
            await self.handle_xp_gain_channels(ctx, option, *channels)
        else:
            await self.handle_xp_gain_channels(ctx, option)

    @config_channels_slash_group.sub_command_group(
        name="xp_gain_channels",
        description="Manages the server's xp gain channels (voice & text) (if there is no xp gain channels then xp can be gained everywhere)",
    )
    async def config_channels_xp_gain_channels_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This command manages the server's xp gain channels (voice & text) (if there is no xp gain channels then xp can be gained everywhere)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_xp_gain_channels_slash_group.sub_command(
        name="display",
        description="Displays the server's xp gain channels",
    )
    async def config_channels_xp_gain_channels_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This command displays the server's xp gain channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_xp_gain_channels(inter)

    @config_channels_xp_gain_channels_slash_group.sub_command(
        name="add",
        description="Adds channels to the server's xp gain channels (can add multiple at a time)",
    )
    async def config_channels_xp_gain_channels_add_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[Union[TextChannel, VoiceChannel]] = Param(
            None, converter=Utils.channel_converter
        ),
    ):
        """
        This slash command adds channels to the server's xp gain channels (can add multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[typing.Union[disnake.TextChannel, disnake.VoiceChannel]]` optional
            The channels that will be added to the server's xp gain channels list (mentions or IDs)
        """
        if channels:
            await self.handle_xp_gain_channels(inter, "add", *channels)

    @config_channels_xp_gain_channels_slash_group.sub_command(
        name="remove",
        description="Removes channels from the server's xp gain channels (can remove multiple at a time)",
    )
    async def config_channels_xp_gain_channels_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channels: List[Union[TextChannel, VoiceChannel]] = Param(
            None, converter=Utils.channel_converter
        ),
    ):
        """
        This slash command removes channels from the server's xp gain channels (can remove multiple at a time)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channels: :class:`typing.List[typing.Union[disnake.TextChannel, disnake.VoiceChannel]]` optional
            The channels that will be removed from the server's xp gain channels list (mentions or IDs)
        """
        if channels:
            await self.handle_xp_gain_channels(inter, "remove", *channels)

    @config_channels_xp_gain_channels_slash_group.sub_command(
        name="purge",
        description="Purges the server's xp gain channels",
    )
    async def config_channels_xp_gain_channels_purge_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command purges the server's xp gain channels

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_xp_gain_channels(inter, "purge")

    async def handle_xp_gain_channels(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        *channels: Union[TextChannel, VoiceChannel],
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not channels:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="channels", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    _channels = channels
                    channels = list(channels)
                    dropped_channels = []
                    afk_channel = None
                    for channel in _channels:
                        if option == "add":
                            if "xp_gain_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id in set(
                                self.bot.configs[source.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue
                            elif channel == source.guild.afk_channel:
                                del channels[channels.index(channel)]
                                afk_channel = channel
                                continue

                            self.bot.config_repo.add_xp_gain_channel(
                                source.guild.id,
                                channel.id,
                                f"{channel}",
                                type(channel).__name__,
                            )

                            if (
                                "xp_gain_channels"
                                not in self.bot.configs[source.guild.id]
                            ):
                                self.bot.configs[source.guild.id][
                                    "xp_gain_channels"
                                ] = {}

                            if (
                                type(channel).__name__
                                not in self.bot.configs[source.guild.id][
                                    "xp_gain_channels"
                                ]
                            ):
                                self.bot.configs[source.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ] = []

                            self.bot.configs[source.guild.id]["xp_gain_channels"][
                                type(channel).__name__
                            ].append(channel.id)
                        elif option == "remove":
                            if "xp_gain_channels" in self.bot.configs[
                                source.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[source.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_xp_gain_channel(
                                source.guild.id, channel.id
                            )
                            del self.bot.configs[source.guild.id]["xp_gain_channels"][
                                type(channel).__name__
                            ][
                                self.bot.configs[source.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ].index(channel.id)
                            ]

                    if afk_channel:
                        if isinstance(source, Context):
                            await source.reply(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the xp gain channels list!",
                                delete_after=20,
                            )
                        elif not dropped_channels and not channels:
                            await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the xp gain channels list!",
                                ephemeral=True,
                            )
                        else:
                            await source.channel.send(
                                f"ℹ️ - {source.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the xp gain channels list!",
                                delete_after=20,
                            )

                    if dropped_channels:
                        if isinstance(source, Context):
                            await source.reply(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the xp gain channels list!",
                                delete_after=20,
                            )
                        elif not dropped_channels and not channels:
                            await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the xp gain channels list!",
                                ephemeral=True,
                            )
                        else:
                            await source.channel.send(
                                f"ℹ️ - {source.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the xp gain channels list!",
                                delete_after=20,
                            )

                    if channels:
                        if isinstance(source, Context):
                            await source.send(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the xp gain channels list!."
                            )
                        else:
                            await source.response.send_message(
                                f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the xp gain channels list!."
                            )

                    if not self.bot.configs[source.guild.id]["xp_gain_channels"][
                        "TextChannel"
                    ]:
                        del self.bot.configs[source.guild.id]["xp_gain_channels"][
                            "TextChannel"
                        ]

                    if not self.bot.configs[source.guild.id]["xp_gain_channels"][
                        "VoiceChannel"
                    ]:
                        del self.bot.configs[source.guild.id]["xp_gain_channels"][
                            "VoiceChannel"
                        ]

                    if not self.bot.configs[source.guild.id]["xp_gain_channels"]:
                        del self.bot.configs[source.guild.id]["xp_gain_channels"]
                elif option == "purge":
                    if "xp_gain_channels" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - {source.author.mention} - No xp gain channels have been added to the list yet!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - {source.author.mention} - No xp gain channels have been added to the list yet!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.purge_xp_gain_channels(source.guild.id)
                    del self.bot.configs[source.guild.id]["xp_gain_channels"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - Removed all the xp gain channels from the list!."
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - Removed all the xp gain channels from the list!."
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await source.channel.send(
                    f"⚠️ - {source.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} channels to the xp gain channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_xp_gain_channels = self.bot.config_repo.get_xp_gain_channels(
                source.guild.id
            )

            if not server_xp_gain_channels:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - No xp gain channels have been added to the list yet!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - No xp gain channels have been added to the list yet!",
                        ephemeral=True,
                    )

            server_xp_gain_channels_text = []
            server_xp_gain_channels_voice = []

            for m in server_xp_gain_channels:
                if server_xp_gain_channels[m]["type"] == "TextChannel":
                    server_xp_gain_channels_text.append(
                        source.guild.get_channel(int(m))
                    )
                else:
                    server_xp_gain_channels_voice.append(
                        source.guild.get_channel(int(m))
                    )

            if isinstance(source, Context):
                await source.send(
                    f"**ℹ️ - Here's the list of the server's xp gain channels:**\n\n"
                    + (
                        f"TextChannels: {', '.join(c.mention for c in server_xp_gain_channels_text)}\n"
                        if server_xp_gain_channels_text
                        else ""
                    )
                    + (
                        f"VoiceChannels: {', '.join(c.mention for c in server_xp_gain_channels_voice)}\n"
                        if server_xp_gain_channels_voice
                        else ""
                    )
                )
            else:
                await source.response.send_message(
                    f"**ℹ️ - Here's the list of the server's xp gain channels:**\n\n"
                    + (
                        f"TextChannels: {', '.join(c.mention for c in server_xp_gain_channels_text)}\n"
                        if server_xp_gain_channels_text
                        else ""
                    )
                    + (
                        f"VoiceChannels: {', '.join(c.mention for c in server_xp_gain_channels_voice)}\n"
                        if server_xp_gain_channels_voice
                        else ""
                    )
                )

    """ XP CHANNEL """

    @config_channels_group.command(
        pass_context=True,
        name="xp_channel",
        aliases=["xp_chan"],
        brief="🌠",
        description="Manages the server's xp channels where every xp event is sent",
        usage="(set|remove #channel)",
    )
    async def config_channels_xp_channel_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        xp_channel: TextChannel = None,
    ):
        """
        This command manages the server's xp channels where every xp event is sent

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        xp_channel: :class:`disnake.TextChannel` optional
            The channel that will be the xp channel
        """
        await self.handle_xp_channel(ctx, option, xp_channel)

    @config_channels_slash_group.sub_command_group(
        name="xp_channel",
        description="Manages the server's xp channel where every xp event is sent",
    )
    async def config_channels_xp_channel_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's xp channel where every xp event is sent

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_xp_channel_slash_group.sub_command(
        name="display",
        description="Displays the server's xp channel",
    )
    async def config_channels_xp_channel_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's xp channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_xp_channel(inter)

    @config_channels_xp_channel_slash_group.sub_command(
        name="set",
        description="Sets the server's xp channel",
    )
    async def config_channels_xp_channel_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channel: TextChannel,
    ):
        """
        This slash command sets the server's xp channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channel: :class:`disnake.TextChannel`
            The channel that will be the xp channel
        """
        await self.handle_xp_channel(inter, "set", channel)

    @config_channels_xp_channel_slash_group.sub_command(
        name="remove",
        description="Removes the server's xp channel",
    )
    async def config_channels_xp_channel_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command removes the server's xp channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_xp_channel(inter, "remove")

    async def handle_xp_channel(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        xp_channel: TextChannel = None,
    ):
        try:
            if option:
                if option == "set":
                    if not xp_channel:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="notify_channel", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif (
                        "notify_channel" in self.bot.configs[source.guild.id]["xp"]
                        and self.bot.configs[source.guild.id]["xp"]["notify_channel"]
                        == xp_channel
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server's xp channel is already {xp_channel.mention}!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server's xp channel is already {xp_channel.mention}!",
                                ephemeral=True,
                            )
                    elif not xp_channel.permissions_for(source.guild.me).send_messages:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {xp_channel.mention}, make sure i have the right permissions in the new polls channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {xp_channel.mention}, make sure i have the right permissions in the new polls channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                delete_after=20,
                            )

                    self.bot.config_repo.set_xp_notify_channel(
                        source.guild.id, xp_channel.id
                    )
                    self.bot.configs[source.guild.id]["xp"][
                        "notify_channel"
                    ] = xp_channel

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The xp channel is now {xp_channel.mention} in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The xp channel is now {xp_channel.mention} in this guild!"
                        )
                elif option == "remove":
                    if "notify_channel" not in self.bot.configs[source.guild.id]["xp"]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server already doesn't have an xp channel configured!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server already doesn't have an xp channel configured!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.set_xp_notify_channel(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["xp"]["notify_channel"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - This guild doesn't have an xp channel anymore!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - This guild doesn't have an xp channel anymore!"
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's xp channel is: {self.bot.configs[source.guild.id]['xp']['notify_channel'].mention}"
                        if "notify_channel" in self.bot.configs[source.guild.id]["xp"]
                        else f"ℹ️ - The server doesn't have an xp channel yet!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's xp channel is: {self.bot.configs[source.guild.id]['xp']['notify_channel'].mention}"
                        if "notify_channel" in self.bot.configs[source.guild.id]["xp"]
                        else f"ℹ️ - The server doesn't have an xp channel yet!"
                    )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the xp channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ POLLS CHANNEL """

    @config_channels_group.command(
        pass_context=True,
        name="polls_channel",
        aliases=["polls_chan"],
        brief="📊",
        description="Manages the server's polls channel where every polls created will be sent",
        usage="(set|remove #channel)",
    )
    async def config_channels_polls_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        polls_channel: TextChannel = None,
    ):
        """
        This command manages the server's polls channel where every polls created will be sent

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        polls_channel: :class:`disnake.TextChannel` optional
            The channel that will be the polls channel
        """
        await self.handle_polls_channel(ctx, option, polls_channel)

    @config_channels_slash_group.sub_command_group(
        name="polls_channel",
        description="Manages the server's polls channel where every polls created will be sent",
    )
    async def config_channels_polls_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's polls channel where every polls created will be sent

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_polls_slash_group.sub_command(
        name="display",
        description="Displays the server's poll channel",
    )
    async def config_channels_polls_channel_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's poll channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_polls_channel(inter)

    @config_channels_polls_slash_group.sub_command(
        name="set",
        description="Sets the server's poll channel",
    )
    async def config_channels_polls_channel_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channel: TextChannel,
    ):
        """
        This slash command sets the server's poll channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channel: :class:`disnake.TextChannel`
            The channel that will be the polls channel
        """
        await self.handle_polls_channel(inter, "set", channel)

    @config_channels_polls_slash_group.sub_command(
        name="remove",
        description="Removes the server's poll channel",
    )
    async def config_channels_polls_channel_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command removes the server's poll channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_polls_channel(inter, "remove")

    async def handle_polls_channel(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        polls_channel: TextChannel = None,
    ):
        try:
            if option:
                if option == "set":
                    if not polls_channel:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="polls_channel", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif (
                        "polls_channel" in self.bot.configs[source.guild.id]
                        and self.bot.configs[source.guild.id]["polls_channel"]
                        == polls_channel
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - This channel is already the one configured to have polls sent in it!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - This channel is already the one configured to have polls sent in it!",
                                ephemeral=True,
                            )
                    elif not polls_channel.permissions_for(
                        source.guild.me
                    ).send_messages:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {polls_channel.mention}, make sure i have the right permissions in the new polls channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {polls_channel.mention}, make sure i have the right permissions in the new polls channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                ephemeral=True,
                            )

                    self.bot.config_repo.set_polls_channel(
                        source.guild.id, polls_channel.id
                    )
                    old_polls_channel = (
                        self.bot.configs[source.guild.id]["polls_channel"]
                        if "polls_channel" in self.bot.configs[source.guild.id]
                        else None
                    )
                    self.bot.configs[source.guild.id]["polls_channel"] = polls_channel

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The polls channel is now {polls_channel.mention} in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The polls channel is now {polls_channel.mention} in this guild!"
                        )

                    if old_polls_channel:
                        polls = self.bot.poll_repo.get_polls(source.guild.id)

                        if len(polls) > 1 or polls and "old" not in polls:
                            perms = old_polls_channel.permissions_for(source.guild.me)
                            if (
                                not perms.read_message_history
                                or not perms.manage_messages
                            ):
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to delete messages in the channel {old_polls_channel.mention}! (I tried to delete the old polls) Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                                    source.guild.id,
                                )

                            for poll in polls:
                                if poll == "old":
                                    continue

                                try:
                                    poll_msg = await old_polls_channel.fetch_message(
                                        int(poll)
                                    )
                                except NotFound:
                                    continue

                                self.bot.poll_repo.erase_poll(source.guild.id, poll)
                                self.bot.configs[source.guild.id]["polls"][
                                    poll_msg.id
                                ].cancel()
                                del self.bot.configs[source.guild.id]["polls"][
                                    poll_msg.id
                                ]

                                if perms.read_message_history and perms.manage_messages:
                                    await poll_msg.delete()

                                poll = polls[poll]
                                view = View(timeout=None)
                                [
                                    [
                                        view.add_item(
                                            Button(label=b.label, custom_id=b.custom_id)
                                        )
                                        for b in a.children
                                    ]
                                    for a in poll_msg.components
                                ]

                                poll_msg: Message = await self.bot.configs[
                                    source.guild.id
                                ]["polls_channel"].send(
                                    embed=poll_msg.embeds[0],
                                    view=view,
                                )

                                self.bot.poll_repo.create_poll(
                                    source.guild.id,
                                    poll_msg.id,
                                    poll["duration_s"]
                                    - (time() - poll["created_at_s"]),
                                    time(),
                                    poll["choices"],
                                    poll["responses"] if "responses" in poll else None,
                                )
                                poll = self.bot.poll_repo.get_poll(
                                    source.guild.id, poll_msg.id
                                )
                                self.bot.configs[source.guild.id]["polls"][
                                    poll_msg.id
                                ] = self.bot.utils_class.task_launcher(
                                    self.bot.utils_class.poll_completion,
                                    (source.guild, poll),
                                    count=1,
                                )
                elif option == "remove":
                    if "polls_channel" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server already doesn't have a polls channel configured!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server already doesn't have a polls channel configured!",
                                ephemeral=True,
                            )

                    polls = self.bot.poll_repo.get_polls(source.guild.id)
                    if len(polls) > 1 or polls and "old" not in polls:
                        perms = self.bot.configs[source.guild.id][
                            "polls_channel"
                        ].permissions_for(source.guild.me)
                        if not perms.read_message_history or not perms.manage_messages:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to delete messages in the channel {self.bot.configs[source.guild.id]['polls_channel'].mention}! (I tried to delete the old polls) Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                                source.guild.id,
                            )

                        for poll in polls:
                            if poll == "old":
                                continue

                            try:
                                poll_msg = await self.bot.configs[source.guild.id][
                                    "polls_channel"
                                ].fetch_message(int(poll))
                            except NotFound:
                                continue

                            self.bot.poll_repo.erase_poll(source.guild.id, poll)
                            self.bot.configs[source.guild.id]["polls"][
                                poll_msg.id
                            ].cancel()
                            del self.bot.configs[source.guild.id]["polls"][poll_msg.id]

                            if perms.read_message_history and perms.manage_messages:
                                await poll_msg.delete()

                    self.bot.config_repo.set_polls_channel(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["polls_channel"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - This guild doesn't have a polls channel anymore!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - This guild doesn't have a polls channel anymore!"
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's polls channel is: {self.bot.configs[source.guild.id]['polls_channel'].mention}"
                        if "polls_channel" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a polls channel yet!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's polls channel is: {self.bot.configs[source.guild.id]['polls_channel'].mention}"
                        if "polls_channel" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a polls channel yet!"
                    )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the polls channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ SELECT TO ROLE CHANNEL """

    @config_channels_group.command(
        pass_context=True,
        name="select_to_role_channel",
        aliases=["select2role_channel"],
        brief="🤠",
        description="Manages the server's select 2 role channels where the select to role message is sent",
        usage="(set|remove #channel)",
    )
    async def config_channels_select2role_channel_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        select2role_channel: TextChannel = None,
    ):
        """
        This command manages the server's select 2 role channels where the select to role message is sent

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        select2role_channel: :class:`disnake.TextChannel` optional
            The channel that will be the select to role channel
        """
        await self.handle_select_to_role_channel(ctx, option, select2role_channel)

    @config_channels_slash_group.sub_command_group(
        name="select_to_role_channel",
        description="Manages the server's select 2 role channel where the select to role message is sent",
    )
    async def config_channels_select2role_channel_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's select 2 role channels where the select to role message is sent

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_select2role_channel_slash_group.sub_command(
        name="display",
        description="Displays the server's select 2 role channel",
    )
    async def config_channels_select2role_channel_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's select 2 role channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_select_to_role_channel(inter)

    @config_channels_select2role_channel_slash_group.sub_command(
        name="set",
        description="Sets the server's select 2 role channel",
    )
    async def config_channels_select2role_channel_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channel: TextChannel,
    ):
        """
        This slash command sets the server's select 2 role channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channel: :class:`disnake.TextChannel`
            The channel that will be the select 2 role channel
        """
        await self.handle_select_to_role_channel(inter, "set", channel)

    @config_channels_select2role_channel_slash_group.sub_command(
        name="remove",
        description="Removes the server's select 2 role channel",
    )
    async def config_channels_select2role_channel_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command removes the server's select 2 role channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_select_to_role_channel(inter, "remove")

    async def handle_select_to_role_channel(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        select2role_channel: TextChannel = None,
    ):
        try:
            if option:
                if option == "set":
                    if not select2role_channel:
                        raise MissingRequiredArgument(
                            param=Parameter(name="channel", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif (
                        "select2role" in self.bot.configs[source.guild.id]
                        and "channel"
                        in self.bot.configs[source.guild.id]["select2role"]
                        and self.bot.configs[source.guild.id]["select2role"]["channel"]
                        == select2role_channel
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server's select to role channel is already {select2role_channel.mention}!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server's select to role channel is already {select2role_channel.mention}!",
                                ephemeral=True,
                            )
                    elif not select2role_channel.permissions_for(
                        source.guild.me
                    ).send_messages:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {select2role_channel.mention}, make sure i have the right permissions in the new select to role channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {select2role_channel.mention}, make sure i have the right permissions in the new select to role channel before setting it! Required perms: `{', '.join(['SEND_MESSAGES'])}`",
                                ephemeral=True,
                            )

                    old_channel = None
                    if "select2role" not in self.bot.configs[source.guild.id]:
                        self.bot.configs[source.guild.id]["select2role"] = {}
                    elif "channel" in self.bot.configs[source.guild.id]["select2role"]:
                        old_channel: TextChannel = self.bot.configs[source.guild.id][
                            "select2role"
                        ]["channel"]

                    self.bot.configs[source.guild.id]["select2role"][
                        "channel"
                    ] = select2role_channel

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The select to role channel is now {select2role_channel.mention} in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The select to role channel is now {select2role_channel.mention} in this guild!"
                        )

                    if old_channel:
                        perms = old_channel.permissions_for(source.guild.me)
                        if perms.read_message_history and perms.manage_messages:
                            await old_channel.purge(
                                check=lambda m: m.author.id == self.bot.user.id
                            )
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to purge messages in the channel {old_channel.mention}! Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                                source.guild.id,
                            )

                    em = Embed(
                        colour=self.bot.color,
                        title="Roles",
                        description="Here are the server's select to role available, choose one or more roles you wish to be assigned.\n\n**If you want the role to be removed, deselect the corresponding role!**",
                    )

                    if source.guild.icon:
                        em.set_thumbnail(url=source.guild.icon.url)

                    if self.bot.user.avatar:
                        em.set_footer(
                            text=self.bot.user.name, icon_url=self.bot.user.avatar.url
                        )
                    else:
                        em.set_footer(text=self.bot.user.name)

                    em.set_author(
                        name=source.guild.name,
                        icon_url=source.guild.icon.url if source.guild.icon else None,
                    )

                    options = []
                    if (
                        "select2role" in self.bot.configs[source.guild.id]
                        and "selects"
                        in self.bot.configs[source.guild.id]["select2role"]
                    ):
                        values = []
                        for title, value in self.bot.configs[source.guild.id][
                            "select2role"
                        ]["selects"].items():
                            values.append(f"{title}: `@{value['role'].name}`")

                            options.append(
                                SelectOption(
                                    label=title,
                                    description=value["description"],
                                    value=title,
                                    default=False,
                                )
                            )

                        em.add_field(
                            name="Available roles:",
                            value="\n".join(values),
                        )
                    else:
                        em.add_field(
                            name="Information", value="For now no roles are available!"
                        )

                    view = None

                    if options:
                        view = View(timeout=None)
                        view.add_item(
                            Select(
                                options=options,
                                custom_id=f"{self.bot.configs[source.guild.id]['select2role']['channel'].id}",
                                placeholder="Choose one or more role!",
                                min_values=0,
                                max_values=len(options),
                            )
                        )

                    self.bot.configs[source.guild.id]["select2role"]["roles_msg_id"] = (
                        await self.bot.configs[source.guild.id]["select2role"][
                            "channel"
                        ].send(
                            embed=em,
                            view=view,
                        )
                    ).id

                    self.bot.config_repo.set_select2role_channel(
                        source.guild.id,
                        select2role_channel.id,
                        self.bot.configs[source.guild.id]["select2role"][
                            "roles_msg_id"
                        ],
                    )
                elif option == "remove":
                    if (
                        "select2role" not in self.bot.configs[source.guild.id]
                        or "channel"
                        not in self.bot.configs[source.guild.id]["select2role"]
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server already doesn't have a select to role channel configured!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server already doesn't have a select to role channel configured!",
                                ephemeral=True,
                            )

                    perms = self.bot.configs[source.guild.id]["select2role"][
                        "channel"
                    ].permissions_for(source.guild.me)

                    if perms.read_message_history and perms.manage_messages:
                        await self.bot.configs[source.guild.id]["select2role"][
                            "channel"
                        ].purge(check=lambda m: m.author.id == self.bot.user.id)
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[source.guild.id]['select2role']['channel'].mention}! Required perms: `{', '.join(['READ_MESSAGE_HISTORY', 'MANAGE_MESSAGES'])}`",
                            source.guild.id,
                        )

                    self.bot.config_repo.set_select2role_channel(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["select2role"]["channel"]
                    del self.bot.configs[source.guild.id]["select2role"]["roles_msg_id"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - This guild doesn't have a select to role channel anymore!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - This guild doesn't have a select to role channel anymore!"
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's select to role channel is: {self.bot.configs[source.guild.id]['select2role']['channel'].mention}"
                        if "select2role" in self.bot.configs[source.guild.id]
                        and "channel"
                        in self.bot.configs[source.guild.id]["select2role"]
                        else f"ℹ️ - The server doesn't have a select to role channel yet!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's select to role channel is: {self.bot.configs[source.guild.id]['select2role']['channel'].mention}"
                        if "select2role" in self.bot.configs[source.guild.id]
                        and "channel"
                        in self.bot.configs[source.guild.id]["select2role"]
                        else f"ℹ️ - The server doesn't have a select to role channel yet!"
                    )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the select to role channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ MODS CHANNEL """

    @config_channels_group.command(
        pass_context=True,
        name="mods_channel",
        aliases=["mod_channel"],
        brief="🔱",
        description="Manages the server's mods channel where all the error messages and other information are sent",
        usage="(set|remove #channel)",
    )
    async def config_channels_mods_channel_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        mods_channel: TextChannel = None,
    ):
        """
        This command manages the server's mods channel where all the error messages and other information are sent

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        mods_channel: :class:`disnake.TextChannel` optional
            The channel that will be the mods channel
        """
        await self.handle_mods_channel(ctx, option, mods_channel)

    @config_channels_slash_group.sub_command_group(
        name="mods_channel",
        description="Manages the server's mods channel where all the error messages and other information are sent",
    )
    async def config_channels_mods_channel_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's mods channel where all the error messages and other information are sent

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_mods_channel_slash_group.sub_command(
        name="display",
        description="Displays the server's mods channel",
    )
    async def config_channels_mods_channel_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's mods channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_mods_channel(inter)

    @config_channels_mods_channel_slash_group.sub_command(
        name="set",
        description="Sets the server's mods channel",
    )
    async def config_channels_mods_channel_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channel: TextChannel,
    ):
        """
        This slash command sets the server's mods channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channel: :class:`disnake.TextChannel` optional
            The channel that will be the mods channel
        """
        await self.handle_mods_channel(inter, "set", channel)

    @config_channels_mods_channel_slash_group.sub_command(
        name="remove",
        description="Removes the server's mods channel",
    )
    async def config_channels_mods_channel_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash removes the server's mods channel

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_mods_channel(inter, "remove")

    async def handle_mods_channel(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        mods_channel: TextChannel = None,
    ):
        try:
            if option:
                if option == "set":
                    if not mods_channel:
                        raise MissingRequiredArgument(
                            param=Parameter(name="channel", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif (
                        "mods_channel" in self.bot.configs[source.guild.id]
                        and self.bot.configs[source.guild.id]["mods_channel"]
                        == mods_channel
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server's mods channel is already {mods_channel.mention}!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server's mods channel is already {mods_channel.mention}!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.set_mods_channel(
                        source.guild.id,
                        mods_channel.id,
                    )
                    self.bot.configs[source.guild.id]["mods_channel"] = mods_channel

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The mods channel is now {mods_channel.mention} in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The mods channel is now {mods_channel.mention} in this guild!"
                        )
                elif option == "remove":
                    if "mods_channel" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server already doesn't have a mods channel configured!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server already doesn't have a mods channel configured!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.set_mods_channel(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["mods_channel"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - This guild doesn't have a mods channel anymore!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - This guild doesn't have a mods channel anymore!"
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's mods channel is: {self.bot.configs[source.guild.id]['mods_channel'].mention}"
                        if "mods_channel" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a mods channel yet!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's mods channel is: {self.bot.configs[source.guild.id]['mods_channel'].mention}"
                        if "mods_channel" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a mods channel yet!"
                    )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the mods channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ GAMES CATEGORY """

    @config_channels_group.command(
        pass_context=True,
        name="games_category",
        aliases=["game_category"],
        brief="🔱",
        description="Manages the server's games category where all the game channels are created",
        usage="(set|remove #category)",
    )
    async def config_channels_games_category_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        games_category: CategoryChannel = None,
    ):
        """
        This command manages the server's games category where all the game channels are created

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        option: :class:`Utils.to_lower` optional
            The option -> set or remove
        games_category: :class:`disnake.CategoryChannel` optional
            The category that will be the games category
        """
        await self.handle_games_category(ctx, option, games_category)

    @config_channels_slash_group.sub_command_group(
        name="games_category",
        description="Manages the server's games category where all the game channels are created",
    )
    async def config_channels_games_category_slash_group(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command group manages the server's games category where all the game channels are created

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        pass

    @config_channels_games_category_slash_group.sub_command(
        name="display",
        description="Displays the server's games category",
    )
    async def config_channels_games_category_display_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash command displays the server's games category

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_games_category(inter)

    @config_channels_games_category_slash_group.sub_command(
        name="set",
        description="Sets the server's games category",
    )
    async def config_channels_games_category_set_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        category: CategoryChannel,
    ):
        """
        This slash command sets the server's games category

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        category: :class:`disnake.CategoryChannel` optional
            The category that will be the games category
        """
        await self.handle_games_category(inter, "set", category)

    @config_channels_games_category_slash_group.sub_command(
        name="remove",
        description="Removes the server's games category",
    )
    async def config_channels_games_category_remove_slash_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        This slash removes the server's games category

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_games_category(inter, "remove")

    async def handle_games_category(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        option: str = None,
        games_category: CategoryChannel = None,
    ):
        try:
            if option:
                if option == "set":
                    if not games_category:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="category", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif (
                        "games_category" in self.bot.configs[source.guild.id]
                        and self.bot.configs[source.guild.id]["games_category"]
                        == games_category
                    ):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server's games category is already {games_category.mention}!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server's games category is already {games_category.mention}!",
                                ephemeral=True,
                            )

                    if (
                        "games_category" in self.bot.configs[source.guild.id]
                        and self.bot.configs[source.guild.id]["games_category"]
                    ):
                        if (
                            self.bot.configs[source.guild.id]["games_category"]
                            .permissions_for(source.guild.me)
                            .manage_channels
                        ):
                            channels: List[TextChannel] = self.bot.configs[
                                source.guild.id
                            ]["games_category"].channels

                            for channel in channels:
                                await channel.move(
                                    category=games_category,
                                    reason=f"Games category set to {games_category} by {source.author}!",
                                )
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to delete channels from the category {self.bot.configs[source.guild.id]['tickets']['tickets_category'].mention}! Required perms: `{', '.join(['MANAGE_CHANNELS'])}`",
                                source.guild.id,
                            )

                    self.bot.config_repo.set_games_category(
                        source.guild.id,
                        games_category.id,
                    )
                    self.bot.configs[source.guild.id]["games_category"] = games_category

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - The games category is now {games_category.mention} in this guild!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - The games category is now {games_category.mention} in this guild!"
                        )
                elif option == "remove":
                    if "games_category" not in self.bot.configs[source.guild.id]:
                        if isinstance(source, Context):
                            return await source.reply(
                                f"ℹ️ - The server already doesn't have a games category configured!",
                                delete_after=20,
                            )
                        else:
                            return await source.response.send_message(
                                f"ℹ️ - The server already doesn't have a games category configured!",
                                ephemeral=True,
                            )

                    self.bot.config_repo.set_games_category(source.guild.id, None)
                    del self.bot.configs[source.guild.id]["games_category"]

                    if isinstance(source, Context):
                        await source.send(
                            f"ℹ️ - This guild doesn't have a games category anymore!"
                        )
                    else:
                        await source.response.send_message(
                            f"ℹ️ - This guild doesn't have a games category anymore!"
                        )
                else:
                    await source.reply(
                        f"ℹ️ - {source.author.mention} - This option isn't available for the command `{source.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                if isinstance(source, Context):
                    await source.send(
                        f"ℹ️ - The current server's games category is: {self.bot.configs[source.guild.id]['games_category'].mention}"
                        if "games_category" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a games category yet!"
                    )
                else:
                    await source.response.send_message(
                        f"ℹ️ - The current server's games category is: {self.bot.configs[source.guild.id]['games_category'].mention}"
                        if "games_category" in self.bot.configs[source.guild.id]
                        else f"ℹ️ - The server doesn't have a games category yet!"
                    )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await source.channel.send(
                f"⚠️ - {source.author.mention} - An error occurred while setting the games category! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    """ METHOD(S) """

    async def check_role_duplicates(
        self, source: Union[Context, ApplicationCommandInteraction], role: Role
    ) -> bool:
        if (
            "muted_role" in self.bot.configs[source.guild.id]
            and self.bot.configs[source.guild.id]["muted_role"] == role
        ):
            resp = f"ℹ️ - This role is already the one configured has the muted role!"
        elif role.id in set(self.bot.moderators[source.guild.id]):
            resp = f"ℹ️ - {source.author.mention} - The role `@{role}` is already assigned to a moderator!"
        elif role.id in set(self.bot.djs[source.guild.id]):
            resp = f"ℹ️ - {source.author.mention} - The role `@{role}` is already assigned to a dj!"
        elif "prestiges" in self.bot.configs[source.guild.id]["xp"] and role in set(
            self.bot.configs[source.guild.id]["xp"]["prestiges"].values()
        ):
            resp = f"ℹ️ - {source.author.mention} - The role `@{role}` is already assigned to a prestige! Prestige: `{list(self.bot.configs[source.guild.id]['xp']['prestiges'].keys())[list(self.bot.configs[source.guild.id]['xp']['prestiges'].values()).index(role)]}`"
        elif "lvl2role" in self.bot.configs[source.guild.id]["xp"] and role in set(
            self.bot.configs[source.guild.id]["xp"]["lvl2role"].values()
        ):
            resp = f"ℹ️ - {source.author.mention} - The role `@{role}` is already assigned to a level! Level: `{list(self.bot.configs[source.guild.id]['xp']['lvl2role'].keys())[list(self.bot.configs[source.guild.id]['xp']['lvl2role'].values()).index(role)]}`"
        elif (
            "select2role" in self.bot.configs[source.guild.id]
            and "selects" in self.bot.configs[source.guild.id]["select2role"]
            and role
            in {
                v["role"]
                for v in self.bot.configs[source.guild.id]["select2role"][
                    "selects"
                ].values()
            }
        ):
            resp = f"ℹ️ - {source.author.mention} - The role `@{role}` is already assigned to a title! Title: `{list(self.bot.configs[source.guild.id]['select2role']['selects'].keys())[list(self.bot.configs[source.guild.id]['select2role']['selects'].values()).index(role)]}`"
        else:
            return False

        if isinstance(source, Context):
            await source.reply(resp, delete_after=20)
        else:
            await source.channel.send(resp, delete_after=20)

        return True


def setup(bot):
    bot.add_cog(Moderation(bot))
