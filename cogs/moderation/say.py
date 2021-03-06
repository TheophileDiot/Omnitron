from typing import Union

from disnake import GuildCommandInteraction, TextChannel
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
    source: Union[Context, GuildCommandInteraction],
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

    if channel == source.channel and not isinstance(source, Context):
        await source.response.send_message(message)
    else:
        await channel.send(message)

        if channel != source.channel:
            if isinstance(source, Context):
                await source.send(
                    f"Your message has successfully been sent to the channel {channel.mention}"
                )
            else:
                await source.response.send_message(
                    f"Your message has successfully been sent to the channel {channel.mention}"
                )


class Moderation(Cog, name="moderation.say"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="say",
        aliases=["acc", "announcement", "talk"],
        usage='(#channel) "message"',
        description="Sends a message to a specified channel or the current one!",
    )
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def say_command(self, ctx: Context, *, args: str):
        """
        This command sends a message to a specified channel or the current one!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        args: :class:`str` optional
            The other options including a channel to send the message in if there is one and the message to send
        """
        channel: TextChannel = ctx.channel

        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
            args = " ".join(args.split(" ")[1::])

        await handle_say(ctx, channel, args)

    @slash_command(
        name="say",
        description="Send a message to a specified salon or the current one!",
    )
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def say_slash_command(
        self,
        inter: GuildCommandInteraction,
        message: str,
        channel: TextChannel = None,
    ):
        """
        This slash command sends a message to a specified channel or the current one!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.GuildCommandInteraction`
            The application command interaction
        message: :class:`str`
            The message to send
        channel: :class:`disnake.TextChannel` optional
            the text channel to send the message in
        """
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
