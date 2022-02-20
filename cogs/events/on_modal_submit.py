from datetime import datetime

from disnake import Colour, Embed, Message, ModalInteraction, NotFound
from disnake.ext.commands import Cog

from bot import Omnitron


class Events(Cog, name="events.on_modal_submit"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_modal_submit(self, interaction: ModalInteraction):
        await self.bot.wait_until_ready()

        if interaction.custom_id.startswith("report_message"):
            channel_id = int(interaction.custom_id.split("_")[3])
            message_id = int(interaction.custom_id.split("_")[-1])

            try:
                channel = self.bot.get_channel(
                    channel_id
                ) or await self.bot.fetch_channel(channel_id)
                message: Message = await channel.fetch_message(message_id)
            except NotFound:
                interaction.response.send_message(
                    "⚠️ - Your report couldn't have been done because either the channel or the message no longer exist - ⚠️",
                    ephemeral=True,
                )
                return

            em = Embed(
                title=f"The member {interaction.author} reported {message.author}'s message",
                description=f'Message content: "{message.clean_content}"\n'
                f"Report date: `{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}`\n"
                f"URL to the message: {message.jump_url}",
                colour=Colour.red(),
            )

            if message.author.avatar:
                em.set_thumbnail(url=message.author.avatar.url)
        elif interaction.custom_id.startswith("report_member"):
            member_id = int(interaction.custom_id.split("_")[-1])

            try:
                member = interaction.guild.get_member(
                    member_id
                ) or await interaction.guild.fetch_member(member_id)
            except NotFound:
                interaction.response.send_message(
                    "⚠️ - Your report couldn't have been done because the member is no longer in the guild - ⚠️",
                    ephemeral=True,
                )
                return

            em = Embed(
                title=f"The member {interaction.author} reported {member}",
                description=f"Report date: `{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}`",
                colour=Colour.red(),
            )

            if member.avatar:
                em.set_thumbnail(url=member.avatar.url)
        else:
            return

        em.add_field(name="Report reason", value=interaction.text_values["reason"])

        await self.bot.utils_class.send_message_to_mods("", interaction.guild.id, em)

        await interaction.response.send_message(
            "ℹ️ - Your report has been successfully sent to the server's moderators!",
            ephemeral=True,
        )


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
