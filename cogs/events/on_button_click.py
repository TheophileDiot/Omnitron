from disnake import (
    Forbidden,
    MessageInteraction,
    NotFound,
    PermissionOverwrite,
)
from disnake.ext.commands import Cog
from disnake.utils import find

from bot import Omnitron


class Events(Cog, name="events.on_button_click"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_button_click(self, interaction: MessageInteraction):
        await self.bot.wait_until_ready()

        if interaction.author.bot:
            return
        elif (
            "polls_channel" in self.bot.configs[interaction.guild.id]
            and interaction.channel.id
            == self.bot.configs[interaction.guild.id]["polls_channel"].id
            and "polls" in self.bot.configs[interaction.guild.id]
        ):
            if (
                interaction.message.id
                not in self.bot.configs[interaction.guild.id]["polls"]
            ):
                return

            responses = self.bot.poll_repo.get_responses(
                interaction.guild.id, interaction.message.id
            )

            if str(interaction.author.id) in responses:
                return await interaction.send(
                    content=f"You have already answered this poll! Your answer: `{responses[str(interaction.author.id)]['response']}`",
                    ephemeral=True,
                )

            self.bot.poll_repo.create_response(
                interaction.guild.id,
                interaction.message.id,
                interaction.component.label,
                interaction.author.id,
            )
            new_embed = interaction.message.embeds[0]
            new_embed.to_dict()["fields"][0][
                "value"
            ] = f"`{str(int(new_embed.to_dict()['fields'][0]['value'][1:-1]) + 1)}`"
            await interaction.edit_original_message(embed=new_embed)
            await interaction.followup.send(
                content=f"Your answer has been taken into account! Answer: `{interaction.component.label}`",
                ephemeral=True,
            )
        elif (
            "tickets" in self.bot.configs[interaction.guild.id]
            and interaction.channel.id
            == self.bot.configs[interaction.guild.id]["tickets"]["tickets_channel"].id
            and interaction.component.custom_id
            == f"{self.bot.configs[interaction.guild.id]['tickets']['tickets_channel'].id}.ticket_create"
        ):
            channel_name = f"ticket-channel-{interaction.author.name.lower()}"

            if channel_name in [
                channel.name for channel in set(interaction.guild.text_channels)
            ]:
                channel = find(
                    lambda c: c.name == channel_name, interaction.guild.text_channels
                )
                return await interaction.send(
                    content=f"You already have an existing ticket channel! {channel.mention if channel else ''}",
                    ephemeral=True,
                )

            overwrites = {}

            for m in set(self.bot.moderators[interaction.guild.id]):
                try:
                    overwrites[
                        interaction.guild.get_role(int(m))
                        or (
                            interaction.guild.get_member(int(m))
                            or await interaction.guild.fetch_member(int(m))
                        )
                    ] = PermissionOverwrite(
                        **{
                            "view_channel": True,
                            "read_messages": True,
                            "send_messages": True,
                            "manage_messages": True,
                        }
                    )
                except NotFound:
                    pass

            overwrites[self.bot.user] = PermissionOverwrite(
                **{
                    "view_channel": True,
                    "read_messages": True,
                    "send_messages": True,
                    "manage_messages": True,
                }
            )
            overwrites[interaction.author] = PermissionOverwrite(
                **{"view_channel": True, "read_messages": True, "send_messages": True}
            )
            overwrites[interaction.guild.default_role] = PermissionOverwrite(
                **{"view_channel": False}
            )

            try:
                channel = await self.bot.configs[interaction.guild.id]["tickets"][
                    "tickets_category"
                ].create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    reason=f"Creation of the ticket channel of {interaction.author}",
                )
            except Forbidden as f:
                await interaction.send(
                    content=f"⚠️ - Your ticket channel couldn't be created because i'm missing permissions! Moderators have been informed about this!",
                    ephemeral=True,
                )
                f.text = f"⚠️ - I don't have the right permissions to create channels in the category {self.bot.configs[interaction.guild.id]['tickets']['tickets_category'].mention} (I tried to create a ticket channel for the member {interaction.author})!"
                raise

            self.bot.ticket_repo.create_ticket(
                interaction.guild.id, channel.id, interaction.author.id
            )
            await channel.send(
                f"ℹ️ - {interaction.author.mention} - Here goes your ticket channel, feel free to ask questions or just talk to the server's moderators privately!"
            )
            await interaction.send(
                content=f"Your ticket channel {channel.mention} has been successfully created!",
                ephemeral=True,
            )
        else:
            tickets = self.bot.ticket_repo.get_tickets(interaction.guild.id)
            if tickets and str(interaction.channel.id) in [
                ticket for ticket in tickets
            ]:
                if not self.bot.utils_class.is_mod(interaction.author, self.bot):
                    return await interaction.send(
                        content=f"You cannot interact with this message because you are not a moderator of this server!",
                        ephemeral=True,
                    )
                delete_pending = tickets[str(interaction.channel.id)][
                    "deletion_pending"
                ]
                if interaction.author.id != delete_pending["author"]:
                    return await interaction.send(
                        content=f"📥 - You are not the user who started the deletion procedure for this ticket, so you cannot interact with this message!",
                        ephemeral=True,
                    )

                if (
                    interaction.component.custom_id
                    == f"{interaction.channel.id}_confirm_ticket"
                ):
                    self.bot.ticket_repo.delete_ticket(
                        interaction.guild.id, interaction.channel.id
                    )

                    try:
                        await interaction.channel.delete()
                    except Forbidden as f:
                        f.text = f"⚠️ - I don't have the right permissions to delete channels in the category {self.bot.configs[interaction.guild.id]['tickets']['tickets_category'].mention} (I tried to delete the ticket channel {interaction.channel.mention})!"
                        raise
                else:
                    await interaction.send(
                        content=f"📥 - Cancellation of the ticket deletion!",
                        ephemeral=True,
                    )
                    self.bot.ticket_repo.cancel_deletion(
                        interaction.guild.id, interaction.channel.id
                    )
                    await interaction.message.delete()


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
