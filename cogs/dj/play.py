from inspect import Parameter
from re import compile as re_compile

from discord import Embed
from discord.ext.commands import (
    BotMissingPermissions,
    bot_has_permissions,
    bot_has_guild_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
)
from discord.ext.commands.errors import MissingRequiredArgument
from lavalink.exceptions import NodeException
from lavalink.models import AudioTrack

from data import Utils


class Dj(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")

    """ CHECKS """

    def __ensure_voice(function):
        async def check(self, ctx: Context, *, query: str = None, **kwargs):
            """This check ensures that the bot and command author are in the same voicechannel."""
            try:
                player = self.bot.lavalink.player_manager.create(
                    ctx.guild.id, endpoint=str(ctx.guild.region)
                )
            except NodeException:
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - The player is not ready yet, please try again in a few seconds!",
                    delete_after=20,
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
                elif (
                    not ctx.guild.me.permissions_in(ctx.author.voice.channel).connect
                    or not ctx.guild.me.permissions_in(ctx.author.voice.channel).speak
                ):
                    raise BotMissingPermissions(["connect", "speak"])

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
        """Searches and plays a song from a given query."""
        async with ctx.typing():
            # Get the player for this guild from cache.
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)

            if not query and player.paused:
                await player.set_pause(False)
                return await ctx.send(f"▶️ - Resume Playing!")
            elif not query and not ctx.message.attachments:
                raise MissingRequiredArgument(
                    param=Parameter(name="query", kind=Parameter.KEYWORD_ONLY)
                )
            elif query and not ctx.message.attachments:
                # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
                query = query.strip("<>")

                # Check if the user input might be a URL. If it isn't, we can Lavalink do a SoundCloud search for it instead.
                if not self.url_rx.match(query):
                    query = f"scsearch:{query}"
            elif ctx.message.attachments and (
                not ctx.message.attachments[0].content_type
                or not ctx.message.attachments[0].content_type.startswith("audio")
            ):
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - The file you attach to your message is not a valid playable file!",
                    delete_after=20,
                )

            results = await player.node.get_tracks(
                query if query else ctx.message.attachments[0].url
            )

            # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
            # ALternatively, results['tracks'] could be an empty array if the query yielded no tracks.
            if results and "exception" in results:
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - {results['exception']['message']}",
                    delete_after=20,
                )
            if not results or not results["tracks"]:
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - The video or playlist you are looking for does not exist!",
                    delete_after=20,
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
                    player.add(requester=ctx.author.id, track=track)

                content = (
                    "🎶 - **Adding the Soundcloud playlist to the server playlist:** - 🎶"
                )
            else:
                track = results["tracks"][0]
                if player.is_playing:
                    content = "🎶 - **Adding to the server playlist:** - 🎶"
                else:
                    content = "🎶 - **Playing:** - 🎶"

            title = (
                track["info"]["title"]
                if track["info"]["title"] != "Unknown title"
                or not ctx.message.attachments
                else ctx.message.attachments[0].filename
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

            self.bot.playlists[ctx.guild.id].append(
                {
                    "type": "Attachment"
                    if ctx.message.attachments
                    and ctx.message.attachments[0].content_type
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
