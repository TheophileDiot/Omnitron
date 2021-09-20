from typing import Union

from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    slash_command,
)

from bot import Omnitron


class Miscellaneous(Cog, name="misc.serverinfos"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="serverinfos",
        aliases=["si", "serverinfo"],
        description="Get server's information!",
    )
    @bot_has_permissions(send_messages=True)
    async def serverinfos_command(self, ctx: Context):
        await self.handle_serverinfos(ctx)

    @slash_command(
        name="serverinfos",
        aliases=["si", "serverinfo"],
        description="Get server's information!",
    )
    async def serverinfos_slash_command(self, inter: ApplicationCommandInteraction):
        await self.handle_serverinfos(inter)

    """ METHOD(S) """

    async def handle_serverinfos(
        self, source: Union[Context, ApplicationCommandInteraction]
    ):
        em = Embed(
            title=f"{source.guild.name} server information", colour=self.bot.color
        )

        em.set_thumbnail(url=source.guild.icon.url if source.guild.icon else None)
        em.set_author(
            name=source.guild.name,
            icon_url=source.guild.icon.url if source.guild.icon else None,
        )
        em.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        em.add_field(name="**Server's name:**", value=source.guild.name, inline=True)
        em.add_field(
            name="**Creation date:**",
            value=source.guild.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            inline=True,
        )
        em.add_field(name="**Server's owner:**", value=source.guild.owner, inline=True)
        em.add_field(
            name="**Number of members:**", value=source.guild.member_count, inline=True
        )
        em.add_field(
            name="**Number of roles:**", value=str(len(source.guild.roles)), inline=True
        )
        em.add_field(
            name="**Number of text channels:**",
            value=str(len(source.guild.text_channels)),
            inline=True,
        )
        em.add_field(
            name="**Number of voice channels:**",
            value=str(len(source.guild.voice_channels)),
            inline=True,
        )

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
