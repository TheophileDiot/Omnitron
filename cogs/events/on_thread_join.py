from disnake import Forbidden, Thread
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_thread_join"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_thread_join(self, thread: Thread):
        await self.bot.wait_until_ready()

        try:
            await thread.join()
        except Forbidden:
            pass


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
