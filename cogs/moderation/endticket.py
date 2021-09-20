from disnake import ButtonStyle
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    bot_has_guild_permissions,
    max_concurrency,
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
        tickets = self.bot.ticket_repo.get_tickets(ctx.guild.id)
        if not tickets or str(ctx.channel.id) not in [ticket for ticket in tickets]:
            return await ctx.reply(
                f"⛔ - {ctx.author.mention} - You cannot use this command outside a ticket channel! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}{ctx.command.qualified_name}` to get more help!",
                delete_after=20,
            )
        ticket = tickets[str(ctx.channel.id)]
        if "deletion_pending" in ticket:
            return await ctx.reply(
                f"⛔ - {ctx.author.mention} - You cannot create two ticket deletion procedures simultaneously!",
                delete_after=20,
            )
        self.bot.ticket_repo.prepare_deletion(
            ctx.guild.id, ctx.channel.id, ctx.author.id
        )
        nl = "\n"
        view = View(timeout=None)
        view.add_item(
            Button(
                style=ButtonStyle.success,
                label="yes",
                custom_id=f"{ctx.channel.id}_confirm_ticket",
            )
        )
        view.add_item(
            Button(
                style=ButtonStyle.danger,
                label="no",
                custom_id=f"{ctx.channel.id}_cancel_ticket",
            )
        )

        await ctx.send(
            content=f"**📤 - {ctx.author.mention} - Confirmation of ticket deletion!**{nl}{nl}Do you wish to terminate this ticket?",
            view=view,
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
