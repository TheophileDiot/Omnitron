from datetime import datetime, timedelta
from discord import Member
from discord.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    has_permissions,
    max_concurrency,
)

from bot import Omnitron


class Moderation(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="clear",
        aliases=["delete"],
        usage="<number of messages> (@member)",
        description="Delete a given number of messages in the channel from everyone or a certain member! (99 max) (default: 10)",
    )
    @has_permissions(manage_messages=True)
    @bot_has_permissions(
        read_message_history=True, manage_messages=True, send_messages=True
    )
    @max_concurrency(1, per=BucketType.channel)
    async def clear_command(
        self, ctx: Context, nbr_msgs: int = 10, member: Member = None
    ):
        if nbr_msgs <= 0:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - Please provide a number greater than 0! `${self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.name}` for more details.",
                delete_after=10,
            )

        deleted = await ctx.channel.purge(
            limit=nbr_msgs, check=(lambda m: m.author == member) if member else None
        )
        await ctx.send(
            f"ℹ️ - `{len(deleted)}` message{'s' if len(deleted) > 1 else ''} deleted {f'from the user {member}' if member else ''}.",
            delete_after=20,
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
