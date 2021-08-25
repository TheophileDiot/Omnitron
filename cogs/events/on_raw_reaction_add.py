from discord import RawReactionActionEvent
from discord.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """When a reaction is added, if the user have a prestige pending then handle it according to the reaction added"""
        if payload.member.bot:
            return

        db_user = self.bot.user_repo.get_user(payload.guild_id, payload.user_id)

        if (
            "prestige_pending" in db_user
            and payload.message_id == db_user["prestige_pending"]["confirmation_id"]
        ):
            if payload.emoji.name == "✅":
                await self.xp_class.manage_prestige(payload.member, "added_prestige")
                await payload.member.remove_roles(
                    *[
                        role
                        for role in payload.member.roles
                        if role
                        in (
                            set(
                                self.bot.configs[payload.guild_id]["xp"][
                                    "lvl2role"
                                ].values()
                            )
                            if "lvl2role" in self.bot.configs[payload.guild_id]["xp"]
                            else []
                        )
                        or role
                        in set(
                            self.bot.configs[payload.guild_id]["xp"][
                                "prestiges"
                            ].values()
                        )
                    ]
                )
                await payload.member.add_roles(
                    self.bot.configs[payload.guild_id]["xp"]["prestiges"][
                        (int(db_user["prestige"]) + 1) or 1
                    ]
                )
                self.bot.user_repo.cancel_prestige(payload.guild_id, payload.user_id)

                if "notify_channel" in self.bot.configs[payload.guild_id]["xp"]:
                    await self.bot.configs[payload.guild_id]["xp"][
                        "notify_channel"
                    ].send(
                        f"🎉 - {payload.member.mention} - You have just switched to prestige `{(int(db_user['prestige']) + 1) or 1}` - `{(self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]).name}` ! - 🎉"
                    )
            elif payload.emoji.name == "❌":
                self.bot.user_repo.cancel_prestige(payload.guild_id, payload.user_id)
            else:
                return
            message = await (
                await self.bot.fetch_channel(payload.channel_id)
            ).fetch_message(payload.message_id)
            await message.remove_reaction("✅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
