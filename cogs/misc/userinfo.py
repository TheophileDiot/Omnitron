from typing import Union

from disnake import ApplicationCommandInteraction, Embed, Member
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    guild_only,
    slash_command,
    user_command,
)

from bot import Omnitron


class Miscellaneous(Cog, name="misc.userinfo"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="userinfo",
        aliases=["ui", "userinfos"],
        usage="(@member)",
        description="Get the information from a member or from yourself!",
    )
    @bot_has_permissions(send_messages=True)
    async def userinfo_command(self, ctx: Context, member: Member = None):
        await self.handle_userinfo(ctx, member)

    @slash_command(
        name="userinfo",
        description="Get the information from a member or from yourself!",
    )
    @guild_only()
    async def userinfo_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member = None
    ):
        await self.handle_userinfo(inter, member)

    @user_command(
        name="userinfo",
        description="Get the information from a member or from yourself!",
    )
    @guild_only()
    async def userinfo_user_command(self, inter: ApplicationCommandInteraction):
        await self.handle_userinfo(inter, inter.target)

    """ METHOD(S) """

    async def handle_userinfo(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        member: Member = None,
    ):
        if not member:
            member = source.author

        em = Embed(
            title=f"{member}'s information",
            colour=member.colour,
        )

        if member.avatar:
            em.set_thumbnail(url=member.avatar.url)
            em.set_author(
                name=f"Infos on {member}",
                icon_url=member.avatar.url,
            )
        else:
            em.set_author(name=f"Infos on {member}")

        if source.author.avatar:
            em.set_footer(
                text=source.author.name,
                icon_url=source.author.avatar.url,
            )
        else:
            em.set_footer(
                text=source.author.name,
            )

        em.add_field(name="**User name**", value=member.name, inline=True)
        em.add_field(name="**Discriminator:**", value=member.discriminator, inline=True)
        em.add_field(name="**ID:**", value=member.id, inline=True)
        em.add_field(name="**Status:**", value=member.status, inline=True)
        em.add_field(
            name="**Created on:**",
            value=member.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            inline=True,
        )
        em.add_field(
            name="**Joined the server on:**",
            value=member.joined_at.strftime("%d/%m/%Y, %H:%M:%S"),
            inline=True,
        )
        em.add_field(
            name="**Roles:**",
            value=", ".join(
                [
                    f"`@{role.name}`"
                    for role in member.roles
                    if role != source.guild.default_role
                ]
            )
            if len(member.roles) > 1
            else "No Roles.",
            inline=True,
        )

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.response.send_message(embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
