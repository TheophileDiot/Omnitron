from discord import Embed, Member
from discord.ext.commands import Cog, command, Context

from bot import Omnitron


class Miscellaneous(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="userinfos",
        aliases=["ui", "userinfo"],
        usage="(@member)",
        description="Get the information from a member or from yourself!",
    )
    async def userinfos_command(self, ctx: Context, member: Member = None):
        if not member:
            member = ctx.author

        em = Embed(
            title=f"{member.display_name}'s information",
            colour=member.colour,
        )

        em.set_thumbnail(url=member.avatar_url)
        em.set_author(name=f"Infos on {member}", icon_url=member.avatar_url)
        em.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

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
                    if role != ctx.guild.default_role
                ]
            )
            if len(member.roles) > 1
            else "No Roles.",
            inline=True,
        )

        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
