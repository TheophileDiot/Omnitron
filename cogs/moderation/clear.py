from typing import Union

from disnake import GuildCommandInteraction, Member
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    has_permissions,
    max_concurrency,
    Range,
    slash_command,
)

from bot import Omnitron


async def handle_clear(
    source: Union[Context, GuildCommandInteraction],
    nbr_msgs: int,
    member: Member = None,
):
    if not isinstance(source, Context):
        await source.response.defer(ephemeral=True)

    if member:
        deleted = await source.channel.purge(
            limit=nbr_msgs, check=(lambda m: m.author == member)
        )
    else:
        deleted = await source.channel.purge(limit=nbr_msgs)

    if isinstance(source, Context):
        await source.send(
            f"ℹ️ - `{len(deleted)}` message{'s' if len(deleted) > 1 else ''} deleted {f'from the user {member}' if member else ''}.",
            delete_after=20,
        )
    else:
        await source.edit_original_message(
            content=f"ℹ️ - `{len(deleted)}` message{'s' if len(deleted) > 1 else ''} deleted {f'from the user {member}' if member else ''}."
        )


class Moderation(Cog, name="moderation.clear"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="clear",
        aliases=["delete"],
        usage="<number of messages> (@member)",
        description="Deletes a given number of messages in the channel from everyone or a certain member! (default: 10)",
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(
        read_message_history=True, manage_messages=True, send_messages=True
    )
    @max_concurrency(1, per=BucketType.channel)
    async def clear_command(
        self, ctx: Context, number_messages: Range[int, 1, ...] = 10, member: Member = None
    ):
        """
        This command deletes a given number of messages in the channel from everyone or a certain member! (default: 10)

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        number_messages: :class:`disnake.ext.commands.Range` optional
            The number of messages to delete (10 by default)
        member: :class:`disnake.Member` optional
            Deletes messages only sent by this member
        """
        await handle_clear(ctx, int(number_messages), member)

    @slash_command(
        name="clear",
        description="Deletes a given number of messages in the channel from everyone or a certain member! (default: 10)",
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(read_message_history=True, manage_messages=True)
    @max_concurrency(1, per=BucketType.channel)
    async def clear_command(
        self,
        inter: GuildCommandInteraction,
        number_messages: Range[int, 1, ...] = 10,
        member: Member = None,
    ):
        """
        This slash command deletes a given number of messages in the channel from everyone or a certain member! (default: 10)

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        number_messages: :class:`disnake.ext.commands.Range` optional
            The number of messages to delete (10 by default)
        member: :class:`disnake.Member` optional
            Deletes messages only sent by this member
        """
        await handle_clear(inter, number_messages, member)


def setup(bot):
    bot.add_cog(Moderation(bot))
