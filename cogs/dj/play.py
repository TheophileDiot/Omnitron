from inspect import Parameter
from re import compile as re_compile
from typing import Union

from disnake import ApplicationCommandInteraction, Embed, Option, OptionType
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
from lavalink.exceptions import NodeException
from lavalink.models import AudioTrack

from data import Utils


class Dj(Cog, name="dj.play"):
    def __init__(self, bot):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")
        self.yt_rx = re_compile(
            r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?"
        )

    """ CHECKS """

    def __ensure_voice(function):
        async def check(
            self,
            source: Union[Context, ApplicationCommandInteraction],
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
                await source.guild.change_voice_state(
                    channel=source.author.voice.channel
                )
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
        options=[
            Option(
                name="query",
                description="The link or title of the song!",
                type=OptionType.string,
                required=True,
            ),
        ],
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_guild_permissions(connect=True, speak=True)
    @bot_has_permissions(embed_links=True)
    @__ensure_voice
    @max_concurrency(1, per=BucketType.guild)
    async def play_slash_command(
        self, inter: ApplicationCommandInteraction, query: str
    ):
        await self.handle_play(inter, query)

    """ METHOD(S) """

    async def handle_play(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        query: Union[str, None],
    ):
        """Searches and plays a song from a given query."""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(source.guild.id)

        if not query and player.paused:
            await player.set_pause(False)
            return await source.send(f"▶️ - Resume Playing!")
        elif not query and (
            isinstance(source, ApplicationCommandInteraction)
            or not source.message.attachments
        ):
            raise MissingRequiredArgument(
                param=Parameter(name="query", kind=Parameter.KEYWORD_ONLY)
            )
        elif query and (
            isinstance(source, ApplicationCommandInteraction)
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
                player.add(requester=source.author.id, track=track)

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

        # You can attach additional information to audiotracks through kwargs, however this involves
        # constructing the AudioTrack class yourself.
        track = AudioTrack(track, source.author.id, recommended=True)
        player.add(requester=source.author.id, track=track)

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
