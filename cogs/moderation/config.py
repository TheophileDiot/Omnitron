from discord import (
    CategoryChannel,
    Embed,
    Forbidden,
    Member,
    NotFound,
    Role,
    TextChannel,
    VoiceChannel,
)
from discord.ext.commands import bot_has_permissions, Context, Cog, group
from discord.ext.commands.errors import (
    BadArgument,
    BadUnionArgument,
    MissingRequiredArgument,
)
from dislash import ActionRow, Button, SelectMenu, SelectOption
from inspect import Parameter
from time import time
from typing import Union

from bot import Omnitron
from data import Utils, Xp_class

BOOL2VAL = {True: "ON", False: "OFF"}


class Moderation(Cog):
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
        description="This option manage the server's security",
    )
    async def config_security_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's security configuration",
                )
            )

    @config_group.group(
        pass_context=True,
        case_insensitive=True,
        name="xp",
        brief="✨",
        usage="(sub-command)",
        description="This option manage the server's experience feature",
    )
    async def config_xp_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's experience configuration",
                )
            )

    @config_group.group(
        pass_context=True,
        case_insensitive=True,
        name="channels",
        aliases=["channel"],
        brief="📻",
        usage="(sub-command)",
        description="This option manage the server's special channels",
    )
    async def config_channels_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's channels configuration",
                )
            )

    """ MAIN GROUP'S COMMAND(S) """

    @config_group.command(
        pass_context=True,
        name="moderators",
        aliases=["mods"],
        brief="🔨",
        description="This option manage the server's moderators (role & members) (can add/remove multiple at a time)",
        usage="add|remove|purge @role|@member",
    )
    async def config_moderators_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *mods: Union[Role, Member],
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
                    dropped_mods = []
                    bot_mods = []
                    for mod in _mods:
                        if option == "add":
                            if mod.id in set(self.bot.moderators[ctx.guild.id]):
                                del mods[mods.index(mod)]
                                dropped_mods.append(mod)
                                continue
                            elif isinstance(mod, Member) and mod.bot:
                                del mods[mods.index(mod)]
                                bot_mods.append(mod)
                                continue

                            self.bot.config_repo.add_moderator(
                                ctx.guild.id, mod.id, f"{mod}", type(mod).__name__
                            )
                            self.bot.moderators[ctx.guild.id].append(mod.id)
                        elif option == "remove":
                            if mod.id not in set(self.bot.moderators[ctx.guild.id]):
                                del mods[mods.index(mod)]
                                dropped_mods.append(mod)
                                continue

                            self.bot.config_repo.remove_moderator(ctx.guild.id, mod.id)
                            del self.bot.moderators[ctx.guild.id][
                                self.bot.moderators[ctx.guild.id].index(mod.id)
                            ]

                    if bot_mods:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([f'`@{mod}`' for mod in bot_mods])} {'is a' if len(bot_mods) == 1 else 'are'} bot user{'s' if len(bot_mods) > 1 else ''} so you can't add {'them' if len(bot_mods) > 1 else 'him'} in the moderators list!",
                            delete_after=20,
                        )

                    if dropped_mods:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in dropped_mods])} {'is' if len(dropped_mods) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the moderators list!",
                            delete_after=20,
                        )

                    if mods:
                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{mod} ({type(mod).__name__})`' for mod in mods])} {'to' if option == 'add' else 'from'} the moderators list!."
                        )
                elif option == "purge":
                    if not self.bot.moderators[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No moderators (members & roles) have been added to the list yet!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_moderators(ctx.guild.id)
                    self.bot.moderators[ctx.guild.id] = {}
                    await ctx.send(
                        f"ℹ️ - Removed all the moderators from the moderators list."
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} `@{mod}` {'role' if isinstance(mod, Role) else 'member'} to the moderators list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_mods = self.bot.config_repo.get_moderators(ctx.guild.id).values()

            if not server_mods:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No moderators (members & roles) have been added to the list yet!",
                    delete_after=20,
                )

            server_mods_roles = []
            server_mods_members = []

            for m in server_mods:
                if m["type"] == "Role":
                    server_mods_roles.append(m["name"])
                else:
                    server_mods_members.append(m["name"])

            await ctx.send(
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

    @config_group.command(
        pass_context=True,
        name="djs",
        aliases=["players"],
        brief="🧑‍🎤",
        description="This option manage the server's djs (role & members) (if there is no dj then everyone can use music commands) (can add/remove multiple at a time)",
        usage="add|remove|purge @role|@member",
    )
    async def config_djs_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *djs: Union[Role, Member],
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
                    dropped_djs = []
                    bot_djs = []
                    for dj in _djs:
                        if option == "add":
                            if dj.id in set(self.bot.djs[ctx.guild.id]):
                                del djs[djs.index(dj)]
                                dropped_djs.append(dj)
                                continue
                            elif isinstance(dj, Member) and dj.bot:
                                del djs[djs.index(dj)]
                                bot_djs.append(dj)
                                continue

                            self.bot.config_repo.add_dj(
                                ctx.guild.id, dj.id, f"{dj}", type(dj).__name__
                            )
                            self.bot.djs[ctx.guild.id].append(dj.id)
                        elif option == "remove":
                            if dj.id not in set(self.bot.djs[ctx.guild.id]):
                                del djs[djs.index(dj)]
                                dropped_djs.append(dj)
                                continue

                            self.bot.config_repo.remove_dj(ctx.guild.id, dj.id)
                            del self.bot.djs[ctx.guild.id][
                                self.bot.djs[ctx.guild.id].index(dj.id)
                            ]
                            try:
                                await ctx.send(
                                    f"ℹ️ - Removed `@{await ctx.guild.try_member(int(dj.id)) if isinstance(dj, Member) else ctx.guild.get_role(int(dj.id))}` {'role' if isinstance(dj, Role) else 'member'} from the djs list!."
                                )
                            except NotFound:
                                pass

                    if bot_djs:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([f'`@{dj}`' for dj in bot_djs])} {'is a' if len(bot_djs) == 1 else 'are'} bot user{'s' if len(bot_djs) > 1 else ''} so you can't add {'them' if len(bot_djs) > 1 else 'him'} in the djs list!",
                            delete_after=20,
                        )

                    if dropped_djs:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([f'`@{dj} ({type(dj).__name__})`' for dj in dropped_djs])} {'is' if len(dropped_djs) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the djs list!",
                            delete_after=20,
                        )

                    if djs:
                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([f'`@{dj} ({type(dj).__name__})`' for dj in djs])} {'to' if option == 'add' else 'from'} the djs list!."
                        )
                elif option == "purge":
                    if not self.bot.djs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No djs (members & roles) have been added to the list yet!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_djs(ctx.guild.id)
                    self.bot.djs[ctx.guild.id] = {}
                    await ctx.send(f"ℹ️ - Removed all the djs from the djs list!.")
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} `@{dj}` {'role' if isinstance(dj, Role) else 'member'} to the djs list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_djs = self.bot.config_repo.get_djs(ctx.guild.id).values()

            if not server_djs:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No djs (members & roles) have been added to the list yet!",
                    delete_after=20,
                )

            server_djs_roles = []
            server_djs_members = []

            for m in server_djs:
                if m["type"] == "Role":
                    server_djs_roles.append(m["name"])
                else:
                    server_djs_members.append(m["name"])

            await ctx.send(
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

    @config_group.command(
        pass_context=True,
        name="prefix",
        aliases=["prfx"],
        brief="❗",
        description="This option manage the server's prefix",
        usage="(set|reset) (<prefix>)",
    )
    async def config_prefix_command(
        self, ctx: Context, option: Utils.to_lower = None, prefix: str = None
    ):
        if option:
            try:
                if option == "set":
                    if not prefix:
                        raise MissingRequiredArgument(
                            param=Parameter(name="prefix", kind=Parameter.KEYWORD_ONLY)
                        )
                    self.bot.config_repo.set_prefix(ctx.guild.id, prefix)
                    self.bot.configs[ctx.guild.id]["prefix"] = prefix
                    await ctx.send(f"ℹ️ - Bot prefix updated to `{prefix}`.")
                elif option == "reset":
                    self.bot.config_repo.set_prefix(ctx.guild.id)
                    self.bot.configs[ctx.guild.id]["prefix"] = "o!"
                    await ctx.send(f"ℹ️ - Bot prefix hs been reset to `o!`.")
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'resetting the prefix' if option == 'reset' else f'setting the prefix to `{prefix}`'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            msg = await ctx.send(
                f"ℹ️ - {ctx.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`!"
            )

            try:
                await msg.add_reaction("👀")
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to add reactions in the channel {ctx.channel.mention} (message: {msg.jump_url}, reaction: 👀)!"
                raise

    @config_group.command(
        pass_context=True,
        name="tickets",
        aliases=["ticket"],
        brief="📥",
        description="This option manage the server's tickets channel and category!",
        usage="(on|update|resolve|off) (#channel) (#category|<category_name>)",
    )
    async def config_tickets_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "tickets" in self.bot.configs[ctx.guild.id]
                ) == val and option not in ("update", "resolve"):
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The tickets are already set to `{BOOL2VAL[val]}`!"
                        + (
                            " Parameters: "
                            + f"\n'tickets_channel': {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[ctx.guild.id]['tickets'] else '`No channel specified.`'}"
                            + f"\n'tickets_category': {self.bot.configs[ctx.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[ctx.guild.id]['tickets'] else '`No category specified.`'}"
                            if "tickets" in self.bot.configs[ctx.guild.id]
                            else ""
                        )
                    )

                if val:
                    if "tickets" not in self.bot.configs[ctx.guild.id] and option in (
                        "update",
                        "resolve",
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The tickets are set to `OFF`! Please activate them before {'updating' if option == 'update' else 'resolving'}."
                        )
                    if option == "resolve":
                        if (
                            "tickets_channel"
                            not in self.bot.configs[ctx.guild.id]["tickets"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - There is no tickets_channel configure! Please configure one before resolving."
                            )

                        if [
                            m
                            for m in set(
                                await self.bot.configs[ctx.guild.id]["tickets"][
                                    "tickets_channel"
                                ]
                                .history(limit=10)
                                .flatten()
                            )
                            if m.author.id == self.bot.user.id
                        ]:
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - There is no need for the ticket message to be resolved."
                            )

                        tickets_channel = self.bot.configs[ctx.guild.id]["tickets"][
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
                            ctx.guild.id,
                            val,
                            tickets_channel.id
                            if isinstance(tickets_channel, TextChannel)
                            else self.bot.configs[ctx.guild.id]["tickets"][
                                "tickets_channel"
                            ].id,
                            tickets_channel.id
                            if isinstance(tickets_channel, CategoryChannel)
                            else tickets_category
                            if isinstance(tickets_channel, CategoryChannel)
                            else self.bot.configs[ctx.guild.id]["tickets"][
                                "tickets_category"
                            ].id,
                        )

                        if isinstance(tickets_channel, TextChannel):
                            if (
                                ctx.guild.me.permissions_in(
                                    self.bot.configs[ctx.guild.id]["tickets"][
                                        "tickets_channel"
                                    ]
                                ).read_message_history
                                and ctx.guild.me.permissions_in(
                                    self.bot.configs[ctx.guild.id]["tickets"][
                                        "tickets_channel"
                                    ]
                                ).manage_messages
                            ):
                                await self.bot.configs[ctx.guild.id]["tickets"][
                                    "tickets_channel"
                                ].purge(check=lambda m: m.author.id == self.bot.user.id)
                            else:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention}!",
                                    ctx.guild.id,
                                )

                        self.bot.configs[ctx.guild.id]["tickets"] = {
                            "tickets_channel": tickets_channel
                            if isinstance(tickets_channel, TextChannel)
                            else self.bot.configs[ctx.guild.id]["tickets"][
                                "tickets_channel"
                            ],
                            "tickets_category": tickets_channel
                            if isinstance(tickets_channel, CategoryChannel)
                            else tickets_category
                            if isinstance(tickets_channel, CategoryChannel)
                            else self.bot.configs[ctx.guild.id]["tickets"][
                                "tickets_category"
                            ],
                        }

                    elif option != "resolve":
                        self.bot.config_repo.set_tickets(
                            ctx.guild.id,
                            val,
                            tickets_channel.id,
                            tickets_category.id,
                        )
                        self.bot.configs[ctx.guild.id]["tickets"] = {
                            "tickets_channel": tickets_channel,
                            "tickets_category": tickets_category,
                        }

                    if isinstance(tickets_channel, TextChannel):
                        em = Embed(
                            colour=self.bot.color,
                            title="📥 - Ticket",
                            description="**To create a ticket please click on the button 📥**\n\nAfter clicking on the button, a private room will be created at the bottom of the ticket category.\n\nYou can only create one ticket at a time.",
                        )

                        em.set_thumbnail(url=ctx.guild.icon_url)
                        em.set_footer(
                            text=self.bot.user.name, icon_url=self.bot.user.avatar_url
                        )

                        if self.bot.configs[ctx.guild.id]["tickets"][
                            "tickets_channel"
                        ].can_send:
                            await self.bot.configs[ctx.guild.id]["tickets"][
                                "tickets_channel"
                            ].send(
                                content=None,
                                embed=em,
                                components=[
                                    ActionRow(
                                        Button(
                                            style=1,
                                            emoji="📥",
                                            custom_id=f"{self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].id}.ticket_create",
                                        )
                                    )
                                ],
                            )
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention} (i tried to send the message that allow users to create tickets so please reactivate this feature after changing the permissions)!",
                                ctx.guild.id,
                            )
                else:
                    if (
                        ctx.guild.me.permissions_in(
                            self.bot.configs[ctx.guild.id]["tickets"]["tickets_channel"]
                        ).read_message_history
                        and ctx.guild.me.permissions_in(
                            self.bot.configs[ctx.guild.id]["tickets"]["tickets_channel"]
                        ).manage_messages
                    ):
                        await self.bot.configs[ctx.guild.id]["tickets"][
                            "tickets_channel"
                        ].purge(check=lambda m: m.author.id == self.bot.user.id)
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention}!",
                            ctx.guild.id,
                        )

                    channels = set(
                        self.bot.configs[ctx.guild.id]["tickets"][
                            "tickets_category"
                        ].channels
                    )

                    if ctx.guild.me.permissions_in(
                        self.bot.configs[ctx.guild.id]["tickets"]["tickets_category"]
                    ).manage_channels:
                        for channel in channels:
                            await channel.delete(
                                reason=f"Tickets turned off by {ctx.author}!"
                            )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to delete channels from the category {self.bot.configs[ctx.guild.id]['tickets']['tickets_category'].mention}!",
                            ctx.guild.id,
                        )

                    self.bot.ticket_repo.purge_tickets(ctx.guild.id)
                    self.bot.config_repo.remove_tickets(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["tickets"]

                await ctx.send(
                    f"ℹ️ - The tickets are now `{BOOL2VAL[val] if option not in ('update', 'resolve') else ('UPDATED' if option == 'update' else 'RESOLVED')}` in this guild!"
                    + (
                        " Parameters: "
                        + f"\n'tickets_channel': {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[ctx.guild.id]['tickets'] else '`No channel specified.`'}"
                        + f"\n'tickets_category': {self.bot.configs[ctx.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[ctx.guild.id]['tickets'] else '`No category specified.`'}"
                        if "tickets" in self.bot.configs[ctx.guild.id]
                        and option != "resolve"
                        else ""
                    )
                )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {f'setting the tickets `{BOOL2VAL[val]}`' if option != 'update' else 'updating the tickets'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The tickets are currently `{BOOL2VAL['tickets' in self.bot.configs[ctx.guild.id]]}` in this guild!"
                + (
                    " Parameters: "
                    + f"\n'tickets_channel': {self.bot.configs[ctx.guild.id]['tickets']['tickets_channel'].mention if 'tickets_channel' in self.bot.configs[ctx.guild.id]['tickets'] else '`No channel specified.`'}"
                    + f"\n'tickets_category': {self.bot.configs[ctx.guild.id]['tickets']['tickets_category'].mention if 'tickets_category' in self.bot.configs[ctx.guild.id]['tickets'] else '`No category specified.`'}"
                    if "tickets" in self.bot.configs[ctx.guild.id]
                    else ""
                )
            )

    @config_group.command(
        pass_context=True,
        name="select_to_role",
        aliases=["select_2_role", "select2role"],
        brief="🥸",
        description="This option manage the server's server_2_role feature!",
        usage='add|update|resolve|remove|purge "Title" @role',
    )
    async def config_select_2_role_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        title: str = None,
        role: Role = None,
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
                            "select2role" in self.bot.configs[ctx.guild.id]
                            and "selects"
                            in self.bot.configs[ctx.guild.id]["select2role"]
                            and title
                            in set(
                                self.bot.configs[ctx.guild.id]["select2role"]["selects"]
                            )
                            and option != "update"
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The title `{title}` is already assigned to a role! Value: `@{self.bot.configs[ctx.guild.id]['select2role']['selects'][title]}`",
                                delete_after=20,
                            )
                        elif (
                            "select2role" in self.bot.configs[ctx.guild.id]
                            and "selects"
                            in self.bot.configs[ctx.guild.id]["select2role"]
                            and role
                            in set(
                                self.bot.configs[ctx.guild.id]["select2role"][
                                    "selects"
                                ].values()
                            )
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a title! Title: `{list(self.bot.configs[ctx.guild.id]['select2role']['selects'].keys())[list(self.bot.configs[ctx.guild.id]['select2role']['selects'].values()).index(role)]}`",
                                delete_after=20,
                            )
                        elif "lvl2role" in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] and role in set(
                            self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].values()
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a level! Level: `{list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].values()).index(role)]}`",
                                delete_after=20,
                            )
                        elif "prestiges" in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] and role in set(
                            self.bot.configs[ctx.guild.id]["xp"]["prestiges"].values()
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a prestige! Prestige: `{list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].values()).index(role)]}`",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_select2role(
                            ctx.guild.id, title, f"{role}", role.id
                        )

                        if "select2role" not in self.bot.configs[ctx.guild.id]:
                            self.bot.configs[ctx.guild.id]["select2role"] = {
                                "selects": {}
                            }
                        elif (
                            "selects"
                            not in self.bot.configs[ctx.guild.id]["select2role"]
                        ):
                            self.bot.configs[ctx.guild.id]["select2role"][
                                "selects"
                            ] = {}

                        self.bot.configs[ctx.guild.id]["select2role"]["selects"][
                            title
                        ] = role

                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the title `{title}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the select to role list."
                        )
                    elif option == "remove":
                        if (
                            "select2role" not in self.bot.configs[ctx.guild.id]
                            or "selects"
                            not in self.bot.configs[ctx.guild.id]["select2role"]
                            or title
                            not in set(
                                self.bot.configs[ctx.guild.id]["select2role"]["selects"]
                            )
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The title `{title}` is already not in the select to role list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_select2role(ctx.guild.id, title)
                        role = self.bot.configs[ctx.guild.id]["select2role"][
                            "selects"
                        ].pop(title)
                        await ctx.send(
                            f"ℹ️ - Removed the title `{title}` which was corresponding to the role `@{role}` from the select to role list."
                        )

                        if not self.bot.configs[ctx.guild.id]["select2role"]["selects"]:
                            del self.bot.configs[ctx.guild.id]["select2role"]["selects"]

                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot:
                                    continue

                                try:
                                    await member.remove_roles(role)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove this role `@{role.name}` from {member} (maybe the role is above mine)"
                                    raise
                elif option == "resolve":
                    await ctx.send(
                        f"ℹ️ - Resolved the select2role message successfully."
                    )
                elif option == "purge":
                    if (
                        "select2role" not in self.bot.configs[ctx.guild.id]
                        or "selects"
                        not in self.bot.configs[ctx.guild.id]["select2role"]
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The select to role list is already empty!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_select2role(ctx.guild.id)
                    roles = set(
                        self.bot.configs[ctx.guild.id]["select2role"][
                            "selects"
                        ].values()
                    )
                    del self.bot.configs[ctx.guild.id]["select2role"]["selects"]
                    await ctx.send(
                        f"ℹ️ - Removed all the titles from the select to role list."
                    )

                    members = set(ctx.guild.members)
                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot:
                                    continue

                                try:
                                    await member.remove_roles(*roles)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in roles])} from {member} (maybe one of them is above mine)"
                                    raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{role.name}` (i tried to remove the old level role from members)!",
                            ctx.guild.id,
                        )
                else:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if "channel" in self.bot.configs[ctx.guild.id]["select2role"]:
                    roles_msg = None

                    if "roles_msg_id" in self.bot.configs[ctx.guild.id]["select2role"]:
                        try:
                            roles_msg = await self.bot.configs[ctx.guild.id][
                                "select2role"
                            ]["channel"].fetch_message(
                                self.bot.configs[ctx.guild.id]["select2role"][
                                    "roles_msg_id"
                                ]
                            )
                        except NotFound:
                            pass

                    em = Embed(
                        colour=self.bot.color,
                        title="Roles",
                        description="Here are the server's select to role available, choose one or more roles you wish to be assigned.\n\n**If you want the role to be removed, deselect the corresponding role!**",
                    )

                    em.set_thumbnail(url=ctx.guild.icon_url)
                    em.set_footer(
                        text=self.bot.user.name, icon_url=self.bot.user.avatar_url
                    )
                    em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

                    options = []
                    if (
                        "select2role" in self.bot.configs[ctx.guild.id]
                        and "selects" in self.bot.configs[ctx.guild.id]["select2role"]
                    ):
                        em.add_field(
                            name="Available roles:",
                            value="\n".join(
                                [
                                    f"{title}: `@{role.name}`"
                                    for title, role in self.bot.configs[ctx.guild.id][
                                        "select2role"
                                    ]["selects"].items()
                                ]
                            ),
                        )

                        for title, role in self.bot.configs[ctx.guild.id][
                            "select2role"
                        ]["selects"].items():
                            options.append(
                                SelectOption(
                                    label=title, value=role.name, default=False
                                )
                            )
                    else:
                        em.add_field(
                            name="Information", value="For now no roles are available!"
                        )

                    if roles_msg:
                        await roles_msg.edit(
                            content=None,
                            embed=em,
                            components=[
                                SelectMenu(
                                    options=options,
                                    custom_id=f"{self.bot.configs[ctx.guild.id]['select2role']['channel'].id}",
                                    placeholder="Choose one or more role!",
                                    min_values=0,
                                    max_values=len(options),
                                )
                            ]
                            if options
                            else None,
                        )
                    else:
                        if self.bot.configs[ctx.guild.id]["select2role"][
                            "channel"
                        ].can_send:
                            self.bot.configs[ctx.guild.id]["select2role"][
                                "roles_msg_id"
                            ] = (
                                await self.bot.configs[ctx.guild.id]["select2role"][
                                    "channel"
                                ].send(
                                    content=None,
                                    embed=em,
                                    components=[
                                        SelectMenu(
                                            options=options,
                                            custom_id=f"{self.bot.configs[ctx.guild.id]['select2role']['channel'].id}",
                                            placeholder="Choose one or more role!",
                                            min_values=0,
                                            max_values=len(options),
                                        )
                                    ]
                                    if options
                                    else None,
                                )
                            ).id
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[ctx.guild.id]['select2role']['channel'].mention} (i tried to send the message that allow users to select a role so please reactivate this feature after changing the permissions)!",
                                ctx.guild.id,
                            )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the value `{title}` {'to' if option != 'update' else 'from'} the select to role message! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if (
                "select2role" not in self.bot.configs[ctx.guild.id]
                or "selects" not in self.bot.configs[ctx.guild.id]["select2role"]
            ):
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No select to role have been added to the list yet!",
                    delete_after=20,
                )

            server_select_2_role = self.bot.configs[ctx.guild.id]["select2role"][
                "selects"
            ]
            roles_mess = ""
            for key in sorted(server_select_2_role):
                roles_mess += f"`{key}` = `@{server_select_2_role[key]}`\n"
            await ctx.send(
                f"**ℹ️ - Here's the list of the server's select to role:**\n\n{roles_mess}"
            )

    @config_group.command(
        pass_context=True,
        name="muted_role",
        aliases=["mute_role"],
        brief="🤐",
        description="This option manage the server's muted role",
        usage="set|remove @role",
    )
    async def config_djs_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                    elif (
                        "muted_role" in self.bot.configs[ctx.guild.id]
                        and self.bot.configs[ctx.guild.id]["muted_role"] == muted
                    ):
                        return await ctx.reply(
                            f"ℹ️ - This role is already the one configured has the muted role!",
                            delete_after=20,
                        )

                    old_role = None
                    if "muted_role" in self.bot.configs[ctx.guild.id]:
                        old_role = self.bot.configs[ctx.guild.id]["muted_role"]

                    self.bot.config_repo.set_muted_role(ctx.guild.id, muted.id)
                    self.bot.configs[ctx.guild.id]["muted_role"] = muted

                    await ctx.send(
                        f"ℹ️ - The muted role is now `@{muted}` in this guild!"
                    )

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        db_users = self.bot.user_repo.get_users(ctx.guild.id)
                        for db_user in db_users.values():
                            if db_user["muted"]:
                                try:
                                    member = await ctx.guild.try_member(
                                        int(db_user["id"])
                                    )
                                except NotFound:
                                    continue

                                if old_role:
                                    try:
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
                            f"⚠️ - I don't have the right permissions to manage these roles {f'`@{old_role.name}` ' if old_role else ''}`@{muted.name}` (i tried to replace the old muted role with the new one from muted members)!",
                            ctx.guild.id,
                        )
                elif option == "remove":
                    if "muted_role" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - The server already doesn't have a muted role configured!",
                            delete_after=20,
                        )

                    old_role = self.bot.configs[ctx.guild.id]["muted_role"]
                    self.bot.config_repo.set_muted_role(ctx.guild.id, None)
                    del self.bot.configs[ctx.guild.id]["muted_role"]

                    await ctx.send(
                        f"ℹ️ - The muted role is now removed from this guild!"
                    )

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        db_users = self.bot.user_repo.get_users(ctx.guild.id)
                        for db_user in db_users.values():
                            if db_user["muted"]:
                                try:
                                    member = await ctx.guild.try_member(
                                        int(db_user["id"])
                                    )
                                except NotFound:
                                    continue

                                try:
                                    await member.remove_roles(*old_role)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)"
                                    raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{old_role.name}` (i tried to remove the old muted role from muted members)!",
                            ctx.guild.id,
                        )
                else:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadArgument:
                raise BadArgument
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while configuring the muted_role! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - The current server's muted role is: `@{self.bot.configs[ctx.guild.id]['muted_role']}`"
                if "muted_role" in self.bot.configs[ctx.guild.id]
                else f"ℹ️ - The server doesn't have a muted role yet!"
            )

    """ MAIN GROUP'S SECURITY COMMAND(S) """

    @config_security_group.command(
        pass_context=True,
        name="prevent_invites",
        aliases=["prev_i"],
        brief="✉️",
        description="This option manage if users are allowed to send other servers invites or not (specify a channel to be notified when someone tries to send an invitation link)!",
        usage="(on|update|off) (#channel)",
    )
    async def config_security_prevent_invites_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "prevent_invites" in self.bot.configs[ctx.guild.id]
                ) == val and option != "update":
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The invites prevention is already set to `{BOOL2VAL[val]}`!"
                        + f" Parameters: 'notify_channel': {self.bot.configs[ctx.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                        if "prevent_invites" in self.bot.configs[ctx.guild.id]
                        else ""
                    )

                if val:
                    self.bot.config_repo.set_invite_prevention(
                        ctx.guild.id, notify_channel.id if notify_channel else None
                    )
                    self.bot.configs[ctx.guild.id]["prevent_invites"] = {"is_on": True}

                    if notify_channel:
                        self.bot.configs[ctx.guild.id]["prevent_invites"][
                            "notify_channel"
                        ] = notify_channel
                else:
                    self.bot.config_repo.remove_invite_prevention(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["prevent_invites"]

                await ctx.send(
                    f"ℹ️ - The invites prevention is now `{BOOL2VAL[val] if option != 'update' else 'UPDATED'}` in this guild!"
                    + (
                        f" Parameters: 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
                        if val
                        else ""
                    )
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {f'setting the invites prevention `{BOOL2VAL[val]}`' if option != 'update' else 'updating the invites prevention'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The invites prevention is currently `{BOOL2VAL['prevent_invites' in self.bot.configs[ctx.guild.id]]}` in this guild!"
                + f" Parameters: 'notify_channel': {self.bot.configs[ctx.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                if "prevent_invites" in self.bot.configs[ctx.guild.id]
                else ""
            )

    @config_security_group.command(
        pass_context=True,
        name="mute_on_join",
        aliases=["m_on_j"],
        brief="🔇",
        description="This option manage if users are muted during a certain amount of time when joining the server and then notify it at the end if a channel is specified! (default duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
        usage="(on|update|off) (<duration_value> <duration_type> #channel)",
    )
    async def config_security_mute_on_join_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        _duration: int = None,
        duration_type: str = None,
        notify_channel: TextChannel = None,
    ):
        if "muted_role" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The server doesn't have a muted role yet! Please configure one with the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}config muted_role` to set one!",
                delete_after=20,
            )

        if option:
            try:
                val = False
                if option in ("on", "update"):
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "mute_on_join" in self.bot.configs[ctx.guild.id]
                ) == val and option != "update":
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The mute on join is already `{BOOL2VAL[val]}`!"
                        + (
                            f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[ctx.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[ctx.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                            if "mute_on_join" in self.bot.configs[ctx.guild.id]
                            else ""
                        ),
                        delete_after=20,
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
                        _duration, duration_type, ctx
                    )
                    if not _duration:
                        return

                    self.bot.config_repo.set_mute_on_join(
                        ctx.guild.id,
                        _duration,
                        notify_channel.id if notify_channel else None,
                    )
                    self.bot.configs[ctx.guild.id]["mute_on_join"] = {
                        "duration": _duration,
                    }

                    if notify_channel:
                        self.bot.configs[ctx.guild.id]["mute_on_join"][
                            "notify_channel"
                        ] = notify_channel
                else:
                    self.bot.config_repo.remove_mute_on_join(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["mute_on_join"]

                await ctx.send(
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
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {f'setting the mute on join `{BOOL2VAL[val]}`' if option != 'update' else 'updating the mute on join'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The mute on join is currently `{BOOL2VAL['mute_on_join' in self.bot.configs[ctx.guild.id]]}` in this guild!"
                + (
                    f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[ctx.guild.id]['mute_on_join']['duration'])}`, 'notify_channel': {self.bot.configs[ctx.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                    if "mute_on_join" in self.bot.configs[ctx.guild.id]
                    else ""
                )
            )

    """ MAIN GROUP'S XP COMMAND(S) """

    @config_xp_group.command(
        pass_context=True,
        name="switch",
        brief="➕",
        description="This option turn the server's experience feature on or off",
        usage="(on|off)",
    )
    async def config_xp_switch_command(
        self, ctx: Context, option: Utils.to_lower = None
    ):
        if option:
            try:
                val = False
                if option == "on":
                    val = True
                elif option == "off":
                    val = False
                else:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if self.bot.configs[ctx.guild.id]["xp"]["is_on"] == val:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The xp is already `{BOOL2VAL[val]}`!",
                        delete_after=20,
                    )

                self.bot.config_repo.set_xp(ctx.guild.id, val)
                self.bot.configs[ctx.guild.id]["xp"]["is_on"] = val
                await ctx.send(f"ℹ️ - The xp is now `{BOOL2VAL[val]}` in this guild!")
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while setting the xp `{BOOL2VAL[val]}`! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The xp is currently `{BOOL2VAL[self.bot.configs[ctx.guild.id]['xp']['is_on']]}` in this guild!"
            )

    @config_xp_group.command(
        pass_context=True,
        name="boost",
        aliases=["boosts", "boosted", "boosteds"],
        brief="🔋",
        description="This option manage the server's boosted roles | members, you can precise what xp bonus they'll get (default = 20%)",
        usage="add|update|remove|purge @role|@member (<bonus>)",
    )
    async def config_xp_boost_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        boosted: Union[Role, Member] = None,
        bonus: int = 20,
    ):
        if option:
            try:
                if option in ("add", "update", "remove"):
                    if not boosted:
                        raise MissingRequiredArgument(
                            param=Parameter(name="boosted", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif isinstance(boosted, Member) and boosted.bot:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - You can't add a bot user to the boosted xp list!",
                            delete_after=20,
                        )

                    if option == "add" or option == "update":
                        if (
                            "boosteds" in self.bot.configs[ctx.guild.id]["xp"]
                            and str(boosted.id)
                            in set(self.bot.configs[ctx.guild.id]["xp"]["boosteds"])
                            and option != "update"
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already in the boosted xp list!",
                                delete_after=20,
                            )

                        if bonus <= 0:
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The bonus value must be greater than 0!",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_xp_boosted(
                            ctx.guild.id,
                            boosted.id,
                            f"{boosted}",
                            bonus,
                            type(boosted).__name__,
                        )

                        if "boosteds" not in self.bot.configs[ctx.guild.id]["xp"]:
                            self.bot.configs[ctx.guild.id]["xp"]["boosteds"] = {}

                        self.bot.configs[ctx.guild.id]["xp"]["boosteds"][
                            str(boosted.id)
                        ] = bonus

                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Updated'} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option == 'add' else 'from'} the boosted xp list. Bonus: `{bonus}%`"
                        )
                    elif option == "remove":
                        if "boosteds" not in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] or str(boosted.id) not in set(
                            self.bot.configs[ctx.guild.id]["xp"]["boosteds"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} is already not in the boosted xp list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_xp_boosted(ctx.guild.id, boosted.id)
                        del self.bot.configs[ctx.guild.id]["xp"]["boosteds"][
                            str(boosted.id)
                        ]

                        try:
                            await ctx.send(
                                f"ℹ️ - Removed `@{await ctx.guild.try_member(int(boosted.id)) if isinstance(boosted, Member) else ctx.guild.get_role(int(boosted.id))}` {'role' if isinstance(boosted, Role) else 'member'} from the boosted xp list."
                            )
                        except NotFound:
                            pass

                        if not self.bot.configs[ctx.guild.id]["xp"]["boosteds"]:
                            del self.bot.configs[ctx.guild.id]["xp"]["boosteds"]
                elif option == "purge":
                    if "boosteds" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The boosteds list is already empty!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_xp_boosted(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["xp"]["boosteds"]
                    await ctx.send(
                        f"ℹ️ - Removed all the Roles & Members from the boosteds list."
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option != 'update' else 'from'} the boosters list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_boosteds = self.bot.config_repo.get_xp_boosted(ctx.guild.id).values()
            if not server_boosteds:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No boosted (members & roles) have been added to the list yet!",
                    delete_after=20,
                )
            server_boosteds_roles = []
            server_boosteds_members = []
            for m in server_boosteds:
                if m["type"] == "Role":
                    server_boosteds_roles.append([m["name"], m["bonus"]])
                else:
                    server_boosteds_members.append([m["name"], m["bonus"]])
            await ctx.send(
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

    @config_xp_group.command(
        pass_context=True,
        name="max_lvl",
        aliases=["mx_lvl"],
        brief="🛑",
        description="This option manage the server's max level",
        usage="(<number of levels>)",
    )
    async def config_xp_max_lvl_command(self, ctx: Context, max_lvl: int = None):
        try:
            if max_lvl:
                if max_lvl <= 0:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The max level value must be greater than 0!",
                        delete_after=20,
                    )
                elif max_lvl == self.bot.configs[ctx.guild.id]["xp"]["max_lvl"]:
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The max level value is already the one configured for this server! Value: `{max_lvl}`",
                        delete_after=20,
                    )

                self.bot.config_repo.set_xp_max_lvl(ctx.guild.id, max_lvl)
                self.bot.configs[ctx.guild.id]["xp"]["max_lvl"] = max_lvl
                await ctx.send(f"ℹ️ - The max level is now `{max_lvl}` in this guild!")

                members = set(ctx.guild.members)
                for member in members:
                    db_user = self.bot.user_repo.get_user(ctx.guild.id, member.id)
                    if int(db_user["level"]) > max_lvl:
                        self.bot.user_repo.set_levels(ctx.guild.id, member.id, max_lvl)
            else:
                await ctx.send(
                    f"ℹ️ - The current server's max level is: `{self.bot.configs[ctx.guild.id]['xp']['max_lvl']}`"
                )
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occurred while setting the server's max level! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_xp_group.command(
        pass_context=True,
        name="level_to_role",
        aliases=["level_2_role", "lvl_to_role", "lvl_2_role", "l_2_r"],
        brief="🎭",
        description="This option manage the server's level to role",
        usage="add|update|remove|purge <level value> @role",
    )
    async def config_xp_lvl2role_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The level value must be greater than 0!",
                            delete_after=20,
                        )

                    if option == "add" or option == "update":
                        if not role:
                            raise MissingRequiredArgument(
                                param=Parameter(
                                    name="role", kind=Parameter.KEYWORD_ONLY
                                )
                            )

                        if (
                            "lvl2role" in self.bot.configs[ctx.guild.id]["xp"]
                            and lvl
                            in set(self.bot.configs[ctx.guild.id]["xp"]["lvl2role"])
                            and option != "update"
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The level `{lvl}` is already assigned to a role! Value: `@{self.bot.configs[ctx.guild.id]['xp']['lvl2role'][lvl]}`",
                                delete_after=20,
                            )
                        elif "lvl2role" in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] and role in set(
                            self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].values()
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a level! Level: `{list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].values()).index(role)]}`",
                                delete_after=20,
                            )
                        elif "prestiges" in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] and role in set(
                            self.bot.configs[ctx.guild.id]["xp"]["prestiges"].values()
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a prestige! Prestige: `{list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].values()).index(role)]}`",
                                delete_after=20,
                            )
                        elif (
                            "select2role" in self.bot.configs[ctx.guild.id]
                            and "selects"
                            in self.bot.configs[ctx.guild.id]["select2role"]
                            and role
                            in set(
                                self.bot.configs[ctx.guild.id]["select2role"][
                                    "selects"
                                ].values()
                            )
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a title! Title: `{list(self.bot.configs[ctx.guild.id]['select2role']['selects'].keys())[list(self.bot.configs[ctx.guild.id]['select2role']['selects'].values()).index(role)]}`",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_xp_lvl2role(
                            ctx.guild.id, lvl, f"{role}", role.id
                        )

                        if "lvl2role" not in self.bot.configs[ctx.guild.id]["xp"]:
                            self.bot.configs[ctx.guild.id]["xp"]["lvl2role"] = {}

                        self.bot.configs[ctx.guild.id]["xp"]["lvl2role"][lvl] = role

                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Updated'} the level `{lvl}` corresponding to the `@{role}` role {'to' if option == 'add' else 'from'} the level to role list."
                        )

                        db_users = self.bot.user_repo.get_users(ctx.guild.id)
                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot:
                                    continue

                                await self.xp_class.manage_levels(
                                    member,
                                    db_users[str(member.id)]["level"],
                                    "new_r_2_l",
                                )
                    elif option == "remove":
                        if "lvl2role" not in self.bot.configs[ctx.guild.id][
                            "xp"
                        ] or lvl not in set(
                            self.bot.configs[ctx.guild.id]["xp"]["lvl2role"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - The level `{lvl}` is already not in the level to role list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_xp_lvl2role(ctx.guild.id, lvl)
                        role = self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].pop(lvl)
                        await ctx.send(
                            f"ℹ️ - Removed the level `{lvl}` which was corresponding to the role `@{role}` from the level to role list."
                        )

                        if not self.bot.configs[ctx.guild.id]["xp"]["lvl2role"]:
                            del self.bot.configs[ctx.guild.id]["xp"]["lvl2role"]

                        if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                            members = set(ctx.guild.members)
                            async with self.bot.limiter:
                                for member in members:
                                    if member.bot:
                                        continue

                                    try:
                                        await member.remove_roles(role)
                                    except Forbidden as f:
                                        f.text = f"⚠️ - I don't have the right permissions to remove this role `@{role.name}` from {member} (maybe the role is above mine)"
                                        raise
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to manage this role `@{role.name}` (i tried to remove the old level role from members)!",
                                ctx.guild.id,
                            )
                elif option == "purge":
                    if "lvl2role" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The level to role list is already empty!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_xp_lvl2role(ctx.guild.id)
                    roles = set(
                        self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].values()
                    )
                    del self.bot.configs[ctx.guild.id]["xp"]["lvl2role"]
                    await ctx.send(
                        f"ℹ️ - Removed all the levels from the level to role list."
                    )

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot:
                                    continue

                                try:
                                    await member.remove_roles(*roles)
                                except Forbidden as f:
                                    f.text = f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in roles])} from {member} (maybe one of them is above mine)"
                                    raise
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles {', '.join([f'`@{role.name}`' for role in roles])} (i tried to remove the old level roles from members)!",
                            ctx.guild.id,
                        )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the level `{lvl}` {'to' if option != 'update' else 'from'} the level to role list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if "lvl2role" not in self.bot.configs[ctx.guild.id]["xp"]:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No levels to role have been added to the list yet!",
                    delete_after=20,
                )

            server_lvls_2_role = self.bot.configs[ctx.guild.id]["xp"]["lvl2role"]
            roles_mess = ""
            for key in sorted(server_lvls_2_role):
                roles_mess += f"level `{key}` = `@{server_lvls_2_role[key]}`\n"
            await ctx.send(
                f"**ℹ️ - Here's the list of the server's levels to role:**\n\n{roles_mess}"
            )

    @config_xp_group.command(
        pass_context=True,
        name="prestiges",
        aliases=["prestg", "prestige"],
        brief="💫",
        description="This option manage the server's prestiges",
        usage="add|update|remove|purge @role <prestige_value>",
    )
    async def config_xp_prestiges_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                    elif "prestiges" in self.bot.configs[ctx.guild.id][
                        "xp"
                    ] and role in set(
                        self.bot.configs[ctx.guild.id]["xp"]["prestiges"].values()
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a prestige! Prestige: `{list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].values()).index(role)]}`",
                            delete_after=20,
                        )
                    elif "lvl2role" in self.bot.configs[ctx.guild.id][
                        "xp"
                    ] and role in set(
                        self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].values()
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a level! Level: `{list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].values()).index(role)]}`",
                            delete_after=20,
                        )
                    elif (
                        "select2role" in self.bot.configs[ctx.guild.id]
                        and "selects" in self.bot.configs[ctx.guild.id]["select2role"]
                        and role
                        in set(
                            self.bot.configs[ctx.guild.id]["select2role"][
                                "selects"
                            ].values()
                        )
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a title! Title: `{list(self.bot.configs[ctx.guild.id]['select2role']['selects'].keys())[list(self.bot.configs[ctx.guild.id]['select2role']['selects'].values()).index(role)]}`",
                            delete_after=20,
                        )

                    if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
                        self.bot.configs[ctx.guild.id]["xp"]["prestiges"] = {}

                    prestige = (
                        len(self.bot.configs[ctx.guild.id]["xp"]["prestiges"]) + 1
                    )

                    self.bot.config_repo.add_xp_prestiges(
                        ctx.guild.id, f"p_{prestige}", f"{role}", role.id
                    )

                    self.bot.configs[ctx.guild.id]["xp"]["prestiges"][prestige] = role

                    await ctx.send(
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
                    elif "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No prestiges have been added to the list yet!",
                            delete_after=20,
                        )
                    elif (
                        role
                        in set(
                            self.bot.configs[ctx.guild.id]["xp"]["prestiges"].values()
                        )
                        and prestige
                        == list(
                            self.bot.configs[ctx.guild.id]["xp"]["prestiges"].keys()
                        )[
                            list(
                                self.bot.configs[ctx.guild.id]["xp"][
                                    "prestiges"
                                ].values()
                            ).index(role)
                        ]
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The prestige `{prestige}` already have the role `@{role}` assigned!",
                            delete_after=20,
                        )
                    elif role in set(
                        self.bot.configs[ctx.guild.id]["xp"]["prestiges"].values()
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a prestige! Prestige: `{list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['prestiges'].values()).index(role)]}`",
                            delete_after=20,
                        )
                    elif "lvl2role" in self.bot.configs[ctx.guild.id][
                        "xp"
                    ] and role in set(
                        self.bot.configs[ctx.guild.id]["xp"]["lvl2role"].values()
                    ):
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The role `@{role}` is already assigned to a level! Level: `{list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].keys())[list(self.bot.configs[ctx.guild.id]['xp']['lvl2role'].values()).index(role)]}`",
                            delete_after=20,
                        )

                    old_role = self.bot.configs[ctx.guild.id]["xp"]["prestiges"][
                        prestige
                    ]

                    self.bot.config_repo.add_xp_prestiges(
                        ctx.guild.id, f"p_{prestige}", f"{role}", role.id
                    )
                    self.bot.configs[ctx.guild.id]["xp"]["prestiges"][prestige] = role

                    await ctx.send(
                        f"ℹ️ - Updated the prestige `{prestige}` corresponding to the `@{role}` role from the prestiges list."
                    )

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
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
                            f"⚠️ - I don't have the right permissions to manage these roles `@{old_role.name}`, `@{role.name}` (i tried to replace the old prestige role with the new one from members)!",
                            ctx.guild.id,
                        )
                elif option == "remove":
                    if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No prestiges have been added to the list yet!"
                        )

                    prestige = len(self.bot.configs[ctx.guild.id]["xp"]["prestiges"])
                    old_role = self.bot.configs[ctx.guild.id]["xp"]["prestiges"][
                        prestige
                    ]
                    self.bot.config_repo.remove_xp_prestiges(ctx.guild.id)
                    await ctx.send(
                        f"ℹ️ - Removed the prestige `{prestige}` which was corresponding to the `@{self.bot.configs[ctx.guild.id]['xp']['prestiges'].pop(len(self.bot.configs[ctx.guild.id]['xp']['prestiges']))}` role from the prestiges list."
                    )

                    if not self.bot.configs[ctx.guild.id]["xp"]["prestiges"]:
                        del self.bot.configs[ctx.guild.id]["xp"]["prestiges"]

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot or old_role not in member.roles:
                                    continue

                                try:
                                    await member.remove_roles(old_role)
                                except Forbidden:
                                    await self.bot.utils_class.send_message_to_mods(
                                        f"⚠️ - I don't have the right permissions to remove the role `{old_role}` from {member} (maybe the role is above mine)",
                                        ctx.guild.id,
                                    )

                                await self.xp_class.manage_prestige(
                                    member, "removed_prestige"
                                )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage this role `@{old_role.name}` (i tried to remove the old prestige role from members)!",
                            ctx.guild.id,
                        )
                elif option == "purge":
                    if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - The prestiges list is already empty!",
                            delete_after=20,
                        )

                    old_roles = self.bot.configs[ctx.guild.id]["xp"][
                        "prestiges"
                    ].values()
                    self.bot.config_repo.purge_xp_prestiges(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["xp"]["prestiges"]
                    await ctx.send(
                        f"ℹ️ - Removed all the prestiges from the prestiges list."
                    )

                    if ctx.guild.me.permissions_in(ctx.channel).manage_roles:
                        members = set(ctx.guild.members)
                        async with self.bot.limiter:
                            for member in members:
                                if member.bot or not set(member.roles) & set(old_roles):
                                    continue

                                try:
                                    await member.remove_roles(*old_roles)
                                except Forbidden:
                                    await self.bot.utils_class.send_message_to_mods(
                                        f"⚠️ - I don't have the right permissions to remove one of these roles {', '.join([f'`@{role.name}`' for role in old_roles])} from {member} (maybe one of these roles is above mine)",
                                        ctx.guild.id,
                                    )

                                await self.xp_class.manage_prestige(
                                    member, "purged_prestiges"
                                )
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to manage these roles {', '.join([f'`@{role.name}`' for role in old_roles])} (i tried to remove the prestige level roles from members)!",
                            ctx.guild.id,
                        )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the prestige `{prestige}` {'to' if option != 'update' else 'from'} the prestiges list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            if "prestiges" not in self.bot.configs[ctx.guild.id]["xp"]:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No prestiges have been added to the list yet!",
                    delete_after=20,
                )

            server_prestiges = self.bot.configs[ctx.guild.id]["xp"]["prestiges"]
            roles_mess = ""
            for key in sorted(server_prestiges):
                roles_mess += f"prestige `{key}` = `@{server_prestiges[key]}`\n"
            await ctx.send(
                f"**ℹ️ - Here's the list of the server's prestiges:**\n\n{roles_mess}"
            )

    """ MAIN GROUP'S CHANNELS COMMANDS """

    @config_channels_group.command(
        pass_context=True,
        name="commands_channels",
        aliases=["command_channels", "command_channel", "cmds_chans"],
        brief="🕹️",
        description="This option manage the server's commands channels  (if there is no commands channel then commands can be used everywhere) (can add/remove multiple at a time)",
        usage="add|remove|purge (#channels)",
    )
    async def config_channels_commands_channels_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                                ctx.guild.id
                            ] and channel.id in set(
                                self.bot.configs[ctx.guild.id]["commands_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.add_commands_channel(
                                ctx.guild.id, channel.id, f"{channel}"
                            )

                            if (
                                "commands_channels"
                                not in self.bot.configs[ctx.guild.id]
                            ):
                                self.bot.configs[ctx.guild.id]["commands_channels"] = []

                            self.bot.configs[ctx.guild.id]["commands_channels"].append(
                                channel.id
                            )
                        elif option == "remove":
                            if "commands_channels" in self.bot.configs[
                                ctx.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[ctx.guild.id]["commands_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_commands_channel(
                                ctx.guild.id, channel.id
                            )
                            del self.bot.configs[ctx.guild.id]["commands_channels"][
                                self.bot.configs[ctx.guild.id][
                                    "commands_channels"
                                ].index(channel.id)
                            ]

                    if dropped_channels:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the commands channels list!",
                            delete_after=20,
                        )

                        if not self.bot.configs[ctx.guild.id]["commands_channels"]:
                            del self.bot.configs[ctx.guild.id]["commands_channels"]

                    if channels:
                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the commands channels list!."
                        )
                elif option == "purge":
                    if "commands_channels" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No commands channels have been added to the list yet!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_commands_channels(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["commands_channels"]
                    await ctx.send(
                        f"ℹ️ - Removed all the commands channels from the list!."
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} {channel.mention} to the commands channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_commands_channels = self.bot.config_repo.get_commands_channels(
                ctx.guild.id
            ).keys()
            if not server_commands_channels:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No commands channels have been added to the list yet!",
                    delete_after=20,
                )
            await ctx.send(
                f"**ℹ️ - Here's the list of the server's commands channels:** {', '.join([ctx.guild.get_channel(int(c)).mention for c in server_commands_channels])}"
            )

    @config_channels_group.command(
        pass_context=True,
        name="music_channels",
        aliases=["music_channel" "music_chans"],
        brief="🎶",
        description="This option manage the server's music channels  (if there is no music channel then music can be listened everywhere) (can add/remove multiple at a time)",
        usage="add|remove|purge (#voice_channels|<voice_channels_name>)",
    )
    async def config_channels_music_channels_command(
        self, ctx: Context, option: Utils.to_lower = None, *channels: VoiceChannel
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
                                ctx.guild.id
                            ] and channel.id in set(
                                self.bot.configs[ctx.guild.id]["music_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue
                            elif channel == ctx.guild.afk_channel:
                                del channels[channels.index(channel)]
                                afk_channel = channel
                                continue

                            self.bot.config_repo.add_music_channel(
                                ctx.guild.id, channel.id, f"{channel}"
                            )

                            if "music_channels" not in self.bot.configs[ctx.guild.id]:
                                self.bot.configs[ctx.guild.id]["music_channels"] = []

                            self.bot.configs[ctx.guild.id]["music_channels"].append(
                                channel.id
                            )
                        elif option == "remove":
                            if "music_channels" in self.bot.configs[
                                ctx.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[ctx.guild.id]["music_channels"]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_music_channel(
                                ctx.guild.id, channel.id
                            )
                            del self.bot.configs[ctx.guild.id]["music_channels"][
                                self.bot.configs[ctx.guild.id]["music_channels"].index(
                                    channel.id
                                )
                            ]

                    if afk_channel:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the music channels list!",
                            delete_after=20,
                        )

                        if not self.bot.configs[ctx.guild.id]["music_channels"]:
                            del self.bot.configs[ctx.guild.id]["music_channels"]

                    if dropped_channels:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the music channels list!",
                            delete_after=20,
                        )

                    if channels:
                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the music channels list!."
                        )
                elif option == "purge":
                    if "music_channels" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No music channels have been added to the list yet!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_music_channels(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["music_channels"]
                    await ctx.send(
                        f"ℹ️ - Removed all the music channels from the list!."
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} {channel.mention} to the music channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_music_channels = self.bot.config_repo.get_music_channels(
                ctx.guild.id
            ).keys()
            if not server_music_channels:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No music channels have been added to the list yet!",
                    delete_after=20,
                )
            await ctx.send(
                f"**ℹ️ - Here's the list of the server's music channels:** {', '.join([ctx.guild.get_channel(int(c)).mention for c in server_music_channels])}"
            )

    @config_channels_group.command(
        pass_context=True,
        name="xp_gain_channels",
        aliases=["xp_gain_channel"],
        brief="🌌",
        description="This option manage the server's xp gain channels (voice & text)  (if there is no xp gain channels then xp can be gained everywhere) (can add/remove multiple at a time)",
        usage="add|remove|purge (#voice_channel|<voice_channel_name>)|#TextChannel",
    )
    async def config_channels_xp_gain_channels_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        *channels: Union[VoiceChannel, TextChannel],
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
                                ctx.guild.id
                            ] and channel.id in set(
                                self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue
                            elif channel == ctx.guild.afk_channel:
                                del channels[channels.index(channel)]
                                afk_channel = channel
                                continue

                            self.bot.config_repo.add_xp_gain_channel(
                                ctx.guild.id,
                                channel.id,
                                f"{channel}",
                                type(channel).__name__,
                            )

                            if "xp_gain_channels" not in self.bot.configs[ctx.guild.id]:
                                self.bot.configs[ctx.guild.id]["xp_gain_channels"] = {}

                            if (
                                type(channel).__name__
                                not in self.bot.configs[ctx.guild.id][
                                    "xp_gain_channels"
                                ]
                            ):
                                self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ] = []

                            self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                type(channel).__name__
                            ].append(channel.id)
                        elif option == "remove":
                            if "xp_gain_channels" in self.bot.configs[
                                ctx.guild.id
                            ] and channel.id not in set(
                                self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ]
                            ):
                                del channels[channels.index(channel)]
                                dropped_channels.append(channel)
                                continue

                            self.bot.config_repo.remove_xp_gain_channel(
                                ctx.guild.id, channel.id
                            )
                            del self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                type(channel).__name__
                            ][
                                self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                    type(channel).__name__
                                ].index(channel.id)
                            ]

                    if afk_channel:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {afk_channel.mention} is an AFK channel so you can't add it to the xp gain channels list!",
                            delete_after=20,
                        )

                        if not self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                            type(channel).__name__
                        ]:
                            del self.bot.configs[ctx.guild.id]["xp_gain_channels"][
                                type(channel).__name__
                            ]

                        if not self.bot.configs[ctx.guild.id]["xp_gain_channels"]:
                            del self.bot.configs[ctx.guild.id]["xp_gain_channels"]

                    if dropped_channels:
                        await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - {', '.join([channel.mention for channel in dropped_channels])} {'is' if len(dropped_channels) == 1 else 'are'} already {'not' if option == 'remove' else ''} in the xp gain channels list!",
                            delete_after=20,
                        )

                    if channels:
                        await ctx.send(
                            f"ℹ️ - {'Added' if option == 'add' else 'Removed'} {', '.join([channel.mention for channel in channels])} {'to' if option == 'add' else 'from'} the xp gain channels list!."
                        )
                elif option == "purge":
                    if "xp_gain_channels" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - No xp gain channels have been added to the list yet!",
                            delete_after=20,
                        )

                    self.bot.config_repo.purge_xp_gain_channels(ctx.guild.id)
                    del self.bot.configs[ctx.guild.id]["xp_gain_channels"]
                    await ctx.send(
                        f"ℹ️ - Removed all the xp gain channels from the list!."
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except BadUnionArgument as bua:
                raise BadUnionArgument(
                    param=bua.param, converters=bua.converters, errors=bua.errors
                )
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occurred while {'adding' if option == 'add' else 'removing'} {channel.mention} to the xp gain channels list! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            server_xp_gain_channels = self.bot.config_repo.get_xp_gain_channels(
                ctx.guild.id
            )

            if not server_xp_gain_channels:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - No xp gain channels have been added to the list yet!",
                    delete_after=20,
                )

            server_xp_gain_channels_text = []
            server_xp_gain_channels_voice = []

            for m in server_xp_gain_channels:
                if server_xp_gain_channels[m]["type"] == "TextChannel":
                    server_xp_gain_channels_text.append(ctx.guild.get_channel(int(m)))
                else:
                    server_xp_gain_channels_voice.append(ctx.guild.get_channel(int(m)))

            await ctx.send(
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

    @config_channels_group.command(
        pass_context=True,
        name="xp_channel",
        aliases=["xp_chan"],
        brief="🌠",
        description="This option manage the server's xp channels where every xp event is sent",
        usage="set|remove #channel",
    )
    async def config_channels_xp_max_lvl_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                        "notify_channel" in self.bot.configs[ctx.guild.id]["xp"]
                        and self.bot.configs[ctx.guild.id]["xp"]["notify_channel"]
                        == xp_channel
                    ):
                        return await ctx.reply(
                            f"ℹ️ - The server's xp channel is already {xp_channel.mention}!",
                            delete_after=20,
                        )

                    self.bot.config_repo.set_xp_notify_channel(
                        ctx.guild.id, xp_channel.id
                    )
                    self.bot.configs[ctx.guild.id]["xp"]["notify_channel"] = xp_channel
                    await ctx.send(
                        f"ℹ️ - The xp channel is now {xp_channel.mention} in this guild!"
                    )
                elif option == "remove":
                    if "notify_channel" not in self.bot.configs[ctx.guild.id]["xp"]:
                        return await ctx.reply(
                            f"ℹ️ - The server already doesn't have an xp channel configured!",
                            delete_after=20,
                        )

                    self.bot.config_repo.set_xp_notify_channel(ctx.guild.id, None)
                    del self.bot.configs[ctx.guild.id]["xp"]["notify_channel"]
                    await ctx.send(
                        f"ℹ️ - This guild doesn't have an xp channel anymore!"
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                await ctx.send(
                    f"ℹ️ - The current server's xp channel is: {self.bot.configs[ctx.guild.id]['xp']['notify_channel'].mention}"
                    if "notify_channel" in self.bot.configs[ctx.guild.id]["xp"]
                    else f"ℹ️ - The server doesn't have an xp channel yet!"
                )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occurred while setting the xp channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_channels_group.command(
        pass_context=True,
        name="polls_channel",
        aliases=["polls_chan"],
        brief="📊",
        description="This option manage the server's polls channel where every polls created will be sent",
        usage="set|remove #channel",
    )
    async def config_channels_polls_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                        "polls_channel" in self.bot.configs[ctx.guild.id]
                        and self.bot.configs[ctx.guild.id]["polls_channel"]
                        == polls_channel
                    ):
                        return await ctx.reply(
                            f"ℹ️ - This channel is already the one configured to have polls sent in it!",
                            delete_after=20,
                        )
                    elif not polls_channel.can_send:
                        return await ctx.reply(
                            f"⚠️ - I don't have the right permissions to send messages in the channel {polls_channel.mention}, make sure i have the right permissions in the new polls channel before setting it!",
                            delete_after=20,
                        )

                    self.bot.config_repo.set_polls_channel(
                        ctx.guild.id, polls_channel.id
                    )
                    old_polls_channel = (
                        self.bot.configs[ctx.guild.id]["polls_channel"]
                        if "polls_channel" in self.bot.configs[ctx.guild.id]
                        else None
                    )
                    self.bot.configs[ctx.guild.id]["polls_channel"] = polls_channel
                    await ctx.send(
                        f"ℹ️ - The polls channel is now {polls_channel.mention} in this guild!"
                    )

                    if old_polls_channel:
                        polls = self.bot.poll_repo.get_polls(ctx.guild.id)

                        if len(polls) > 1 or polls and "old" not in polls:
                            if not ctx.guild.me.permissions_in(
                                old_polls_channel
                            ).manage_messages:
                                await self.bot.utils_class.send_message_to_mods(
                                    f"⚠️ - I don't have the right permissions to delete messages in the channel {old_polls_channel.mention}! (I tried to delete the old polls)",
                                    ctx.guild.id,
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

                                self.bot.poll_repo.erase_poll(ctx.guild.id, poll)
                                self.bot.configs[ctx.guild.id]["polls"][
                                    poll_msg.id
                                ].cancel()
                                del self.bot.configs[ctx.guild.id]["polls"][poll_msg.id]

                                if ctx.guild.me.permissions_in(
                                    old_polls_channel
                                ).manage_messages:
                                    await poll_msg.delete()

                                poll = polls[poll]

                                poll_msg = await self.bot.configs[ctx.guild.id][
                                    "polls_channel"
                                ].send(
                                    embed=poll_msg.embeds[0],
                                    components=poll_msg.components,
                                )

                                self.bot.poll_repo.create_poll(
                                    ctx.guild.id,
                                    poll_msg.id,
                                    poll["duration_s"]
                                    - (time() - poll["created_at_s"]),
                                    time(),
                                    poll["choices"],
                                    poll["responses"] if "responses" in poll else None,
                                )
                                poll = self.bot.poll_repo.get_poll(
                                    ctx.guild.id, poll_msg.id
                                )
                                self.bot.configs[ctx.guild.id]["polls"][
                                    poll_msg.id
                                ] = self.bot.utils_class.task_launcher(
                                    self.bot.utils_class.poll_completion,
                                    (ctx.guild, poll),
                                    count=1,
                                )
                elif option == "remove":
                    if "polls_channel" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - The server already doesn't have a polls channel configured!",
                            delete_after=20,
                        )

                    polls = self.bot.poll_repo.get_polls(ctx.guild.id)
                    if len(polls) > 1 or polls and "old" not in polls:
                        if not ctx.guild.me.permissions_in(
                            self.bot.configs[ctx.guild.id]["polls_channel"]
                        ).manage_messages:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to delete messages in the channel {self.bot.configs[ctx.guild.id]['polls_channel'].mention}! (I tried to delete the old polls)",
                                ctx.guild.id,
                            )

                        for poll in polls:
                            if poll == "old":
                                continue

                            try:
                                poll_msg = await self.bot.configs[ctx.guild.id][
                                    "polls_channel"
                                ].fetch_message(int(poll))
                            except NotFound:
                                continue

                            self.bot.poll_repo.erase_poll(ctx.guild.id, poll)
                            self.bot.configs[ctx.guild.id]["polls"][
                                poll_msg.id
                            ].cancel()
                            del self.bot.configs[ctx.guild.id]["polls"][poll_msg.id]

                            if ctx.guild.me.permissions_in(
                                self.bot.configs[ctx.guild.id]["polls_channel"]
                            ).manage_messages:
                                await poll_msg.delete()

                    self.bot.config_repo.set_polls_channel(ctx.guild.id, None)
                    del self.bot.configs[ctx.guild.id]["polls_channel"]
                    await ctx.send(
                        f"ℹ️ - This guild doesn't have a polls channel anymore!"
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                await ctx.send(
                    f"ℹ️ - The current server's polls channel is: {self.bot.configs[ctx.guild.id]['polls_channel'].mention}"
                    if "polls_channel" in self.bot.configs[ctx.guild.id]
                    else f"ℹ️ - The server doesn't have a polls channel yet!"
                )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occurred while setting the polls channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_channels_group.command(
        pass_context=True,
        name="select_to_role_channel",
        aliases=["select2role_channel"],
        brief="🤠",
        description="This option manage the server's select 2 role channels where the select to role message is sended",
        usage="set|remove #channel",
    )
    async def config_channels_select2role_channel_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                        "select2role" in self.bot.configs[ctx.guild.id]
                        and "channel" in self.bot.configs[ctx.guild.id]["select2role"]
                        and self.bot.configs[ctx.guild.id]["select2role"]["channel"]
                        == select2role_channel
                    ):
                        return await ctx.reply(
                            f"ℹ️ - The server's select to role channel is already {select2role_channel.mention}!",
                            delete_after=20,
                        )
                    elif not select2role_channel.can_send:
                        return await ctx.reply(
                            f"⚠️ - I don't have the right permissions to send messages in the channel {select2role_channel.mention}, make sure i have the right permissions in the new select to role channel before setting it!",
                            delete_after=20,
                        )

                    old_channel = None
                    if "select2role" not in self.bot.configs[ctx.guild.id]:
                        self.bot.configs[ctx.guild.id]["select2role"] = {}
                    elif "channel" in self.bot.configs[ctx.guild.id]["select2role"]:
                        old_channel = self.bot.configs[ctx.guild.id]["select2role"][
                            "channel"
                        ]

                    self.bot.configs[ctx.guild.id]["select2role"][
                        "channel"
                    ] = select2role_channel
                    await ctx.send(
                        f"ℹ️ - The select to role channel is now {select2role_channel.mention} in this guild!"
                    )

                    if old_channel:
                        if (
                            ctx.guild.me.permissions_in(
                                old_channel
                            ).read_message_history
                            and ctx.guild.me.permissions_in(old_channel).manage_messages
                        ):
                            await old_channel.purge(
                                check=lambda m: m.author.id == self.bot.user.id
                            )
                        else:
                            await self.bot.utils_class.send_message_to_mods(
                                f"⚠️ - I don't have the right permissions to purge messages in the channel {old_channel.mention}!",
                                ctx.guild.id,
                            )

                    em = Embed(
                        colour=self.bot.color,
                        title="Roles",
                        description="Here are the server's select to role available, choose one or more roles you wish to be assigned.\n\n**If you want the role to be removed, deselect the corresponding role!**",
                    )

                    em.set_thumbnail(url=ctx.guild.icon_url)
                    em.set_footer(
                        text=self.bot.user.name, icon_url=self.bot.user.avatar_url
                    )
                    em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

                    options = []
                    if (
                        "select2role" in self.bot.configs[ctx.guild.id]
                        and "selects" in self.bot.configs[ctx.guild.id]["select2role"]
                    ):
                        em.add_field(
                            name="Available roles:",
                            value="\n".join(
                                [
                                    f"{title}: `@{role.name}`"
                                    for title, role in self.bot.configs[ctx.guild.id][
                                        "select2role"
                                    ]["selects"].items()
                                ]
                            ),
                        )

                        for title, role in self.bot.configs[ctx.guild.id][
                            "select2role"
                        ]["selects"].items():
                            options.append(
                                SelectOption(
                                    label=title, value=role.name, default=False
                                )
                            )
                    else:
                        em.add_field(
                            name="Information", value="For now no roles are available!"
                        )

                    self.bot.configs[ctx.guild.id]["select2role"]["roles_msg_id"] = (
                        await self.bot.configs[ctx.guild.id]["select2role"][
                            "channel"
                        ].send(
                            content=None,
                            embed=em,
                            components=[
                                SelectMenu(
                                    options=options,
                                    custom_id=f"{self.bot.configs[ctx.guild.id]['select2role']['channel'].id}",
                                    placeholder="Choose one or more role!",
                                    min_values=0,
                                    max_values=len(options),
                                )
                            ]
                            if options
                            else None,
                        )
                    ).id

                    self.bot.config_repo.set_select2role_channel(
                        ctx.guild.id,
                        select2role_channel.id,
                        self.bot.configs[ctx.guild.id]["select2role"]["roles_msg_id"],
                    )
                elif option == "remove":
                    if (
                        "select2role" not in self.bot.configs[ctx.guild.id]
                        or "channel"
                        not in self.bot.configs[ctx.guild.id]["select2role"]
                    ):
                        return await ctx.reply(
                            f"ℹ️ - The server already doesn't have a select to role channel configured!",
                            delete_after=20,
                        )

                    if (
                        ctx.guild.me.permissions_in(
                            self.bot.configs[ctx.guild.id]["select2role"]["channel"]
                        ).read_message_history
                        and ctx.guild.me.permissions_in(
                            self.bot.configs[ctx.guild.id]["select2role"]["channel"]
                        ).manage_messages
                    ):
                        await self.bot.configs[ctx.guild.id]["select2role"][
                            "channel"
                        ].purge(check=lambda m: m.author.id == self.bot.user.id)
                    else:
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to purge messages in the channel {self.bot.configs[ctx.guild.id]['select2role']['channel'].mention}!",
                            ctx.guild.id,
                        )

                    self.bot.config_repo.set_select2role_channel(ctx.guild.id, None)
                    del self.bot.configs[ctx.guild.id]["select2role"]["channel"]
                    del self.bot.configs[ctx.guild.id]["select2role"]["roles_msg_id"]
                    await ctx.send(
                        f"ℹ️ - This guild doesn't have a select to role channel anymore!"
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                await ctx.send(
                    f"ℹ️ - The current server's select to role channel is: {self.bot.configs[ctx.guild.id]['select2role']['channel'].mention}"
                    if "select2role" in self.bot.configs[ctx.guild.id]
                    and "channel" in self.bot.configs[ctx.guild.id]["select2role"]
                    else f"ℹ️ - The server doesn't have a select to role channel yet!"
                )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occurred while setting the select to role channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_channels_group.command(
        pass_context=True,
        name="mods_channel",
        aliases=["mod_channel"],
        brief="🔱",
        description="This option manage the server's mods channel where all the error messages and other information are sent",
        usage="set|remove #channel",
    )
    async def config_channels_mods_channel_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
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
                        "mods_channel" in self.bot.configs[ctx.guild.id]
                        and self.bot.configs[ctx.guild.id]["mods_channel"]
                        == mods_channel
                    ):
                        return await ctx.reply(
                            f"ℹ️ - The server's mods channel is already {mods_channel.mention}!",
                            delete_after=20,
                        )

                    self.bot.config_repo.set_mods_channel(
                        ctx.guild.id,
                        mods_channel.id,
                    )
                    self.bot.configs[ctx.guild.id]["mods_channel"] = mods_channel
                    await ctx.send(
                        f"ℹ️ - The mods channel is now {mods_channel.mention} in this guild!"
                    )

                elif option == "remove":
                    if "mods_channel" not in self.bot.configs[ctx.guild.id]:
                        return await ctx.reply(
                            f"ℹ️ - The server already doesn't have a mods channel configured!",
                            delete_after=20,
                        )

                    self.bot.config_repo.set_mods_channel(ctx.guild.id, None)
                    del self.bot.configs[ctx.guild.id]["mods_channel"]
                    await ctx.send(
                        f"ℹ️ - This guild doesn't have a mods channel anymore!"
                    )
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                await ctx.send(
                    f"ℹ️ - The current server's mods channel is: {self.bot.configs[ctx.guild.id]['mods_channel'].mention}"
                    if "mods_channel" in self.bot.configs[ctx.guild.id]
                    else f"ℹ️ - The server doesn't have a mods channel yet!"
                )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occurred while setting the mods channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
