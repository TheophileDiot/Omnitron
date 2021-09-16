from discord.ext.commands import bot_has_permissions, Context, Cog, command
from discord.permissions import Permissions

from bot import Omnitron
from data import Utils


class Moderation(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="say",
        aliases=["acc", "announcement", "talk"],
        usage='(#channel) "message"',
        description="Send a message to a specified salon or the current one!",
    )
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def say_command(self, ctx: Context, *, args: str):
        channel = ctx.channel
        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            args = " ".join(args.split(" ")[1::])
            if (
                not ctx.guild.me.permissions_in(channel).view_channel
                or not channel.can_send
            ):
                return await ctx.reply(
                    f"⛔ - I don't have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join([Permissions.view_channel, Permissions.send_messages])}`",
                    delete_after=20,
                )

        if ctx.guild.me.permissions_in(ctx.channel).manage_messages:
            await ctx.message.delete()

        await channel.send(args)


def setup(bot):
    bot.add_cog(Moderation(bot))
