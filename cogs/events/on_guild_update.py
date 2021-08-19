from discord import Guild
from discord.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_update(self, before: Guild, after: Guild):
        """When a guild is updated, update the database"""
        updates = {}
        if before.name != after.name:
            updates["name"] = after.name
        if f"{before.owner}" != f"{after.owner}":
            updates["owner"] = f"{after.owner}"
        if updates:
            self.bot.main_repo.update_guild(after.id, updates)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
