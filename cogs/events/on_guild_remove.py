from disnake import Guild
from disnake.ext.commands import Cog
from logging import info

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_guild_remove"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_remove(self, guild: Guild):
        """When the bot get kicked from a guild, set his presence to False it from the database"""
        self.bot.main_repo.kicked_from_guild(guild.id)
        del self.bot.configs[guild.id]
        info(
            f"Kicked from the guild {guild.name} ({guild.id}), created by {guild.owner}"
        )


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
