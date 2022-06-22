from disnake import GuildCommandInteraction, TextInputStyle
from disnake.ext.commands import (
    BucketType,
    Cog,
    cooldown,
    guild_only,
    message_command,
    user_command,
)
from disnake.ui import Modal, TextInput

from bot import Omnitron


class Miscellaneous(Cog, name="misc.report"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ COMMANDS """

    @message_command(name="🛑 Report")
    @guild_only()
    @cooldown(rate=1, per=60, type=BucketType.member)
    async def report_message_command(self, inter: GuildCommandInteraction):
        """
        This message command reports a member's message

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        """
        await inter.response.send_modal(
            modal=Modal(
                title="Report Reason",
                components=[
                    TextInput(
                        label="The reason for the message report",
                        custom_id="reason",
                        style=TextInputStyle.paragraph,
                        placeholder="I report this message because ...",
                        required=True,
                        min_length=10,
                        max_length=1024,
                    )
                ],
                custom_id=f"report_message_{inter.author.id}_{inter.target.channel.id}_{inter.target.id}",
                timeout=300,
            )
        )

    @user_command(name="🛑 Report")
    @guild_only()
    @cooldown(rate=1, per=60, type=BucketType.member)
    async def report_user_command(self, inter: GuildCommandInteraction):
        """
        This user command reports a member

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        """
        await inter.response.send_modal(
            modal=Modal(
                title="Report Reason",
                components=[
                    TextInput(
                        label="The reason for the member report",
                        custom_id="reason",
                        style=TextInputStyle.paragraph,
                        placeholder="I report this member because ...",
                        required=True,
                        min_length=10,
                        max_length=1024,
                    )
                ],
                custom_id=f"report_member_{inter.author.id}_{inter.target.id}",
                timeout=300,
            )
        )


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
