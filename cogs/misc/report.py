from datetime import datetime

from disnake import ApplicationCommandInteraction, Colour, Embed
from disnake.ext.commands import (
    BucketType,
    Cog,
    guild_only,
    message_command,
    cooldown,
)

from bot import Omnitron


class Miscellaneous(Cog, name="misc.report"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ COMMANDS """

    @message_command(name="🛑 Report")
    @guild_only()
    @cooldown(rate=1, per=60, type=BucketType.member)
    async def report_message_command(self, inter: ApplicationCommandInteraction):
        """
        This message command reports a member's message

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        em = Embed(
            title=f"The member {inter.author} reported {inter.target.author}'s message",
            description=f'Message content: "{inter.target.clean_content}"\n'
            f"Report date: `{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}`\n"
            f"URL to the message: {inter.target.jump_url}",
            colour=Colour.red(),
        )

        if inter.target.author.avatar:
            em.set_thumbnail(url=inter.target.author.avatar.url)

        await self.bot.utils_class.send_message_to_mods("", inter.guild.id, em)

        await inter.response.send_message(
            "ℹ️ - Your report has been successfully sent to the server's moderators!",
            ephemeral=True,
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
