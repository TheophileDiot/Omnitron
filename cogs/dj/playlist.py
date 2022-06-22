from typing import Union

from disnake import Colour, Embed, GuildCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    guild_only,
    max_concurrency,
    slash_command,
)

from data import Utils


class Dj(Cog, name="dj.playlist"):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="playlist",
        aliases=["queue", "list"],
        usage="(position)",
        description="Displays the information for the music in the playlist or for a particular one.",
    )
    @Utils.check_bot_starting()
    @bot_has_permissions(send_messages=True, embed_links=True)
    @max_concurrency(1, per=BucketType.guild)
    async def playlist_command(self, ctx: Context, position: int = None):
        """
        This command displays the information for the music in the playlist or for a particular one.

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        position: :class:`int` optional
            The position of the music in the playlist
        """
        await self.handle_playlist(ctx, position)

    @slash_command(
        name="playlist",
        description="Displays the information for the music in the playlist or for a particular one.",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @bot_has_permissions(embed_links=True)
    @max_concurrency(1, per=BucketType.guild)
    async def playlist_slash_command(
        self, inter: GuildCommandInteraction, position: int = None
    ):
        """
        This slash command displays the information for the music in the playlist or for a particular one.

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        position: :class:`int` optional
            The position of the music in the playlist
        """
        await self.handle_playlist(inter, position)

    """ METHOD(S) """

    async def handle_playlist(
        self,
        source: Union[Context, GuildCommandInteraction],
        position: int = None,
    ):
        em = Embed(colour=Colour(0xFF0000))  # YTB color

        if position is not None:
            if position < 1 or position > len(self.bot.playlists[source.guild.id]):
                resp = (
                    f"ℹ️ - {source.author.mention} - I can't display information about the music in the `{position}{'st' if position == 1 else ('nd' if position == 2 else 'th')}` position because "
                    + (
                        "the position value must be greater than 0!"
                        if position < 1
                        else f"There is only `{len(self.bot.playlists[source.guild.id])}` "
                        + (
                            "music present in the playlist!"
                            if len(self.bot.playlists[source.guild.id]) == 1
                            else "musics in the playlist!"
                        )
                    )
                )

                if isinstance(source, Context):
                    return await source.reply(
                        resp,
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        resp,
                        ephemeral=True,
                    )

            position -= 1

            em.title = self.bot.playlists[source.guild.id][position]["title"] + (
                " - *currently playing*" if position == 0 else ""
            )
            em.url = self.bot.playlists[source.guild.id][position]["url"]

            if self.bot.playlists[source.guild.id][position].get("thumbnail"):
                em.set_thumbnail(
                    url=self.bot.playlists[source.guild.id][position]["thumbnail"]
                )

            em.set_author(
                name=f"Author: {self.bot.playlists[source.guild.id][position]['author']}"
            )
            em.set_footer(
                text=f"duration: {self.bot.playlists[source.guild.id][position]['duration']}"
            )
            em.add_field(
                name="Type:",
                value=self.bot.playlists[source.guild.id][position]["type"],
            )

            if isinstance(source, Context):
                return await source.send(
                    content=f"🎶 - Music in the `{position + 1}{'st' if position == 1 else ('nd' if position == 2 else 'th')}` position - 🎶",
                    embed=em,
                )
            else:
                return await source.response.send_message(
                    content=f"🎶 - Music in the `{position + 1}{'st' if position == 1 else ('nd' if position == 2 else 'th')}` position - 🎶",
                    embed=em,
                )

        em.title = "Playlist"

        em.set_author(
            name=f"{source.author}",
            icon_url=source.author.avatar.url if source.author.avatar else None,
        )

        if self.bot.user.avatar:
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            em.set_footer(text=self.bot.user.name)

        if self.bot.playlists[source.guild.id][0].get("thumbnail"):
            em.set_thumbnail(url=self.bot.playlists[source.guild.id][0]["thumbnail"])

        x = 0
        nl = "\n"
        while x < len(self.bot.playlists[source.guild.id]) and x <= 24:
            if x == 24:
                em.add_field(
                    name="**Too many sounds to display them all**",
                    value="...",
                    inline=False,
                )
            else:
                em.add_field(
                    name=f"**{x + 1}:** {self.bot.playlists[source.guild.id][x]['title']}"
                    + (" - *currently playing*" if x == 0 else ""),
                    value=f"**Type:** {self.bot.playlists[source.guild.id][x]['type']}{nl}**Author:** {self.bot.playlists[source.guild.id][x]['author']}{nl}**Duration:** {self.bot.playlists[source.guild.id][x]['duration']}{nl}**URL:** {self.bot.playlists[source.guild.id][x]['url']}",
                    inline=True,
                )
                x += 1

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Dj(bot))
