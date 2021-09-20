from re import compile as re_compile

from disnake import Embed, Colour
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
)

from data import Utils


class Dj(Cog, name="dj.playlist"):
    def __init__(self, bot):
        self.bot = bot
        self.url_rx = re_compile(r"https?://(?:www\.)?.+")
        self.path = "temp/musics/"

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
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player or not player.is_playing:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The bot isn't playing!",
                delete_after=20,
            )

        em = Embed(colour=Colour(0xFF0000))  # YTB color

        if position is not None:
            if position < 1 or position > len(self.bot.playlists[ctx.guild.id]):
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - I can't display information about the music in the `{position}{'st' if position == 1 else ('nd' if position == 2 else 'th')}` position because "
                    + (
                        "the position value must be greater than 0!"
                        if position < 1
                        else f"There is only `{len(self.bot.playlists[ctx.guild.id])}` "
                        + (
                            "music present in the playlist!"
                            if len(self.bot.playlists[ctx.guild.id]) == 1
                            else "musics in the playlist!"
                        )
                    ),
                    delete_after=20,
                )

            position -= 1

            em.title = self.bot.playlists[ctx.guild.id][position]["title"]
            em.url = self.bot.playlists[ctx.guild.id][position]["url"]

            em.set_author(
                name=f"Author: {self.bot.playlists[ctx.guild.id][position]['author']}"
            )
            em.set_footer(
                text=f"duration: {self.bot.playlists[ctx.guild.id][position]['duration']}"
            )
            em.add_field(
                name="Type:", value=self.bot.playlists[ctx.guild.id][position]["type"]
            )

            return await ctx.send(
                content=f"🎶 - Music in the `{position + 1}{'st' if position == 1 else ('nd' if position == 2 else 'th')}` position - 🎶",
                embed=em,
            )

        em.title = "Playlist"

        em.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
        )
        em.set_footer(
            text=ctx.guild.owner.display_name,
            icon_url=ctx.guild.owner.avatar.url if ctx.guild.owner.avatar else None,
        )

        x = 0
        nl = "\n"
        while x < len(self.bot.playlists[ctx.guild.id]) and x <= 24:
            if x == 24:
                em.add_field(
                    name="**Too many sounds to display them all**",
                    value="...",
                    inline=False,
                )
            else:
                em.add_field(
                    name=f"**{x + 1}:** {self.bot.playlists[ctx.guild.id][x]['title']}",
                    value=f"**Type:** {self.bot.playlists[ctx.guild.id][x]['type']}{nl}**Author:** {self.bot.playlists[ctx.guild.id][x]['author']}{nl}**Duration:** {self.bot.playlists[ctx.guild.id][x]['duration']}{nl}**URL:** {self.bot.playlists[ctx.guild.id][x]['url']}",
                    inline=True,
                )
                x += 1

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Dj(bot))
