from inspect import Parameter
from re import compile as re_compile

from discord import Embed, Colour
from discord.ext.commands import (
    bot_has_permissions,
    bot_has_guild_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
)
from discord.ext.commands.errors import MissingRequiredArgument
from lavalink.models import AudioTrack
from youtube_dl import utils, YoutubeDL

from data import Utils


class Dj(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")
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

    """ CHECKS """

    def __ensure_voice(function):
        async def check(self, ctx: Context, *, query: str = None, **kwargs):
            """This check ensures that the bot and command author are in the same voicechannel."""
            player = self.bot.lavalink.player_manager.create(
                ctx.guild.id, endpoint=str(ctx.guild.region)
            )
            # Create returns a player if one exists, otherwise creates.
            # This line is important because it ensures that a player always exists for a guild.

            # Most people might consider this a waste of resources for guilds that aren't playing, but this is
            # the easiest and simplest way of ensuring players are created.

            # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
            # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
            should_connect = ctx.command.name in ("play",)

            if not ctx.author.voice or not ctx.author.voice.channel:
                # Our cog_command_error handler catches this and sends it to the voicechannel.
                # Exceptions allow us to "short-circuit" command invocation via checks so the
                # execution state of the command goes no further.
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - Please connect to a voice room to play!",
                    delete_after=20,
                )

            if not player.is_connected:
                if not should_connect:
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - The player is not connected, please try again!",
                        delete_after=20,
                    )
                elif ctx.author.voice.channel == ctx.guild.afk_channel:
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - Please be in a non-AFK voice channel!",
                        delete_after=20,
                    )
                elif (
                    "music_channels" in self.bot.configs[ctx.guild.id]
                    and ctx.author.voice.channel.id
                    not in self.bot.configs[ctx.guild.id]["music_channels"]
                ):
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - Please be in a valid music channel!",
                        delete_after=20,
                    )

                player.store("channel", ctx.channel.id)
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
            else:
                if int(player.channel_id) != ctx.author.voice.channel.id:
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - Please be in the same voice channel as the bot to control the music!",
                        delete_after=20,
                    )
            return await function(self, ctx, query, **kwargs)

        return check

    """ COMMANDS """

    @command(
        name="play",
        aliases=["yt_p"],
        usage="<Youtube_link>|<Title>",
        description="Plays a link or title from a Youtube video! (supports playlists!)",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(send_messages=True, embed_links=True)
    @max_concurrency(1, per=BucketType.guild)
    @__ensure_voice
    async def play_command(self, ctx: Context, query: str = None):
        """Searches and plays a song from a given query."""
        async with ctx.typing():
            # Get the player for this guild from cache.
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)

            if not query and player.paused:
                await player.set_pause(False)
                return await ctx.send(f"▶️ - Resume Playing!")
            elif not query:
                raise MissingRequiredArgument(
                    param=Parameter(name="query", kind=Parameter.KEYWORD_ONLY)
                )

            # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
            query = query.strip("<>")

            # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
            # SoundCloud searching is possible by prefixing "scsearch:" instead.
            if not self.url_rx.match(query):
                query = f"ytsearch:{query}"

            # Get the results for the query from Lavalink.
            results = await player.node.get_tracks(query)

            # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
            # ALternatively, results['tracks'] could be an empty array if the query yielded no tracks.
            if not results or not results["tracks"]:
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - The video or playlist you are looking for does not exist!",
                    delete_after=20,
                )

            content = ""

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
                    player.add(requester=ctx.author.id, track=track)

                content = (
                    "🎶 - **Adding the YouTube playlist to the server playlist:** - 🎶"
                )
            else:
                track = results["tracks"][0]
                if player.is_playing:
                    content = "🎶 - **Adding to the server playlist:** - 🎶"
                else:
                    content = "🎶 - **Playing:** - 🎶"

            try:
                infos_vid = self.ytdl.extract_info(
                    track["info"]["uri"], download=not False
                )
            except Exception as e:
                if not f"{e}".endswith(
                    "This video may be inappropriate for some users."
                ):
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - An error occurred while retrieving the video information, please try again in a few moments!",
                        delete_after=20,
                    )
                else:
                    return await ctx.reply(
                        f"⚠️ - {ctx.author.mention} - This video is not suitable for some users! (I can't play some age restricted videos)",
                        delete_after=20,
                    )

            em = Embed(
                colour=Colour(0xFF0000),  # YTB color
                title=infos_vid["title"],
                description=infos_vid["description"]
                if len(infos_vid["description"]) < 1024
                else infos_vid["description"][0:1021] + "...",
                url=infos_vid["webpage_url"]
                if "webpage_url" in infos_vid
                else infos_vid["video_url"],
            )

            em.set_thumbnail(url=infos_vid["thumbnail"])
            em.set_author(name=f"Channel: {infos_vid['channel']}")
            em.set_footer(
                text=f"duration: {self.bot.utils_class.duration(infos_vid['duration'])}"
            )

            self.bot.playlists[ctx.guild.id].append(
                {
                    "thumbnail": infos_vid["thumbnail"],
                    "title": infos_vid["title"],
                    "description": infos_vid["description"]
                    if len(infos_vid["description"]) < 1024
                    else infos_vid["description"][0:1021] + "...",
                    "url": infos_vid["webpage_url"]
                    if "webpage_url" in infos_vid
                    else infos_vid["video_url"],
                    "author": infos_vid["channel"],
                    "duration": self.bot.utils_class.duration(infos_vid["duration"]),
                }
            )

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            track = AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

            await ctx.send(content=content, embed=em)

            # We don't want to call .play() if the player is playing as that will effectively skip
            # the current track.
            if not player.is_playing:
                await player.play()


def setup(bot):
    bot.add_cog(Dj(bot))
