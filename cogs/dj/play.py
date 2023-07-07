from functools import wraps
from inspect import Parameter
from os import getenv
from re import compile as re_compile
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from typing import List, Optional, Union
from youtube_dl import utils, YoutubeDL

from disnake import (
    Attachment,
    Client as botClient,
    Colour,
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
    guild_only,
    max_concurrency,
    slash_command,
)
from disnake.ext.commands.errors import MissingRequiredArgument
from lavalink import add_event_hook, Client
from lavalink.events import NodeConnectedEvent, QueueEndEvent, TrackEndEvent
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
        super().__init__(client, channel)
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

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_deaf: bool = True,
        self_mute: bool = False,
    ) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel, self_mute=self_mute, self_deaf=self_deaf
        )

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

        # Clear the queue to ensure old tracks don't start playing
        player.queue.clear()

        if player.is_playing:
            # Stop the current track so Lavalink consumes less resources.
            await player.stop()

        # update the channel_id of the player to None
        player.channel_id = None
        self.cleanup()


class Dj(Cog, name="dj.play"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")
        self.sp_url_rx = re_compile(
            r"^https:\/\/open.spotify.com\/(playlist|track)\/[a-zA-Z0-9]+.*$"
        )
        self.yt_rx = re_compile(
            r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"
        )
        utils.bug_reports_message = lambda: ""
        self.ytdl = YoutubeDL(
            {
                "format": "worstaudio/worst",
                "outtmpl": "temp/musics/%(title)s.%(ext)s",
                "download_archive": "temp/musics.txt",
                "restrictfilenames": True,
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": False,
                "logtostderr": False,
                "quiet": True,
                "no_warnings": True,
                "verbose": False,
                "default_search": "auto",
                # bind to ipv4 since ipv6 addresses cause issues sometimes
                "source_address": "0.0.0.0",
            }
        )

        self.spotify_client: Optional[Spotify] = None
        if getenv("SPOTIFY_CLIENT_ID", False) and getenv(
            "SPOTIFY_CLIENT_SECRET", False
        ):
            self.spotify_client: Spotify = Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=getenv("SPOTIFY_CLIENT_ID", ""),
                    client_secret=getenv("SPOTIFY_CLIENT_SECRET", ""),
                )
            )

    """ EVENTS """

    @Cog.listener()
    async def on_ready(self):
        # This ensures the client isn't overwritten during cog reloads.
        if not hasattr(self.bot, "lavalink"):
            self.bot.lavalink = Client(self.bot.user.id)
            # Host, Port, Password, Region, Name
            self.bot.lavalink.add_node(
                "lavalink", 2333, "youshallnotpass", "eu", "default-node"
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
        @wraps(function)
        async def check(
            self,
            source,
            query: str = None,
            audio_file: Attachment = None,
        ):
            """This check ensures that the bot and command author are in the same voicechannel."""
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

            try:
                player = self.bot.lavalink.player_manager.create(
                    source.guild.id, endpoint=source.author.voice.channel.rtc_region
                )
            except:
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

            return await function(self, source, query, audio_file=audio_file)

        return check

    """ COMMANDS """

    @command(
        name="play",
        aliases=["sc_p"],
        usage="<link>|<Title>",
        description="Plays a link or title from a YouTube/SoundCloud or Spotify song or playlist or an audio file!",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    @__ensure_voice
    @max_concurrency(1, per=BucketType.guild)
    async def play_command(self, source: Context, query: str = None, **kwargs):
        """
        This command plays a link or title from a YouTube/SoundCloud or Spotify song or playlist or an audio file!

        Parameters
        ----------
        source: :class:`disnake.ext.commands.Context`
            The command context
        query: :class:`str` optional
            The link or YouTube/SoundCloud title
        """
        await self.handle_play(source, query)

    @slash_command(
        name="play",
        description="Plays a link or title from a YouTube/SoundCloud or Spotify song or playlist or an audio file!",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(embed_links=True)
    @__ensure_voice
    @max_concurrency(1, per=BucketType.guild)
    async def play_slash_command(
        self,
        source: GuildCommandInteraction,
        query: str = None,
        audio_file: Attachment = None,
    ):
        """
        This slash command plays a link or title from a YouTube/SoundCloud or Spotify song or playlist or an audio file!

        Parameters
        ----------
        source: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        query: :class:`str` optional
            The link or YouTube/SoundCloud title
        audio_file: :class:`disnake.ext.commands.Attachment` optional
            The audio file to play
        """
        await self.handle_play(source, query, audio_file=audio_file)

    """ METHOD(S) """

    async def add_song_to_queue(
        self,
        source: GuildCommandInteraction,
        track: dict,
        player,
        query: str,
        audio_file: Attachment = None,
        multiple: bool = False,
    ) -> Optional[dict]:
        yt_infos = None
        try:
            if self.yt_rx.match(track["info"]["uri"]) and multiple is False:
                yt_infos = self.ytdl.extract_info(track["info"]["uri"], download=False)
        except Exception as e:
            if not f"{e}".endswith("This video may be inappropriate for some users."):
                pass
            else:
                return await source.followup.send(
                    f"⚠️ - {source.author.mention} - This video is not suitable for some users ({track['info']['uri']})! (I can't play some age restricted videos)",
                    ephemeral=True,
                )

        # You can attach additional information to audiotracks through kwargs, however this involves
        # constructing the AudioTrack class yourself.
        audio_track = AudioTrack(track, source.author.id, recommended=True)
        player.add(requester=source.author.id, track=audio_track)

        if yt_infos:
            title = yt_infos["title"]
            url = (
                yt_infos["webpage_url"]
                if "webpage_url" in yt_infos
                else yt_infos["video_url"]
            )
            duration = self.bot.utils_class.duration(yt_infos["duration"])
            author = f"Channel: {yt_infos['channel']}"
        else:
            title = (
                track["info"]["title"]
                if track["info"]["title"] != "Unknown title" or audio_file is None
                else audio_file.filename
            )
            url = (
                query
                if query and not query.startswith("ytsearch")
                else track["info"]["uri"]
            )
            duration = self.bot.utils_class.duration(track["info"]["duration"] / 1000)
            author = track["info"]["author"]

        self.bot.playlists[source.guild.id].append(
            {
                "type": "Attachment"
                if audio_file and audio_file.content_type
                else (
                    "Search query" if query.startswith("ytsearch") else "External link"
                ),
                "title": title,
                "url": url,
                "author": author.replace("Channel: ", ""),
                "duration": duration,
                "thumbnail": yt_infos["thumbnail"] if yt_infos is not None else None,
            }
        )

        return yt_infos

    async def add_spotify_song_to_queue(
        self,
        source: Union[Context, GuildCommandInteraction],
        track: dict,
        player,
        query: str = "ytsearch",
        multiple: bool = False,
    ) -> Optional[dict]:
        try:
            results = await player.node.get_tracks(
                f"ytsearch:{track['name']} {', '.join(a['name'] for a in track['artists'])}"
            )
        except TimeoutError:
            return

        if (
            not results or results and "exception" in results or not results["tracks"]
        ) or (results and "exception" in results):
            return

        track = results["tracks"][0]
        return await self.add_song_to_queue(
            source, track, player, query, multiple=multiple
        )

    async def add_songs_to_queue(
        self,
        source: Union[Context, GuildCommandInteraction],
        tracks: List[dict],
        player,
        query: str = "ytsearch",
        _type: str = "regular",
    ):
        for track in tracks:
            if player.is_playing:
                # Add all of the tracks from the playlist to the queue.
                if _type == "regular":
                    await self.add_song_to_queue(
                        source, track, player, query, multiple=True
                    )
                else:
                    await self.add_spotify_song_to_queue(
                        source, track, player, multiple=True
                    )

        if not player.is_playing:
            self.bot.playlists[source.guild.id] = []

    async def handle_play(
        self,
        source: Union[Context, GuildCommandInteraction],
        query: str = None,
        *,
        audio_file: Attachment = None,
    ):
        """Searches and plays a song from a given query."""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(source.guild.id)
        spotify_track: bool = False

        if not isinstance(source, Context):
            await source.response.defer()

        if (
            isinstance(source, Context)
            and source.message.attachments
            and audio_file is None
        ):
            audio_file = source.message.attachments[0]

        if not query and player.paused:
            await player.set_pause(False)
            return await source.send(f"▶️ - Resume Playing!")
        elif not query and audio_file is None:
            raise MissingRequiredArgument(
                param=Parameter(name="query", kind=Parameter.KEYWORD_ONLY)
            )
        elif query and audio_file is None:
            # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
            query = query.strip("<>")

            if self.sp_url_rx.search(query):
                spotify_track = True
                if self.spotify_client is None:
                    if isinstance(source, Context):
                        return await source.reply(
                            f"⚠️ - {source.author.mention} - Cannot play Spotify songs right now!",
                            delete_after=20,
                        )
                    else:
                        return await source.followup.send(
                            f"⚠️ - {source.author.mention} - Cannot play Spotify songs right now!",
                            ephemeral=True,
                        )

                match = self.sp_url_rx.search(query)
                url = match.group(0)
                sp_type = match.group(1)

                if sp_type == "track":
                    try:
                        track = self.spotify_client.track(url)
                        query = f"ytsearch:{track['name']} {', '.join(a['name'] for a in track['artists'])}"
                    except (ConnectionError, SpotifyException):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"⚠️ - {source.author.mention} - Cannot find the spotify track {url}!",
                                delete_after=20,
                            )
                        else:
                            return await source.followup.send(
                                f"⚠️ - {source.author.mention} - Cannot find the spotify track {url}!",
                                ephemeral=True,
                            )
                elif sp_type == "playlist":
                    try:
                        playlist = self.spotify_client.user_playlist_tracks(
                            user="", playlist_id=url
                        )
                        query = [
                            {
                                "name": track["track"]["name"],
                                "artists": track["track"]["artists"],
                            }
                            for track in playlist["items"]
                        ]
                    except (ConnectionError, SpotifyException):
                        if isinstance(source, Context):
                            return await source.reply(
                                f"⚠️ - {source.author.mention} - Cannot find the spotify playlist {url}! Is the playlist public?",
                                delete_after=20,
                            )
                        else:
                            return await source.followup.send(
                                f"⚠️ - {source.author.mention} - Cannot find the spotify playlist {url}! Is the playlist public?",
                                ephemeral=True,
                            )
            # Check if the user input might be a URL. If it isn't, we can Lavalink do a search for it instead.
            elif not self.url_rx.match(query):
                query = f"ytsearch:{query}"
            # elif self.yt_rx.match(query):
            #     if isinstance(source, Context):
            #         return await source.reply(
            #             f"⚠️ - {source.author.mention} - YouTube links have been disabled due to violation of YouTube terms of service!",
            #             delete_after=20,
            #         )
            #     else:
            #         return await source.response.send_message(
            #             f"⚠️ - {source.author.mention} - YouTube links have been disabled due to violation of YouTube terms of service!",
            #             ephemeral=True,
            #         )

        if audio_file:
            query = audio_file.url

            if not audio_file.content_type or not audio_file.content_type.startswith(
                "audio"
            ):
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - The file you attach to your message is not a valid playable file!",
                        delete_after=20,
                    )
                else:
                    return await source.followup.send(
                        f"⚠️ - {source.author.mention} - The file you attach to your message is not a valid playable file!",
                        ephemeral=True,
                    )

        if not isinstance(query, list):
            try:
                results = await player.node.get_tracks(query)
            except TimeoutError:
                return await source.reply(
                    f"⚠️ - {source.author.mention} - Your query timed out!",
                    delete_after=20,
                )

            if (
                not audio_file
                and (not results or not results["tracks"])
                and query
                and query.startswith("ytsearch:")
            ):
                query = query.replace("ytsearch:", "scsearch:")
                try:
                    results = await player.node.get_tracks(query)
                except TimeoutError:
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - Your query timed out!",
                        delete_after=20,
                    )

            # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
            # ALternatively, results['tracks'] could be an empty array if the query yielded no tracks.
            if not results or not results["tracks"]:
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - The video or playlist you are looking for does not exist!",
                        delete_after=20,
                    )
                else:
                    return await source.followup.send(
                        f"⚠️ - {source.author.mention} - The video or playlist you are looking for does not exist!",
                        ephemeral=True,
                    )

            # Valid loadTypes are:
            #   TRACK_LOADED    - single video/direct URL)
            #   PLAYLIST_LOADED - direct URL to playlist)
            #   SEARCH_RESULT   - query prefixed with either ytsearch:.
            #   NO_MATCHES      - query yielded no results
            #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
            if results["loadType"] == "PLAYLIST_LOADED":
                tracks = results["tracks"]

                yt_infos = await self.add_song_to_queue(
                    source, tracks.pop(0), player, query
                )

                self.bot.loop.create_task(
                    self.add_songs_to_queue(source, tracks, player)
                )

                content = f"🎶 - **Adding the playlist to the server playlist:** - 🎶"
            else:
                track = results["tracks"][0]

                if player.is_playing:
                    content = "🎶 - **Adding to the server playlist:** - 🎶"
                else:
                    content = "🎶 - **Playing:** - 🎶"

                yt_infos = await self.add_song_to_queue(
                    source, track, player, query, audio_file
                )
        else:
            yt_infos = await self.add_spotify_song_to_queue(
                source, query.pop(0), player
            )

            self.bot.loop.create_task(
                self.add_songs_to_queue(source, query, player, _type="spotify")
            )

            content = f"🎶 - **Adding the spotify playlist to the server playlist:** - 🎶"

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

        colour = Colour(0xFF0000) if not spotify_track else Colour(0x1DB954)
        if yt_infos and isinstance(yt_infos, dict):
            title = yt_infos["title"]
            url = (
                yt_infos["webpage_url"]
                if "webpage_url" in yt_infos
                else yt_infos["video_url"]
            )
            duration = self.bot.utils_class.duration(yt_infos["duration"])
            author = f"Channel: {yt_infos['channel']}"
        else:
            title = (
                track["info"]["title"]
                if track["info"]["title"] != "Unknown title" or audio_file is None
                else audio_file.filename
            )
            url = (
                query
                if query and not query.startswith("ytsearch")
                else track["info"]["uri"]
            )
            duration = self.bot.utils_class.duration(track["info"]["duration"] / 1000)
            author = track["info"]["author"]

        em = Embed(
            colour=colour,
            title=title,
            url=url,
        )

        if yt_infos and isinstance(yt_infos, dict):
            em.set_thumbnail(url=yt_infos["thumbnail"])

        em.set_author(name=author)
        em.set_footer(text=f"duration: {duration}")

        if isinstance(source, Context):
            await source.send(content=content, embed=em)
        else:
            await source.followup.send(content=content, embed=em)


def setup(bot):
    bot.add_cog(Dj(bot))
