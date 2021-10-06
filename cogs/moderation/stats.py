from itertools import chain
from typing import Union

from disnake import (
    ApplicationCommandInteraction,
    Member,
    TextChannel,
    VoiceChannel,
)
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    Context,
    group,
    guild_only,
    slash_command,
    user_command,
)

from bot import Omnitron
from data import Utils


class Moderation(Cog, name="moderation.stats"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ GROUP """

    @group(
        pass_context=True,
        case_insensitive=True,
        name="stats",
        aliases=["stat"],
        usage="(sub-command)",
        description="This command manage the server's stats",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def stats_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's stats feature"
                )
            )

    @slash_command(
        name="stats",
        description="This command manage the server's stats",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def stats_slash_group(self, inter: ApplicationCommandInteraction):
        pass

    """ MAIN GROUP'S COMMAND(S) """

    """ MESSAGES COUNT """

    @stats_group.command(
        pass_context=True,
        name="messages_count",
        aliases=["messages_counts", "messages"],
        brief="💬",
        description="This option count every messages (or a member's) sent in this server or in a specific channel",
        usage="(@member) (#text_channel)",
    )
    async def stats_message_count_command(
        self,
        ctx: Context,
        member: Union[Member, TextChannel] = None,
        text_channel: TextChannel = None,
    ):
        if isinstance(member, TextChannel):
            text_channel = member
            member = None

        await self.handle_messages_count(ctx, member, text_channel)

    @stats_slash_group.sub_command(
        name="messages_count",
        description="Count the number of messages a member (our yourself) has sent in the server or in a specific channel",
    )
    async def stats_message_count_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
        text_channel: TextChannel = None,
    ):
        await self.handle_messages_count(inter, member, text_channel)

    @user_command(
        name="count messages",
        description="Count the number of messages a member (our yourself) has sent in the server or in a specific channel",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def stats_message_count_user_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        await self.handle_messages_count(inter, inter.target)

    async def handle_messages_count(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
        text_channel: TextChannel = None,
    ):
        if member:
            db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

            if text_channel:
                count = (
                    db_user["messages_count"][str(text_channel.id)]
                    if "messages_count" in db_user
                    and str(text_channel.id) in db_user["messages_count"]
                    else 0
                )
            else:
                count = (
                    sum(list(db_user["messages_count"].values()))
                    if "messages_count" in db_user
                    else 0
                )

            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} {f'have sent a total of `{count}`' if count else 'have never sent any'} message{'s' if count > 1 else ''} {f'in the channel {text_channel.mention}' if text_channel else 'in the server'}!"
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} {f'have sent a total of `{count}`' if count else 'have never sent any'} message{'s' if count > 1 else ''} {f'in the channel {text_channel.mention}' if text_channel else 'in the server'}!"
                )
        else:
            db_users = self.bot.user_repo.get_users(source.guild.id)

            if isinstance(source, ApplicationCommandInteraction):
                await source.response.defer()

            if text_channel:
                count = sum(
                    [
                        u["messages_count"][str(text_channel.id)]
                        if str(text_channel.id) in u["messages_count"]
                        else 0
                        for u in db_users.values()
                        if "messages_count" in u
                    ]
                )
            else:
                count = sum(
                    list(
                        chain.from_iterable(
                            [
                                [c for c in u["messages_count"].values()]
                                for u in db_users.values()
                                if "messages_count" in u
                            ]
                        )
                    )
                )

            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {f'The channel {text_channel.mention}' if text_channel else 'This guild'} contains `{count}` messages in total!"
                )
            else:
                await source.edit_original_message(
                    content=f"ℹ️ - {f'The channel {text_channel.mention}' if text_channel else 'This guild'} contains `{count}` messages in total!"
                )

    """ VOICE TIME COUNT """

    @stats_group.command(
        pass_context=True,
        name="voice_time_count",
        aliases=["voice_time_counts", "voice_time"],
        brief="🎙️",
        description="This option count every seconds everyone (or a specific member) has passed inside every voice channels or a specific one",
        usage="(@member) (#voice_channel)",
    )
    async def stats_voice_time_count_command(
        self,
        ctx: Context,
        member: Union[Member, VoiceChannel] = None,
        text_channel: VoiceChannel = None,
    ):
        if isinstance(member, VoiceChannel):
            text_channel = member
            member = None

        await self.handle_voice_time_count(ctx, member, text_channel)

    @stats_slash_group.sub_command(
        name="voice_time_count",
        description="Count every seconds everyone (or a member) has passed inside every voice channels or a specific one",
    )
    async def stats_voice_time_count_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
        voice_channel: VoiceChannel = None,
    ):
        await self.handle_voice_time_count(inter, member, voice_channel)

    @user_command(
        name="count voice time",
        description="Count every seconds everyone (or a member) has passed inside every voice channels or a specific one",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def stats_voice_time_count_user_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        await self.handle_voice_time_count(inter, inter.target)

    async def handle_voice_time_count(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
        voice_channel: VoiceChannel = None,
    ):
        if member:
            db_user = self.bot.user_repo.get_user(source.guild.id, member.id)

            if voice_channel:
                count = (
                    db_user["voice_count"][str(voice_channel.id)]
                    if "voice_count" in db_user
                    and str(voice_channel.id) in db_user["voice_count"]
                    else 0
                )
            else:
                count = (
                    sum(list(db_user["voice_count"].values()))
                    if "voice_count" in db_user
                    else 0
                )

            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} {f'have been connected a total of `{self.bot.utils_class.duration(count)}`' if count else 'have never been connected' + (' to any voice channels' if not voice_channel else '')} {f'in the channel {voice_channel.mention}' if voice_channel else 'in the server'}!"
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} {f'have been connected a total of `{self.bot.utils_class.duration(count)}`' if count else 'have never been connected' + (' to any voice channels' if not voice_channel else '')} {f'in the channel {voice_channel.mention}' if voice_channel else 'in the server'}!"
                )
        else:
            db_users = self.bot.user_repo.get_users(source.guild.id)

            if isinstance(source, ApplicationCommandInteraction):
                await source.response.defer()

            if voice_channel:
                count = sum(
                    [
                        u["voice_count"][str(voice_channel.id)]
                        if str(voice_channel.id) in u["voice_count"]
                        else 0
                        for u in db_users.values()
                        if "voice_count" in u
                    ]
                )
            else:
                count = sum(
                    list(
                        chain.from_iterable(
                            [
                                [c for c in u["voice_count"].values()]
                                for u in db_users.values()
                                if "voice_count" in u
                            ]
                        )
                    )
                )

            if isinstance(source, Context):
                await source.send(
                    f"ℹ️ - People in this server have been connected in {f'the channel {voice_channel.mention}' if voice_channel else 'this guild'} for a total duration of `{self.bot.utils_class.duration(count)}` in total!"
                )
            else:
                await source.edit_original_message(
                    content=f"ℹ️ - People in this server have been connected in {f'the channel {voice_channel.mention}' if voice_channel else 'this guild'} for a total duration of `{self.bot.utils_class.duration(count)}` in total!"
                )

    """ COMMAND_COUNT """

    @stats_group.command(
        pass_context=True,
        name="commands_count",
        aliases=["commands_counts", "commands"],
        brief="⌨️",
        description="This option count the number of commands a member (our yourself) has executed in the server (add details at the end to get the full list)",
        usage="(@member) (details)",
    )
    async def stats_commands_count_command(
        self, ctx: Context, member: Union[Member, str] = None, details: str = None
    ):
        res = False

        if details == "details":
            res = True
        elif isinstance(member, str) and member == "details":
            res = True
            member = None
        elif isinstance(member, str):
            member = None

        await self.handle_commands_count(ctx, member, res)

    @stats_slash_group.sub_command(
        name="commands_count",
        description="Count the number of commands a member (our yourself) has executed in the server",
    )
    async def stats_commands_count_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        member: Member = None,
        details: bool = False,
    ):
        await self.handle_commands_count(inter, member, details)

    @user_command(
        name="count commands",
        description="Count the number of commands a member (our yourself) has executed in the server",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def stats_commands_count_user_command(
        self,
        inter: ApplicationCommandInteraction,
    ):
        await self.handle_commands_count(inter, inter.target)

    async def handle_commands_count(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
        details: bool = False,
    ):
        if not member:
            member = source.author

        count = self.bot.user_repo.get_commands_count(
            source.guild.id, member.id, details
        )

        if details:
            if not count:
                if isinstance(source, Context):
                    return await source.send(
                        f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} have never executed any command in the server!"
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} have never executed any command in the server!"
                    )

            endl = "\n"

            nbr = 0
            for command in count.values():
                nbr += command

            resp = f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} have executed a total of `{nbr}` command{'s' if nbr > 1 else ''} in the server!\n\n{endl.join([f'`{c}`: {count[c]}' for c in count])}"
        else:
            if not count:
                count = 0

            resp = f"ℹ️ - {f'The member `{member}`' if member != source.author else 'You'} {f'have executed a total of `{count}`' if count else 'have never executed any'} command{'s' if count > 1 else ''} in the server!"

        if isinstance(source, Context):
            await source.send(resp)
        else:
            await source.response.send_message(resp)

    """ MEMBERS COUNT """

    @stats_group.command(
        pass_context=True,
        name="members_count",
        aliases=["members_counts", "members"],
        brief="🤔",
        description="This option count the members (including bots or not, default is False) in the server!",
        usage="(bots)",
    )
    async def stats_members_count_command(self, ctx: Context, bots: str = None):
        resp = False
        if bots == "bots":
            resp = True

        await self.handle_members_count(ctx, resp)

    @stats_slash_group.sub_command(
        name="members_count",
        description="This option count the members (including bots or not, default is False) in the server!",
    )
    async def stats_members_count_slash_command(
        self, inter: ApplicationCommandInteraction, bots: bool = False
    ):
        await self.handle_members_count(inter, bots)

    async def handle_members_count(
        self, source: Union[Context, ApplicationCommandInteraction], bots: bool = False
    ):
        count = (
            source.guild.member_count
            if bots
            else len([m for m in source.guild.members if not m.bot])
        )

        if isinstance(source, Context):
            await source.send(
                f"ℹ️ - There are `{count}` members in this guild!{' Including bots' if bots else None}"
            )
        else:
            await source.response.send_message(
                f"ℹ️ - There are `{count}` members in this guild!{' Including bots' if bots else None}"
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
