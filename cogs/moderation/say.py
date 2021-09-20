from disnake import TextChannel
from disnake.ext.commands import bot_has_permissions, Context, Cog, command
from disnake.permissions import Permissions

from bot import Omnitron
from data import Utils


class Moderation(Cog, name="moderation.say"):
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
        channel: TextChannel = ctx.channel

        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            args = " ".join(args.split(" ")[1::])
            perms = channel.permissions_for(ctx.guild.me)

            if perms.view_channel or not perms.send_messages:
                return await ctx.reply(
                    f"⛔ - I don't have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join([Permissions.view_channel, Permissions.send_messages])}`",
                    delete_after=20,
                )

        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()

        await channel.send(args)


def setup(bot):
    bot.add_cog(Moderation(bot))
