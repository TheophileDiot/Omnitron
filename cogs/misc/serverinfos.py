from discord import Embed
from discord.ext.commands import Cog, command, Context

from bot import Omnitron


class Miscellaneous(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="serverinfos",
        aliases=["si", "serverinfo"],
        description="Get server's informations!",
    )
    async def serverinfos_command(self, ctx: Context):
        em = Embed(title=f"{ctx.guild.name} server information", colour=self.bot.color)

        em.set_thumbnail(url=ctx.guild.icon_url)
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        em.add_field(name="**Server's name:**", value=ctx.guild.name, inline=True)
        em.add_field(
            name="**Creation date:**",
            value=ctx.guild.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            inline=True,
        )
        em.add_field(name="**Server's owner:**", value=ctx.guild.owner, inline=True)
        em.add_field(
            name="**Number of members:**", value=ctx.guild.member_count, inline=True
        )
        em.add_field(
            name="**Number of roles:**", value=str(len(ctx.guild.roles)), inline=True
        )
        em.add_field(
            name="**Number of text channels:**",
            value=str(len(ctx.guild.text_channels)),
            inline=True,
        )
        em.add_field(
            name="**Number of voice channels:**",
            value=str(len(ctx.guild.voice_channels)),
            inline=True,
        )

        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
