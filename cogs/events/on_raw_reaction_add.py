from discord import Forbidden, RawReactionActionEvent
from discord.ext.commands import Cog

from bot import Omnitron
from data import Utils, Xp_class


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.xp_class = Xp_class(bot)

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
            try:
                if payload.emoji.name == "✅":
                    await self.xp_class.manage_prestige(
                        payload.member, "added_prestige"
                    )

                    try:
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
                                    if "lvl2role"
                                    in self.bot.configs[payload.guild_id]["xp"]
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
                    except Forbidden:
                        roles = ", ".join(
                            [
                                f"`@{role}`"
                                for role in payload.member.roles
                                if role
                                in (
                                    set(
                                        self.bot.configs[payload.guild_id]["xp"][
                                            "lvl2role"
                                        ].values()
                                    )
                                    if "lvl2role"
                                    in self.bot.configs[payload.guild_id]["xp"]
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
                        await self.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to remove the roles {roles} from the member `{payload.member}`!",
                            payload.guild_id,
                        )

                        try:
                            return await payload.member.send(
                                f"⚠️ - I don't have the right permissions to remove the roles {roles} from you so you can't pass the prestige! Please inform a server administrator! (Guild: {await self.bot.fetch_guild(payload.guild_id).name}, ID: {payload.guild_id})"
                            )
                        except Forbidden:
                            try:
                                channel = await self.bot.fetch_channel(
                                    payload.channel_id
                                )
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to fetch the channel under the ID {payload.channel_id}!"
                                raise

                            try:
                                return await channel.send(
                                    f"⚠️ - {payload.member.mention} - I don't have the right permissions to remove the roles {roles} from you so you can't pass the prestige! Please inform a server administrator!"
                                )
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {channel.mention} (message: `⚠️ - {payload.member.mention} - I don't have the right permissions to remove the roles {roles} from you so you can't pass the prestige! Please inform a server administrator!`)!"
                                raise

                    try:
                        await payload.member.add_roles(
                            self.bot.configs[payload.guild_id]["xp"]["prestiges"][
                                (int(db_user["prestige"]) + 1) or 1
                            ]
                        )
                    except Forbidden:
                        await self.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to the member `{payload.member}`!",
                            payload.guild_id,
                        )

                        try:
                            return await payload.member.send(
                                f"⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to you so you can't pass the prestige! Please inform a server administrator! (Guild: {await self.bot.fetch_guild(payload.guild_id).name}, ID: {payload.guild_id})"
                            )
                        except Forbidden:
                            channel = await self.bot.fetch_channel(payload.channel_id)

                            try:
                                return await channel.send(
                                    f"⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to you so you can't pass the prestige! Please inform a server administrator!"
                                )
                            except Forbidden as f:
                                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {channel.mention} (message: `⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to you so you can't pass the prestige! Please inform a server administrator!`)!"
                                raise

                    if "notify_channel" in self.bot.configs[payload.guild_id]["xp"]:
                        try:
                            return await self.bot.configs[payload.guild_id]["xp"][
                                "notify_channel"
                            ].send(
                                f"🎉 - {payload.member.mention} - You have just switched to prestige `{(int(db_user['prestige']) + 1) or 1}` - `{(self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]).name}` ! - 🎉"
                            )
                        except Forbidden as f:
                            f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[payload.guild_id]['xp']['notify_channel'].mention} (message: `🎉 - {payload.member.mention} - You have just switched to prestige `{(int(db_user['prestige']) + 1) or 1}` - `{(self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]).name}` ! - 🎉`)!"
                            raise

                elif payload.emoji.name == "❌":
                    pass
                else:
                    return

                self.bot.user_repo.cancel_prestige(payload.guild_id, payload.user_id)
            except Forbidden:
                raise
            finally:
                message = await (
                    await self.bot.fetch_channel(payload.channel_id)
                ).fetch_message(payload.message_id)
                await message.remove_reaction("✅", self.bot.user)
                await message.remove_reaction("❌", self.bot.user)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
