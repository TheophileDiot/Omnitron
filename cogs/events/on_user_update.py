from disnake import User
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_user_update"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_user_update(self, before: User, after: User):
        """When a user update his profile update him in every guild that he is in in the database"""
        await self.bot.wait_until_ready()

        if after.bot:
            return

        if f"{before}" != f"{after}":
            for guild in set(after.mutual_guilds):
                self.bot.user_repo.update_user(guild.id, after.id, f"{after}")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
