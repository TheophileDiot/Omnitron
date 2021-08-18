from discord.ext.commands import Context, Cog, command
from discord.permissions import Permissions

from bot import Omnitron
from data.utils import check_moderator


class Moderation(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="say",
        aliases=["acc", "announcement", "talk"],
        usage='#channel "message"',
        description="Send a message to a specified salon or the current one!",
    )
    @check_moderator()
    async def say_command(self, ctx: Context, *args: str):
        bot_member = await ctx.guild.fetch_member(self.bot.user.id)
        channel = ctx.channel
        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            if (
                not ctx.author.permissions_in(channel).view_channel
                or not ctx.author.permissions_in(channel).send_messages
            ):
                return await ctx.reply(
                    f"⛔ - You do not have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join([Permissions.view_channel, Permissions.send_messages])}`",
                    delete_after=20,
                )
            elif (
                not bot_member.permissions_in(channel).view_channel
                or not bot_member.permissions_in(channel).send_messages
            ):
                return await ctx.reply(
                    f"⛔ - I don't have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join([Permissions.view_channel, Permissions.send_messages])}`",
                    delete_after=20,
                )
            args = " ".join(args[1::])

        if bot_member.permissions_in(ctx.channel).manage_messages:
            await ctx.message.delete()
        await channel.send(" ".join(args))


def setup(bot):
    bot.add_cog(Moderation(bot))
