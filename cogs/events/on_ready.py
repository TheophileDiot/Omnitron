from collections import OrderedDict
from typing import Union
from discord.ext.commands import Cog
from lavalink import add_event_hook, Client
from lavalink.events import NodeConnectedEvent, QueueEndEvent, TrackEndEvent

from bot import Omnitron


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """Check on start if any guilds that the bot is in are not in the DB else initialise moderators list for every guild in the DB"""
        db_guilds = set([int(k) for k in self.bot.main_repo.get_guilds().keys()])
        guilds = set(self.bot.guilds)
        for guild in guilds:
            if guild.id not in db_guilds:
                self.bot.main_repo.create_guild(
                    guild.id, guild.name, f"{guild.owner}"
                )  # If guild is not in DB, create it

            db_users = set(self.bot.user_repo.get_users(guild.id).keys())
            members = set(
                [m for m in guild.members if not m.bot and str(m.id) not in db_users]
            )
            for member in members:
                self.bot.user_repo.create_user(guild.id, member.id, f"{member}")

            self.bot.moderators[guild.id] = list(
                [int(k) for k in self.bot.config_repo.get_moderators(guild.id).keys()]
            )  # Initialize moderators list for every guilds
            self.bot.configs[guild.id] = {
                "prefix": self.bot.config_repo.get_prefix(guild.id)
            }

            xp = self.bot.config_repo.get_xp(guild.id)
            self.bot.configs[guild.id]["xp"] = dict(xp)

            if "boosteds" in xp:
                self.bot.configs[guild.id]["xp"]["boosteds"] = {
                    key: int(value["bonus"]) for key, value in xp["boosteds"].items()
                }

            if "lvl2role" in xp:
                self.bot.configs[guild.id]["xp"]["lvl2role"] = {
                    int(key): guild.get_role(value["role_id"])
                    for key, value in xp["lvl2role"].items()
                }

            if "prestiges" in xp:
                self.bot.configs[guild.id]["xp"]["prestiges"] = {
                    int(key[2]): guild.get_role(value["role_id"])
                    for key, value in xp["prestiges"].items()
                }

            if "notify_channel" in xp:
                self.bot.configs[guild.id]["xp"]["notify_channel"] = guild.get_channel(
                    xp["notify_channel"]
                )

            mute_on_join = self.bot.config_repo.get_mute_on_join(guild.id)
            if mute_on_join:
                self.bot.configs[guild.id]["mute_on_join"] = {
                    "duration": mute_on_join["duration"],
                    "muted_role": guild.get_role(int(mute_on_join["muted_role_id"])),
                }
                if "notify_channel_id" in mute_on_join:
                    self.bot.configs[guild.id]["mute_on_join"][
                        "notify_channel"
                    ] = guild.get_channel(int(mute_on_join["notify_channel_id"]))

            prevent_invites = self.bot.config_repo.get_invit_prevention(guild.id)
            self.bot.configs[guild.id]["prevent_invites"] = (
                {
                    "notify_channel": guild.get_channel(
                        int(prevent_invites["notify_channel_id"])
                    )
                }
                if isinstance(prevent_invites, OrderedDict)
                else None
            )

            self.bot.playlists[guild.id] = []

            self.bot.djs[guild.id] = list(
                [int(k) for k in self.bot.config_repo.get_djs(guild.id).keys()]
            )  # Initialize moderators list for every guilds

            commands_channels = self.bot.config_repo.get_commands_channels(guild.id)
            if commands_channels:
                self.bot.configs[guild.id]["commands_channels"] = [
                    int(c) for c in commands_channels.keys()
                ]

            music_channels = self.bot.config_repo.get_music_channels(guild.id)
            if music_channels:
                self.bot.configs[guild.id]["music_channels"] = [
                    int(c) for c in music_channels.keys()
                ]

            xp_gain_channels = self.bot.config_repo.get_xp_gain_channels(guild.id)
            if xp_gain_channels:
                text_channels = []
                voice_channels = []

                for k, v in xp_gain_channels.items():
                    if v["type"] == "TextChannel":
                        text_channels.append(int(k))
                    else:
                        voice_channels.append(int(k))

                self.bot.configs[guild.id]["xp_gain_channels"] = {
                    "TextChannel": text_channels,
                    "VoiceChannel": voice_channels,
                }

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

        self.bot.starting = False

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
