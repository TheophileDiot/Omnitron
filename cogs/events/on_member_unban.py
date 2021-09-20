from disnake import Guild, User
from disnake.ext.commands import Cog
from time import time

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_member_unban"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_member_unban(self, guild: Guild, user: User):
        await self.bot.wait_until_ready()

        if user.bot:
            return

        self.bot.user_repo.unban_user(
            guild.id, user.id, time(), f"{self.bot.user}", "Unbanned manually"
        )

        if user.id in self.bot.tasks[guild.id]["ban_completions"]:
            self.bot.tasks[guild.id]["ban_completions"][user.id].cancel()
            del self.bot.tasks[guild.id]["ban_completions"][user.id]


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
