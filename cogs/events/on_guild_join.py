from discord import Guild
from discord.ext.commands import Cog
from logging import info

from bot import Omnitron
from data import Utils


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_join(self, guild: Guild):
        """When the bot joins a guild, add it to the database or set his presence to True if the guild was already stored in the database"""
        self.bot.main_repo.create_guild(guild.id, guild.name, f"{guild.owner}")
        info(f"Joined the guild {guild.name} ({guild.id}), created by {guild.owner}")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
