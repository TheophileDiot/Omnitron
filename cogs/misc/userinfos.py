from typing import Union

from disnake import ApplicationCommandInteraction, Embed, Member, Option, OptionType
from disnake.ext.commands import (
    bot_has_permissions,
    Cog,
    command,
    Context,
    slash_command,
)

from bot import Omnitron


class Miscellaneous(Cog, name="misc.userinfos"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="userinfos",
        aliases=["ui", "userinfo"],
        usage="(@member)",
        description="Get the information from a member or from yourself!",
    )
    @bot_has_permissions(send_messages=True)
    async def userinfos_command(self, ctx: Context, member: Member = None):
        await self.handle_userinfos(ctx, member)

    @slash_command(
        name="userinfos",
        aliases=["ui", "userinfo"],
        description="Get the information from a member or from yourself!",
        options=[
            Option(
                name="member",
                description="Mention the member to get information from",
                type=OptionType.user,
                required=False,
            ),
        ],
    )
    @bot_has_permissions(send_messages=True)
    async def userinfos_slash_command(self, ctx: Context, member: Member = None):
        await self.handle_userinfos(ctx, member)

    """ METHOD(S) """

    async def handle_userinfos(
        self, source: Union[Context, ApplicationCommandInteraction], member: Member
    ):
        if not member:
            member = source.author

        em = Embed(
            title=f"{member.display_name}'s information",
            colour=member.colour,
        )

        em.set_thumbnail(url=member.avatar.url if member.avatar else None)
        em.set_author(
            name=f"Infos on {member}",
            icon_url=member.avatar.url if member.avatar else None,
        )
        em.set_footer(
            text=source.author.name,
            icon_url=source.author.avatar.url if source.author.avatar else None,
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
