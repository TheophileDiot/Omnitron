from disnake import ApplicationCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    slash_command,
)
from time import monotonic
from typing import Union

from bot import Omnitron


async def handle_ping(source: Union[Context, ApplicationCommandInteraction]):
    before = monotonic()

    if isinstance(source, Context):
        message_ping = await source.send("ℹ️ - Pong!")
        await message_ping.edit(
            content=f"ℹ️ - Pong!  `{int((monotonic() - before) * 1000)}ms`"
        )
    else:
        await source.response.send_message("ℹ️ - Pong!")
        await source.edit_original_message(
            content=f"ℹ️ - Pong!  `{int((monotonic() - before) * 1000)}ms`"
        )


class Miscellaneous(Cog, name="misc.ping"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ COMMANDS """

    @command(name="ping", aliases=["latency"], description="Checks the bot latency!")
    @bot_has_permissions(send_messages=True)
    async def ping_command(self, ctx: Context):
        """
        This command checks bot latency!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        await handle_ping(ctx)

    @slash_command(name="ping", description="Checks the bot latency!")
    async def ping_slash_command(self, inter: ApplicationCommandInteraction):
        """
        This slash command checks bot latency!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await handle_ping(inter)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
