from disnake import Guild
from disnake.ext.commands import Cog
from logging import info

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_guild_join"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_join(self, guild: Guild):
        """When the bot joins a guild, add it to the database or set his presence to True if the guild was already stored in the database"""
        db_guild = self.bot.main_repo.get_guild(guild.id)

        if not db_guild:
            self.bot.main_repo.create_guild(guild.id, guild.name, f"{guild.owner}")
        else:
            self.bot.main_repo.update_guild(
                guild.id,
                {"name": guild.name, "owner": f"{guild.owner}", "present": True},
            )

        await self.bot.utils_class.init_guild(guild)
        info(f"Joined the guild {guild.name} ({guild.id}), created by {guild.owner}")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
