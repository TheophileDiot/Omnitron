from asyncio import sleep

from disnake import RawMessageDeleteEvent
from disnake.ext.commands import Cog

from bot import Omnitron


class Events(Cog, name="events.on_raw_message_delete"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        await sleep(1.5)

        if (
            "tickets" in self.bot.configs[payload.guild_id]
            and "tickets_channel" in self.bot.configs[payload.guild_id]["tickets"]
            and self.bot.configs[payload.guild_id]["tickets"]["tickets_channel"].id
            == payload.channel_id
        ):
            if not [
                m
                for m in set(
                    await self.bot.configs[payload.guild_id]["tickets"][
                        "tickets_channel"
                    ]
                    .history(limit=10)
                    .flatten()
                )
                if m.author.id == self.bot.user.id
            ]:
                await self.bot.utils_class.send_message_to_mods(
                    f"⚠️ - Someone just deleted the ticket message (please use the command `{self.bot.utils_class.get_guild_pre(payload.guild_id)[0]}tickets resolve` to resolve it)!",
                    payload.guild_id,
                )
        elif (
            "select2role" in self.bot.configs[payload.guild_id]
            and "roles_msg_id" in self.bot.configs[payload.guild_id]["select2role"]
            and self.bot.configs[payload.guild_id]["select2role"]["roles_msg_id"]
            == payload.message_id
        ):
            del self.bot.configs[payload.guild_id]["select2role"]["roles_msg_id"]
            await self.bot.utils_class.send_message_to_mods(
                f"⚠️ - Someone just deleted the select2role message (please use the command `{self.bot.utils_class.get_guild_pre(payload.guild_id)[0]}cfg select2role resolve` to resolve it)!",
                payload.guild_id,
            )
        elif (
            "polls" in self.bot.configs[payload.guild_id]
            and payload.message_id in self.bot.configs[payload.guild_id]["polls"]
        ):
            self.bot.configs[payload.guild_id]["polls"][payload.message_id].cancel()
            del self.bot.configs[payload.guild_id]["polls"][payload.message_id]
            self.bot.poll_repo.erase_poll(payload.guild_id, payload.message_id)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
