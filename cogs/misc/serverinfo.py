from typing import Union

from disnake import Embed, GuildCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    slash_command,
)

from bot import Omnitron


class Miscellaneous(Cog, name="misc.serverinfo"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="serverinfo",
        aliases=["si", "serverinfos"],
        description="Get server's information!",
    )
    @bot_has_permissions(send_messages=True)
    async def serverinfo_command(self, ctx: Context):
        await self.handle_serverinfo(ctx)

    @slash_command(
        name="serverinfo",
        description="Get server's information!",
    )
    async def serverinfo_slash_command(self, inter: GuildCommandInteraction):
        await self.handle_serverinfo(inter)

    """ METHOD(S) """

    async def handle_serverinfo(
        self, source: Union[Context, GuildCommandInteraction]
    ):
        em = Embed(
            title=f"{source.guild.name} server information", colour=self.bot.color
        )

        if source.guild.icon:
            em.set_thumbnail(url=source.guild.icon.url)
            em.set_author(name=source.guild.name, icon_url=source.guild.icon.url)
        else:
            em.set_author(name=source.guild.name)

        if self.bot.user.avatar:
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            em.set_footer(text=self.bot.user.name)

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
