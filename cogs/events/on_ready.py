from typing import Union
from discord import Activity, ActivityType, activity
from discord.ext.commands import Cog
from lavalink import add_event_hook, Client
from lavalink.events import NodeConnectedEvent, QueueEndEvent, TrackEndEvent
from logging import info

from bot import Omnitron
from data import Utils


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """Check on start if any guilds that the bot is in are not in the DB else initialise moderators list for every guild in the DB"""
        db_guilds = set([int(k) for k in self.bot.main_repo.get_guilds().keys()])
        guilds = set(self.bot.guilds)

        for guild in guilds:

            """GUILDS CHECK"""

            if guild.id not in db_guilds:
                self.bot.main_repo.create_guild(
                    guild.id, guild.name, f"{guild.owner}"
                )  # If guild is not in DB, create it

            db_guild = self.bot.main_repo.get_guild(guild.id)

            if not db_guild["present"]:
                continue

            Utils.init_guild(self.bot, guild)

        print("Omnitron is ready.")
        info("Omnitron successfully started")

        # This ensures the client isn't overwritten during cog reloads.
        if not hasattr(self.bot, "lavalink"):
            self.bot.lavalink = Client(self.bot.user.id)
            # Host, Port, Password, Region, Name
            self.bot.lavalink.add_node(
                "127.0.0.1", 2333, "youshallnotpass", "eu", "default-node"
            )
            self.bot.add_listener(
                self.bot.lavalink.voice_update_handler, "on_socket_response"
            )

        add_event_hook(self.track_hook)

        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name=f"Ping me for prefix")
        )

        self.bot.starting = False

    def cog_unload(self):
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    """ METHOD(S) """

    async def track_hook(self, event: Union[TrackEndEvent, QueueEndEvent]):
        if isinstance(event, QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            guild = await self.bot.fetch_guild(guild_id)
            await self.bot.utils_class.clear_playlist(guild)
            await guild.change_voice_state(channel=None)
        elif isinstance(event, TrackEndEvent):
            guild_id = int(event.player.guild_id)
            del self.bot.playlists[guild_id][0]
        elif isinstance(event, NodeConnectedEvent):
            print("Lavalink node connected!")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
