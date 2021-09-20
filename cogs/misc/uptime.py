from datetime import datetime
from disnake.ext.commands import bot_has_permissions, Cog, command, Context

from bot import Omnitron


class Miscellaneous(Cog, name="misc.uptime"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.start_time = datetime.now()

    @command(
        name="uptime",
        aliases=["up", "time"],
        description="Shows how long the bot has been connected!",
    )
    @bot_has_permissions(send_messages=True)
    async def uptime_command(self, ctx: Context):
        await ctx.send(
            f"ℹ️ - I have been connected since: `{self.bot.utils_class.duration((datetime.now() - self.start_time).total_seconds())}`"
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
