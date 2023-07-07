from copy import deepcopy
from typing import List, Union

from disnake import (
    ButtonStyle,
    Colour,
    Embed,
    GuildCommandInteraction,
    MessageInteraction,
)
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
from disnake.ui import button, Button, View

from data import Utils


class Playlist(View):
    def __init__(self, embeds: List[Embed]):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.embed_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True

        # Sets the footer of the embeds with their respective page numbers.
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    @button(emoji="⏪", style=ButtonStyle.blurple)
    async def first_page(self, button: Button, interaction: MessageInteraction):
        self.embed_count = 0
        embed = self.embeds[self.embed_count]
        embed.set_footer(text=f"Page 1 of {len(self.embeds)}")

        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="◀", style=ButtonStyle.secondary)
    async def prev_page(self, button: button, interaction: MessageInteraction):
        self.embed_count -= 1
        embed = self.embeds[self.embed_count]

        self.next_page.disabled = False
        self.last_page.disabled = False
        if self.embed_count == 0:
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="❌", style=ButtonStyle.red)
    async def remove(self, button: button, interaction: MessageInteraction):
        await interaction.response.edit_message(view=None)

    @button(emoji="▶", style=ButtonStyle.secondary)
    async def next_page(self, button: button, interaction: MessageInteraction):
        self.embed_count += 1
        embed = self.embeds[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @button(emoji="⏩", style=ButtonStyle.blurple)
    async def last_page(self, button: button, interaction: MessageInteraction):
        self.embed_count = len(self.embeds) - 1
        embed = self.embeds[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


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
        if not self.bot.playlists.get(source.guild.id):
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - There is no playlist in this server.",
                    delete_after=20,
                )
            else:
                return await source.followup.send(
                    f"⚠️ - {source.author.mention} - There is no playlist in this server.",
                    ephemeral=True,
                )

        if not isinstance(source, Context):
            await source.response.defer()

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

        default_em = deepcopy(em)
        playlist = deepcopy(self.bot.playlists[source.guild.id])

        nl = "\n"
        embeds = []
        for x in range(len(playlist)):
            if x != 0 and x % 25 == 0:
                embeds.append(em.copy())
                em = default_em.copy()

            em.add_field(
                name=f"**{x + 1}:** {playlist[x]['title']}"
                + (" - *currently playing*" if x == 0 else ""),
                value=f"**Type:** {playlist[x]['type']}{nl}**Author:** {playlist[x]['author']}{nl}**Duration:** {playlist[x]['duration']}{nl}**URL:** {playlist[x]['url']}",
                inline=True,
            )

        if isinstance(source, Context):
            await source.send(embed=embeds[0], view=Playlist(embeds))
        else:
            await source.response.send_message(embed=embeds[0], view=Playlist(embeds))


def setup(bot):
    bot.add_cog(Dj(bot))
