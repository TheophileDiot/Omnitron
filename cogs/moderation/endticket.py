from typing import Union

from disnake import ApplicationCommandInteraction, ButtonStyle
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    bot_has_guild_permissions,
    max_concurrency,
    slash_command,
)
from disnake.ui import Button, View

from bot import Omnitron
from data import Utils


class Moderation(Cog, name="moderation.endticket"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="endticket",
        aliases=["et"],
        description="Create a procedure to delete a ticket. (can only be used in a ticket channel)",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_guild_permissions(manage_channels=True)
    @bot_has_permissions(send_messages=True)
    @max_concurrency(1, BucketType.channel)
    async def endticket_command(self, ctx: Context):
        await self.handle_endticket(ctx)

    @slash_command(
        name="endticket",
        aliases=["et"],
        description="Create a procedure to delete a ticket. (can only be used in a ticket channel)",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_guild_permissions(manage_channels=True)
    @max_concurrency(1, BucketType.channel)
    async def endticket_slash_command(self, ctx: Context):
        await self.handle_endticket(ctx)

    """ METHOD(S) """

    async def handle_endticket(
        self, source: Union[Context, ApplicationCommandInteraction]
    ):
        tickets = self.bot.ticket_repo.get_tickets(source.guild.id)

        if not tickets or str(source.channel.id) not in [ticket for ticket in tickets]:
            if isinstance(source, Context):
                return await source.reply(
                    f"⛔ - {source.author.mention} - You cannot use this command outside a ticket channel! `{self.bot.utils_class.get_guild_pre(source.message)[0]}{source.command.qualified_name}` to get more help!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⛔ - {source.author.mention} - You cannot use this command outside a ticket channel!",
                    ephemeral=True,
                )

        ticket = tickets[str(source.channel.id)]

        if "deletion_pending" in ticket:
            if isinstance(source, Context):
                return await source.reply(
                    f"⛔ - {source.author.mention} - You cannot create two ticket deletion procedures simultaneously!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⛔ - {source.author.mention} - You cannot create two ticket deletion procedures simultaneously!",
                    ephemeral=True,
                )

        self.bot.ticket_repo.prepare_deletion(
            source.guild.id, source.channel.id, source.author.id
        )
        nl = "\n"
        view = View(timeout=None)
        view.add_item(
            Button(
                style=ButtonStyle.success,
                label="yes",
                custom_id=f"{source.channel.id}_confirm_ticket",
            )
        )
        view.add_item(
            Button(
                style=ButtonStyle.danger,
                label="no",
                custom_id=f"{source.channel.id}_cancel_ticket",
            )
        )

        if isinstance(source, Context):
            await source.send(
                content=f"**📤 - {source.author.mention} - Confirmation of ticket deletion!**{nl}{nl}Do you wish to terminate this ticket?",
                view=view,
            )
        else:
            await source.response.send_message(
                content=f"**📤 - {source.author.mention} - Confirmation of ticket deletion!**{nl}{nl}Do you wish to terminate this ticket?",
                view=view,
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
