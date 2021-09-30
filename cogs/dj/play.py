from inspect import Parameter
from re import compile as re_compile
from typing import Union

from disnake import (
    Client as botClient,
    Embed,
    GuildCommandInteraction,
    NotFound,
    VoiceClient,
)
from disnake.abc import Connectable
from disnake.ext.commands import (
    BotMissingPermissions,
    bot_has_permissions,
    bot_has_guild_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
    slash_command,
)
from disnake.ext.commands.errors import MissingRequiredArgument
from lavalink import add_event_hook, Client
from lavalink.events import NodeConnectedEvent, QueueEndEvent, TrackEndEvent
from lavalink.exceptions import NodeException
from lavalink.models import AudioTrack

from bot import Omnitron
from data import Utils


class LavalinkVoiceClient(VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: botClient, channel: Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, "lavalink"):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = Client(client.user.id)
            self.client.lavalink.add_node(
                "localhost", 2333, "youshallnotpass", "us", "default-node"
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # notify lavalink we disconnected
        self.lavalink.player_manager.remove(self.channel.guild.id)
        self.cleanup()


class Dj(Cog, name="dj.play"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")
        self.yt_rx = re_compile(
            r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"
        )

    """ EVENTS """

    @Cog.listener()
    async def on_ready(self):
        # This ensures the client isn't overwritten during cog reloads.
        if not hasattr(self.bot, "lavalink"):
            self.bot.lavalink = Client(self.bot.user.id)
            # Host, Port, Password, Region, Name
            self.bot.lavalink.add_node(
                "127.0.0.1", 2333, "youshallnotpass", "eu", "default-node"
            )
            # self.bot.add_listener(
            #     self.bot.lavalink.voice_update_handler, "on_socket_response"
            # )

        add_event_hook(self.track_hook)

    """ METHODS """

    async def track_hook(
        self, event: Union[TrackEndEvent, QueueEndEvent, NodeConnectedEvent]
    ):
        if isinstance(event, QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)

            try:
                guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(
                    guild_id
                )
            except NotFound:
                return

            await guild.voice_client.disconnect(force=True)
            self.bot.playlists[guild_id].clear()
        elif isinstance(event, TrackEndEvent):
            guild_id = int(event.player.guild_id)

            try:
                del self.bot.playlists[guild_id][0]
            except IndexError:
                pass
        elif isinstance(event, NodeConnectedEvent):
            print("Lavalink node connected!")

    """ CHECKS """

    def __ensure_voice(function):
        async def check(
            self,
            source: Union[Context, GuildCommandInteraction],
            *,
            query: str = None,
            **kwargs,
        ):
            """This check ensures that the bot and command author are in the same voicechannel."""
            try:
                player = self.bot.lavalink.player_manager.create(
                    source.guild.id, endpoint=str(source.guild.region)
                )
            except NodeException:
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - The player is not ready yet, please try again in a few seconds!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"⚠️ - {source.author.mention} - The player is not ready yet, please try again in a few seconds!",
                        ephemeral=True,
                    )

            # Create returns a player if one exists, otherwise creates.
            # This line is important because it ensures that a player always exists for a guild.

            # Most people might consider this a waste of resources for guilds that aren't playing, but this is
            # the easiest and simplest way of ensuring players are created.

            # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
            # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
            # should_connect = ctx.command.name in ("play",)

            if not source.author.voice or not source.author.voice.channel:
                # Our cog_command_error handler catches this and sends it to the voicechannel.
                # Exceptions allow us to "short-circuit" command invocation via checks so the
                # execution state of the command goes no further.
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - Please connect to a voice room to play!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"⚠️ - {source.author.mention} - Please connect to a voice room to play!",
                        ephemeral=True,
                    )

            if not player.is_connected:
                if source.author.voice.channel == source.guild.afk_channel:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"⚠️ - {source.author.mention} - Please be in a non-AFK voice channel!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"⚠️ - {source.author.mention} - Please be in a non-AFK voice channel!",
                            ephemeral=True,
                        )
                elif (
                    "music_channels" in self.bot.configs[source.guild.id]
                    and source.author.voice.channel.id
                    not in self.bot.configs[source.guild.id]["music_channels"]
                ):
                    if isinstance(source, Context):
                        return await source.reply(
                            f"⚠️ - {source.author.mention} - Please be in a valid music channel!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"⚠️ - {source.author.mention} - Please be in a valid music channel!",
                            ephemeral=True,
                        )

                perms = source.author.voice.channel.permissions_for(source.guild.me)
                if not perms.connect or not perms.speak:
                    raise BotMissingPermissions(["connect", "speak"])

                player.store("channel", source.channel.id)
                await source.author.voice.channel.connect(cls=LavalinkVoiceClient)
            else:
                if int(player.channel_id) != source.author.voice.channel.id:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"⚠️ - {source.author.mention} - Please be in the same voice channel as the bot to control the music!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"⚠️ - {source.author.mention} - Please be in the same voice channel as the bot to control the music!",
                            ephemeral=True,
                        )

            return await function(self, source, query, **kwargs)

        return check

    """ COMMANDS """

    @command(
        name="play",
        aliases=["sc_p"],
        usage="<link>|<Title>",
        description="Plays a link or title from a SoundCloud song! It can also play attachments! (supports playlists!)",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    @__ensure_voice
    @max_concurrency(1, per=BucketType.guild)
    async def play_command(self, ctx: Context, query: str = None):
        await self.handle_play(ctx, query)

    @slash_command(
        name="play",
        description="Plays a link or title from a SoundCloud song! (supports playlists!)",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(embed_links=True)
    @__ensure_voice
    @max_concurrency(1, per=BucketType.guild)
    async def play_slash_command(
        self, inter: GuildCommandInteraction, query: str = None
    ):
        await self.handle_play(inter, query)

    """ METHOD(S) """

    async def handle_play(
        self,
        source: Union[Context, GuildCommandInteraction],
        query: Union[str, None],
    ):
        """Searches and plays a song from a given query."""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(source.guild.id)

        if not query and player.paused:
            await player.set_pause(False)
            return await source.send(f"▶️ - Resume Playing!")
        elif not query and (
            isinstance(source, GuildCommandInteraction)
            or not source.message.attachments
        ):
            raise MissingRequiredArgument(
                param=Parameter(name="query", kind=Parameter.KEYWORD_ONLY)
            )
        elif query and (
            isinstance(source, GuildCommandInteraction)
            or not source.message.attachments
        ):
            # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
            query = query.strip("<>")

            # Check if the user input might be a URL. If it isn't, we can Lavalink do a SoundCloud search for it instead.
            if not self.url_rx.match(query):
                query = f"scsearch:{query}"
            elif self.yt_rx.match(query):
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - YouTube links have been disabled due to violation of YouTube terms of service!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"⚠️ - {source.author.mention} - YouTube links have been disabled due to violation of YouTube terms of service!",
                        ephemeral=True,
                    )
        elif (
            isinstance(source, Context)
            and source.message.attachments
            and (
                not source.message.attachments[0].content_type
                or not source.message.attachments[0].content_type.startswith("audio")
            )
        ):
            return await source.reply(
                f"⚠️ - {source.author.mention} - The file you attach to your message is not a valid playable file!",
                delete_after=20,
            )

        results = await player.node.get_tracks(
            query if query else source.message.attachments[0].url
        )

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, results['tracks'] could be an empty array if the query yielded no tracks.
        if results and "exception" in results:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - {results['exception']['message']}",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - {results['exception']['message']}",
                    ephemeral=True,
                )
        elif not results or not results["tracks"]:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The video or playlist you are looking for does not exist!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The video or playlist you are looking for does not exist!",
                    ephemeral=True,
                )

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                audio_track = AudioTrack(track, source.author.id, recommended=True)
                player.add(requester=source.author.id, track=audio_track)

            content = (
                "🎶 - **Adding the Soundcloud playlist to the server playlist:** - 🎶"
            )
        else:
            track = results["tracks"][0]

            if player.is_playing:
                content = "🎶 - **Adding to the server playlist:** - 🎶"
            else:
                content = "🎶 - **Playing:** - 🎶"

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            audio_track = AudioTrack(track, source.author.id, recommended=True)
            player.add(requester=source.author.id, track=audio_track)

        title = (
            track["info"]["title"]
            if track["info"]["title"] != "Unknown title"
            or isinstance(source, ApplicationCommandInteraction)
            or not source.message.attachments
            else source.message.attachments[0].filename
        )
        url = (
            query
            if query and not query.startswith("scsearch")
            else track["info"]["uri"]
        )
        duration = self.bot.utils_class.duration(track["info"]["length"] / 1000)

        em = Embed(
            colour=self.bot.color,
            title=title,
            url=url,
        )

        em.set_author(name=track["info"]["author"])
        em.set_footer(text=f"duration: {duration}")

        self.bot.playlists[source.guild.id].append(
            {
                "type": "Attachment"
                if isinstance(source, Context)
                and source.message.attachments
                and source.message.attachments[0].content_type
                else (
                    "Soundcloud query"
                    if query.startswith("scsearch")
                    else "External link"
                ),
                "title": title,
                "url": url,
                "author": track["info"]["author"],
                "duration": duration,
            }
        )

        if isinstance(source, Context):
            await source.send(content=content, embed=em)
        else:
            await source.response.send_message(content=content, embed=em)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()


def setup(bot):
    bot.add_cog(Dj(bot))
