from disnake import MessageInteraction
from disnake.ext.commands import Cog

from bot import Omnitron


class Events(Cog, name="events.on_dropdown"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_dropdown(self, interaction: MessageInteraction):
        if (
            interaction.channel.id
            != self.bot.configs[interaction.guild.id]["select2role"]["channel"].id
        ):
            return

        roles = [
            role
            for role in self.bot.configs[interaction.guild.id]["select2role"][
                "selects"
            ].values()
        ]
        member_roles = [role for role in interaction.author.roles if role in roles]
        if interaction.values:
            chosen_roles = [
                self.bot.configs[interaction.guild.id]["select2role"]["selects"][s][
                    "role"
                ]
                for s in interaction.values
            ]
        else:
            chosen_roles = []
        added_roles = [role for role in chosen_roles if role not in member_roles]
        removed_roles = [role for role in member_roles if role not in chosen_roles]

        response = ""

        if removed_roles:
            response = f"The role{'s' if len(removed_roles) > 1 else ''} {', '.join([f'`{role.name}`' for role in removed_roles])} has been successfully removed from you!"
            await interaction.author.remove_roles(
                *removed_roles,
                reason=f"Deselected {'these roles' if len(removed_roles) > 1 else 'this role'} in the roles channel",
            )

        if added_roles:
            if response == "":
                response = f"The role{'s' if len(added_roles) > 1 else ''} {', '.join([f'`{role.name}`' for role in added_roles])} has been successfully assigned to you!"
            else:
                response += f"\nAnd the role{'s' if len(added_roles) > 1 else ''} {', '.join([f'`{role.name}`' for role in added_roles])} has been successfully assigned to you!"
            await interaction.author.add_roles(
                *added_roles,
                reason=f"Selected {'these roles' if len(added_roles) > 1 else 'this role'} in the role channel",
            )

        if response:
            await interaction.response.send_message(
                content=response,
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                content="The roles have been updated correctly!",
                ephemeral=True,
            )


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
