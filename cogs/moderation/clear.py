from typing import Union

from disnake import ApplicationCommandInteraction, Member, Option, OptionType
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    has_permissions,
    max_concurrency,
    slash_command,
)

from bot import Omnitron


class Moderation(Cog, name="moderation.clear"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="clear",
        aliases=["delete"],
        usage="<number of messages> (@member)",
        description="Delete a given number of messages in the channel from everyone or a certain member! (default: 10)",
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(
        read_message_history=True, manage_messages=True, send_messages=True
    )
    @max_concurrency(1, per=BucketType.channel)
    async def clear_command(
        self, ctx: Context, nbr_msgs: int = 10, member: Member = None
    ):
        await self.handle_clear(ctx, nbr_msgs, member)

    @slash_command(
        name="clear",
        aliases=["delete"],
        description="Delete a given number of messages in the channel from everyone or a certain member! (default: 10)",
        options=[
            Option(
                name="number_messages",
                description="Enter the number of messages you want to clear",
                type=OptionType.integer,
                required=False,
            ),
            Option(
                name="member",
                description="Enter the member you want to clear the messages from",
                type=OptionType.user,
                required=False,
            ),
        ],
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(read_message_history=True, manage_messages=True)
    @max_concurrency(1, per=BucketType.channel)
    async def clear_command(
        self,
        inter: ApplicationCommandInteraction,
        number_messages: int = 10,
        member: Member = None,
    ):
        await self.handle_clear(inter, number_messages, member)

    """ METHOD(S) """

    async def handle_clear(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        nbr_msgs: int,
        member: Union[Member, None],
    ):
        if nbr_msgs <= 0:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - Please provide a number greater than 0! `${self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.name}` for more details.",
                    delete_after=10,
                )
            else:
                await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Please provide a number greater than 0!",
                    ephemeral=True,
                )

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
            await source.response.send_message(
                f"ℹ️ - `{len(deleted)}` message{'s' if len(deleted) > 1 else ''} deleted {f'from the user {member}' if member else ''}.",
                ephemeral=True,
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
