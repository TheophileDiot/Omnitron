from discord import Member, Role, TextChannel
from discord.channel import VoiceChannel
from discord.ext.commands import Context, Cog, group
from discord.ext.commands.errors import (
    BadArgument,
    BadUnionArgument,
    MissingRequiredArgument,
)
from inspect import Parameter
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
    async def config_command(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's configuration"
                )
            )

    """ MAIN GROUP'S GROUP(S) """

    @config_command.group(
        pass_context=True,
        case_insensitive=True,
        name="security",
        brief="🚓",
        description="This option manage the server's security",
    )
    async def config_security_command(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's security configuration",
                )
            )

    @config_command.group(
        pass_context=True,
        case_insensitive=True,
        name="xp",
        brief="✨",
        usage="(sub-command)",
        description="This option manage the server's experience feature",
    )
    async def config_xp_command(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx,
                    title=f"{ctx.command.brief} Server's experience configuration",
                )
            )

    """ MAIN GROUP'S COMMAND(S) """

    @config_command.command(
        pass_context=True,
        name="moderators",
        aliases=["mods"],
        brief="🔨",
        description="This option manage the server's moderators (role & members)",
        usage="add|remove|purge @role|@member",
    )
    async def config_moderators_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        mod: Union[Role, Member] = None,
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not mod:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="moderator", kind=Parameter.KEYWORD_ONLY
                            )
                        )
                    elif isinstance(mod, Member) and mod.bot:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - You can't add a bot user to the moderators list!",
                            delete_after=20,
                        )

                    if option == "add":
                        if mod.id in set(self.bot.moderators[ctx.guild.id]):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{mod}` {'role' if isinstance(mod, Role) else 'member'} is already in the moderators list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_moderator(
                            ctx.guild.id, mod.id, f"{mod}", type(mod).__name__
                        )
                        self.bot.moderators[ctx.guild.id].append(mod.id)
                        await ctx.send(
                            f"ℹ️ - Added `@{mod}` {'role' if isinstance(mod, Role) else 'member'} to the moderators list."
                        )
                    elif option == "remove":
                        if mod.id not in set(self.bot.moderators[ctx.guild.id]):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{mod}` {'role' if isinstance(mod, Role) else 'member'} is already not in the moderators list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_moderator(ctx.guild.id, mod.id)
                        del self.bot.moderators[ctx.guild.id][
                            self.bot.moderators[ctx.guild.id].index(mod.id)
                        ]
                        await ctx.send(
                            f"ℹ️ - Removed `@{(await ctx.guild.fetch_member(int(mod.id))) if isinstance(mod, Member) else ctx.guild.get_role(int(mod.id))}` {'role' if isinstance(mod, Role) else 'member'} from the moderators list."
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else 'removing'} `@{mod}` {'role' if isinstance(mod, Role) else 'member'} to the moderators list! please try again in a few seconds! Error type: {type(e)}",
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

    @config_command.command(
        pass_context=True,
        name="djs",
        aliases=["players"],
        brief="🧑‍🎤",
        description="This option manage the server's djs (role & members) (if there is no dj then everyone can use music commands)",
        usage="add|remove|purge @role|@member",
    )
    async def config_djs_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        dj: Union[Role, Member] = None,
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not dj:
                        raise MissingRequiredArgument(
                            param=Parameter(name="dj", kind=Parameter.KEYWORD_ONLY)
                        )
                    elif isinstance(dj, Member) and dj.bot:
                        return await ctx.reply(
                            f"ℹ️ - {ctx.author.mention} - You can't add a bot user to the djs list!",
                            delete_after=20,
                        )

                    if option == "add":
                        if dj.id in set(self.bot.djs[ctx.guild.id]):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{dj}` {'role' if isinstance(dj, Role) else 'member'} is already in the djs list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_dj(
                            ctx.guild.id, dj.id, f"{dj}", type(dj).__name__
                        )
                        self.bot.djs[ctx.guild.id].append(dj.id)
                        await ctx.send(
                            f"ℹ️ - Added `@{dj}` {'role' if isinstance(dj, Role) else 'member'} to the djs list!."
                        )
                    elif option == "remove":
                        if dj.id not in set(self.bot.djs[ctx.guild.id]):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - `@{dj}` {'role' if isinstance(dj, Role) else 'member'} is already not in the djs list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_dj(ctx.guild.id, dj.id)
                        del self.bot.djs[ctx.guild.id][
                            self.bot.djs[ctx.guild.id].index(dj.id)
                        ]
                        await ctx.send(
                            f"ℹ️ - Removed `@{(await ctx.guild.fetch_member(int(dj.id))) if isinstance(dj, Member) else ctx.guild.get_role(int(dj.id))}` {'role' if isinstance(dj, Role) else 'member'} from the djs list!."
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else 'removing'} `@{dj}` {'role' if isinstance(dj, Role) else 'member'} to the djs list! please try again in a few seconds! Error type: {type(e)}",
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

    @config_command.command(
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
                    await ctx.send(f"ℹ️ - Bot prefix reseted to `o!`.")
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            except MissingRequiredArgument as mre:
                raise MissingRequiredArgument(param=mre.param)
            except Exception as e:
                await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error occured while {'resetting the prefix' if option == 'reset' else f'setting the prefix to `{prefix}`'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            msg = await ctx.send(
                f"ℹ️ - {ctx.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}`!"
            )
            await msg.add_reaction("👀")

    @config_command.command(
        pass_context=True,
        name="commands_channels",
        aliases=["command_channels", "command_channel", "cmds_chans"],
        brief="🕹️",
        description="This option manage the server's commands channels  (if there is no commands channel then commands can be used everywhere)",
        usage="add|remove|purge #channel",
    )
    async def config_prefix_command(
        self, ctx: Context, option: Utils.to_lower = None, channel: TextChannel = None
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not channel:
                        raise MissingRequiredArgument(
                            param=Parameter(name="channel", kind=Parameter.KEYWORD_ONLY)
                        )

                    if option == "add":
                        if "commands_channels" in self.bot.configs[
                            ctx.guild.id
                        ] and channel.id in set(
                            self.bot.configs[ctx.guild.id]["commands_channels"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - {channel.mention} is already in the commands channels list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_commands_channel(
                            ctx.guild.id, channel.id, f"{channel}"
                        )

                        if "commands_channels" not in self.bot.configs[ctx.guild.id]:
                            self.bot.configs[ctx.guild.id]["commands_channels"] = []

                        self.bot.configs[ctx.guild.id]["commands_channels"].append(
                            channel.id
                        )
                        await ctx.send(
                            f"ℹ️ - Added {channel.mention} to the commands channels list!."
                        )
                    elif option == "remove":
                        if "commands_channels" in self.bot.configs[
                            ctx.guild.id
                        ] and channel.id not in set(
                            self.bot.configs[ctx.guild.id]["commands_channels"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - {channel.mention} is already not in the commands channels list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_commands_channel(
                            ctx.guild.id, channel.id
                        )
                        del self.bot.configs[ctx.guild.id]["commands_channels"][
                            self.bot.configs[ctx.guild.id]["commands_channels"].index(
                                channel.id
                            )
                        ]
                        await ctx.send(
                            f"ℹ️ - Removed {channel.mention} from the commands channels list!."
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else 'removing'} {channel.mention} to the commands channels list! please try again in a few seconds! Error type: {type(e)}",
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

    @config_command.command(
        pass_context=True,
        name="music_channels",
        aliases=["music_channel" "music_chans"],
        brief="🎶",
        description="This option manage the server's music channels  (if there is no music channel then music can be listened everywhere)",
        usage="add|remove|purge (#voice_channel|<voice_channel_name>)",
    )
    async def config_prefix_command(
        self, ctx: Context, option: Utils.to_lower = None, channel: VoiceChannel = None
    ):
        if option:
            try:
                if option in ("add", "remove"):
                    if not channel:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="voice_channel", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    if option == "add":
                        if "music_channels" in self.bot.configs[
                            ctx.guild.id
                        ] and channel.id in set(
                            self.bot.configs[ctx.guild.id]["music_channels"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - {channel.mention} is already in the music channels list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.add_music_channel(
                            ctx.guild.id, channel.id, f"{channel}"
                        )

                        if "music_channels" not in self.bot.configs[ctx.guild.id]:
                            self.bot.configs[ctx.guild.id]["music_channels"] = []

                        self.bot.configs[ctx.guild.id]["music_channels"].append(
                            channel.id
                        )
                        await ctx.send(
                            f"ℹ️ - Added {channel.mention} to the music channels list!."
                        )
                    elif option == "remove":
                        if "music_channels" in self.bot.configs[
                            ctx.guild.id
                        ] and channel.id not in set(
                            self.bot.configs[ctx.guild.id]["music_channels"]
                        ):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - {channel.mention} is already not in the music channels list!",
                                delete_after=20,
                            )

                        self.bot.config_repo.remove_music_channel(
                            ctx.guild.id, channel.id
                        )
                        del self.bot.configs[ctx.guild.id]["music_channels"][
                            self.bot.configs[ctx.guild.id]["music_channels"].index(
                                channel.id
                            )
                        ]
                        await ctx.send(
                            f"ℹ️ - Removed {channel.mention} from the music channels list!."
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else 'removing'} {channel.mention} to the music channels list! please try again in a few seconds! Error type: {type(e)}",
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

    """ MAIN GROUP'S SECURITY COMMAND(S) """

    @config_security_command.command(
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "prevent_invites" in self.bot.configs[ctx.guild.id]
                ) == val and option != "update":
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The invites prevention is already set to `{BOOL2VAL[val]}`!"
                        + f" Parameters: 'notify_channel': {self.bot.configs[ctx.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['prevent_invites'] else '`No channel specified.`'}"
                    )

                if val:
                    self.bot.config_repo.set_invit_prevention(
                        ctx.guild.id, val, notify_channel.id if notify_channel else None
                    )
                    self.bot.configs[ctx.guild.id]["prevent_invites"] = (
                        {"notify_channel": notify_channel} if notify_channel else {}
                    )
                else:
                    self.bot.config_repo.remove_invit_prevention(ctx.guild.id)
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {f'setting the invites prevention `{BOOL2VAL[val]}`' if option != 'update' else 'updating the invites prevention'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The invites prevention is currently `{BOOL2VAL['prevent_invites' in self.bot.configs[ctx.guild.id]]}` in this guild!"
                + f" Parameters: 'notify_channel': {self.bot.configs[ctx.guild.id]['prevent_invites']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['prevent_invites'] else '`No channel specified.`'}"
            )

    @config_security_command.command(
        pass_context=True,
        name="mute_on_join",
        aliases=["m_on_j"],
        brief="🔇",
        description="This option manage if users are muted during a certain amount of time when joining the server and then notify it at the end if a channel is specified! (default duration = 10 min) (duration format -> <duration value (more than 0)> <duration type (d, h, m, s)>",
        usage="(on|update|off) (<duration_value> <duration_type> @muted_role #channel)",
    )
    async def config_security_mute_on_join_command(
        self,
        ctx: Context,
        option: Utils.to_lower = None,
        _duration: int = None,
        duration_type: str = None,
        muted_role: Role = None,
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )

                if (
                    "mute_on_join" in self.bot.configs[ctx.guild.id]
                ) == val and option != "update":
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - The mute on join is already `{BOOL2VAL[val]}`!"
                        + (
                            f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[ctx.guild.id]['mute_on_join']['duration'])}`, 'muted_role': `@{self.bot.configs[ctx.guild.id]['mute_on_join']['muted_role'].name}`, 'notify_channel': {self.bot.configs[ctx.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['mute_on_join'] else '`No channel specified.`'}"
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
                    elif not muted_role:
                        raise MissingRequiredArgument(
                            param=Parameter(
                                name="muted_role", kind=Parameter.KEYWORD_ONLY
                            )
                        )

                    old_duration = f"{_duration} {duration_type}"
                    _duration = await self.bot.utils_class.parse_duration(
                        self.bot, _duration, duration_type, ctx
                    )
                    if not _duration:
                        return

                    self.bot.config_repo.set_mute_on_join(
                        ctx.guild.id,
                        _duration,
                        muted_role.id,
                        notify_channel.id if notify_channel else None,
                    )
                    self.bot.configs[ctx.guild.id]["mute_on_join"] = {
                        "duration": _duration,
                        "muted_role": muted_role,
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
                        f" Parameters: 'duration': `{old_duration}`, 'muted_role': `@{muted_role.name}`, 'notify_channel': {f'{notify_channel.mention}' if notify_channel else '`No channel specified.`'}"
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {f'setting the mute on join `{BOOL2VAL[val]}`' if option != 'update' else 'updating the mute on join'}! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The mute on join is currently `{BOOL2VAL['mute_on_join' in self.bot.configs[ctx.guild.id]]}` in this guild!"
                + (
                    f" Parameters: 'duration': `{self.bot.utils_class.duration(self.bot.configs[ctx.guild.id]['mute_on_join']['duration'])}`, 'muted_role': `@{self.bot.configs[ctx.guild.id]['mute_on_join']['muted_role'].name}`, 'notify_channel': {self.bot.configs[ctx.guild.id]['mute_on_join']['notify_channel'].mention if 'notify_channel' in self.bot.configs[ctx.guild.id]['mute_on_join'] else '`No channel specified.`'}"
                    if "mute_on_join" in self.bot.configs[ctx.guild.id]
                    else ""
                )
            )

    """ MAIN GROUP'S XP COMMAND(S) """

    @config_xp_command.command(
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while setting the xp `{BOOL2VAL[val]}`! please try again in a few seconds! Error type: {type(e)}",
                    delete_after=20,
                )
        else:
            await ctx.send(
                f"ℹ️ - {ctx.author.mention} - The xp is currently `{BOOL2VAL[self.bot.configs[ctx.guild.id]['xp']['is_on']]}` in this guild!"
            )

    @config_xp_command.command(
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
                        await ctx.send(
                            f"ℹ️ - Removed `@{(await ctx.guild.fetch_member(int(boosted.id))) if isinstance(boosted, Member) else ctx.guild.get_role(int(boosted.id))}` {'role' if isinstance(boosted, Role) else 'member'} from the boosted xp list."
                        )

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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} `@{boosted}` {'role' if isinstance(boosted, Role) else 'member'} {'to' if option != 'update' else 'from'} the boosters list! please try again in a few seconds! Error type: {type(e)}",
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

    @config_xp_command.command(
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
            else:
                await ctx.send(
                    f"ℹ️ - The current server's max level is: `{self.bot.configs[ctx.guild.id]['xp']['max_lvl']}`"
                )
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occured while setting the server's max level! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_xp_command.command(
        pass_context=True,
        name="notify_channel",
        aliases=["xp_chan"],
        brief="🌠",
        description="This option manage the server's xp channel",
        usage="set|remove #channel",
    )
    async def config_xp_max_lvl_command(
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
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
                        delete_after=20,
                    )
            else:
                await ctx.send(
                    f"ℹ️ - The current server's xp channel is: `{self.bot.configs[ctx.guild.id]['xp']['notify_channel']}`"
                    if "notify_channel" in self.bot.configs[ctx.guild.id]["xp"]
                    else f"ℹ️ - The server doesn't have an xp channel yet!"
                )
        except MissingRequiredArgument as mre:
            raise MissingRequiredArgument(param=mre.param)
        except Exception as e:
            await ctx.reply(
                f"⚠️ - {ctx.author.mention} - An error occured while setting the xp channel! please try again in a few seconds! Error type: {type(e)}",
                delete_after=20,
            )

    @config_xp_command.command(
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
                        for member in members:
                            if member.bot:
                                continue
                            await self.xp_class.manage_levels(
                                member, db_users[str(member.id)]["level"], "new_r_2_l"
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

                        members = set(ctx.guild.members)
                        for member in members:
                            if member.bot:
                                continue
                            await member.remove_roles(role)
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

                    members = set(ctx.guild.members)
                    for member in members:
                        if member.bot:
                            continue
                        await member.remove_roles(*roles)
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
                    f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the level `{lvl}` {'to' if option != 'update' else 'from'} the level to role list! please try again in a few seconds! Error type: {type(e)}",
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

    @config_xp_command.command(
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

                    members = set(ctx.guild.members)
                    for member in members:
                        if member.bot or old_role not in member.roles:
                            continue
                        await member.remove_roles(*old_role)
                        await member.add_roles(*role)
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

                    members = set(ctx.guild.members)
                    for member in members:
                        if member.bot or old_role not in member.roles:
                            continue
                        await member.remove_roles(old_role)
                        await self.xp_class.manage_prestige(member, "removed_prestige")
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

                    members = set(ctx.guild.members)
                    for member in members:
                        if member.bot or not set(member.roles) & set(old_roles):
                            continue
                        await member.remove_roles(*old_roles)
                        await self.xp_class.manage_prestige(member, "purged_prestiges")
                else:
                    await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - This option isn't available for the command `{ctx.command.qualified_name}`! option: `{option}`! Use the command `{self.bot.utils_class.get_guild_pre(self.bot, ctx.message)[0]}{ctx.command.parents[0]}` to get more help!",
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
            # except Exception as e:
            #     await ctx.reply(
            #         f"⚠️ - {ctx.author.mention} - An error occured while {'adding' if option == 'add' else ('removing' if option == 'remove' else 'updating')} the role `@{role}` to the prestige `{prestige}` {'to' if option != 'update' else 'from'} the prestiges list! please try again in a few seconds! Error type: {type(e)}",
            #         delete_after=20,
            #     )
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


def setup(bot):
    bot.add_cog(Moderation(bot))
