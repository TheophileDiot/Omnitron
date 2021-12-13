from datetime import datetime
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    slash_command,
)

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
        """
        This command shows how long the bot has been connected!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        await ctx.send(
            f"ℹ️ - I have been connected since: `{self.bot.utils_class.duration((datetime.now() - self.start_time).total_seconds())}`"
        )

    @slash_command(
        name="uptime",
        description="Shows how long the bot has been connected!",
    )
    async def uptime_slash_command(self, inter: ApplicationCommandInteraction):
        """
        This slash command shows how long the bot has been connected!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await inter.response.send_message(
            f"ℹ️ - I have been connected since: `{self.bot.utils_class.duration((datetime.now() - self.start_time).total_seconds())}`"
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
