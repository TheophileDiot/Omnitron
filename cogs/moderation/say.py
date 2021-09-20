from typing import Union

from disnake import ApplicationCommandInteraction, TextChannel, Option, OptionType
from disnake.ext.commands import (
    bot_has_permissions,
    Context,
    Cog,
    command,
    slash_command,
)

from bot import Omnitron
from data import Utils


async def handle_say(
    source: Union[Context, ApplicationCommandInteraction],
    channel: TextChannel,
    message: str,
):
    perms = channel.permissions_for(source.guild.me)

    if not perms.view_channel or not perms.send_messages:
        if isinstance(source, Context):
            return await source.reply(
                f"⛔ - I don't have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join(['VIEW_CHANNEL', 'SEND_MESSAGES'])}`",
                delete_after=20,
            )
        else:
            return await source.response.send_message(
                f"⛔ - I don't have the necessary perms to send a message in this channel ({channel})! Required perms: `{', '.join(['VIEW_CHANNEL', 'SEND_MESSAGES'])}`",
                ephemeral=True,
            )

    if (
        isinstance(source, Context)
        and source.channel.permissions_for(source.guild.me).manage_messages
    ):
        await source.message.delete()

    await channel.send(message)


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

        await handle_say(ctx, channel, args)

    @slash_command(
        name="say",
        aliases=["acc", "announcement", "talk"],
        description="Send a message to a specified salon or the current one!",
        options=[
            Option(
                name="message",
                description="Enter the message you want to send through the bot",
                type=OptionType.string,
                required=True,
            ),
            Option(
                name="channel",
                description="Enter the channel you want to send the message in",
                type=OptionType.channel,
                required=False,
            ),
        ],
    )
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def say_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        message: str,
        channel: TextChannel = None,
    ):
        if not channel:
            channel = inter.channel
        elif not isinstance(channel, TextChannel):
            return await inter.response.send_message(
                "The channel precised must be a valid TextChannel!", ephemeral=True
            )

        await handle_say(inter, channel, message)

    """ METHOD(S) """


def setup(bot):
    bot.add_cog(Moderation(bot))
