from disnake import RawMessageUpdateEvent
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_raw_message_edit"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        """When a message is edited, if the prevent_invites option is on check if there is an invitation link to another discord server in the message"""
        if "prevent_invites" in self.bot.configs[payload.guild_id]:
            if not payload.guild_id:
                return

            channel = self.bot.get_channel(
                payload.channel_id
            ) or await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if message.is_system() or message.author.bot:
                return

            ctx = await self.bot.get_context(message=message)
            await self.bot.utils_class.check_invite(ctx)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
