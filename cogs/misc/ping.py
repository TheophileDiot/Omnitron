from discord.ext.commands import bot_has_permissions, Cog, command, Context
from time import monotonic

from bot import Omnitron


class Miscellaneous(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(name="ping", aliases=["latency"], description="Check bot latency!")
    @bot_has_permissions(send_messages=True)
    async def ping_command(self, ctx: Context):
        before = monotonic()
        message_ping = await ctx.send("ℹ️ - Pong!")
        await message_ping.edit(
            content=f"ℹ️ - Pong!  `{int((monotonic() - before) * 1000)}ms`"
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
