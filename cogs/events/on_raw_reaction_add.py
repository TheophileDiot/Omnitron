from asyncio import sleep
from random import choice

from disnake import Forbidden, RawReactionActionEvent
from disnake.ext.commands import Cog

from bot import Omnitron
from cogs.misc.game import NUM2EMOJI, check_for_win_fourinarow
from data import Utils, Xp_class


class Events(Cog, name="events.on_raw_reaction_add"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.xp_class = Xp_class(bot)

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """When a reaction is added, if the channels is a game channel then handle it else if the user have a prestige pending then handle it according to the reaction added"""
        if payload.member.bot:
            return

        if (
            "games" in self.bot.configs[payload.guild_id]
            and self.bot.configs[payload.guild_id]["games"]
            and str(payload.channel_id) in self.bot.configs[payload.guild_id]["games"]
        ):
            reaction = payload.emoji
            channel = self.bot.get_channel(
                payload.channel_id
            ) or await self.bot.fetch_channel(payload.channel_id)
            if channel.name.startswith("4inarow-"):
                message = await channel.fetch_message(payload.message_id)
                if payload.member not in message.mentions:
                    await message.remove_reaction(reaction, payload.member)
                    return await channel.send(
                        f"⛔ - {payload.member.mention} - Only four in a row participants can play",
                        delete_after=10,
                    )

                if reaction.name == "🔄":
                    await message.clear_reactions()
                    board = [
                        ["⬛" if x == 0 or x == 8 or y == 7 else "⚪" for x in range(9)]
                        for y in range(8)
                    ]
                    nl = "\n"
                    await message.edit(
                        content=f"🔴🔴🔴🔴 - {message.mentions[0].mention} **VS** {message.mentions[1].mention} - 🔵🔵🔵🔵\n\n**This is `{choice([message.mentions[0], message.mentions[1]]).name}`'s turn**\n\n{nl.join([''.join(row) for row in board])}"
                    )
                    for x in range(1, 8):
                        await message.add_reaction(NUM2EMOJI[x])
                    await message.add_reaction("🔄")
                    return

                if reaction.name == "💥":
                    await channel.send(
                        "⚠️ - **Deletion of the channel in **`5`** seconds** - ⚠️"
                    )
                    await sleep(5)
                    del self.bot.configs[payload.guild_id]["games"][payload.channel_id]
                    self.bot.games_repo.remove_game(
                        payload.guild_id, payload.channel_id
                    )
                    await channel.delete()
                    return

                content = message.clean_content

                player_turn = content[content.find("`") + 1 : content.rfind("`")]

                if payload.member.name != player_turn:
                    await message.remove_reaction(reaction, payload.member)
                    return await channel.send(
                        f"⛔ - {payload.member.mention} - It's not your turn",
                        delete_after=5,
                    )

                board = [[emoji for emoji in row] for row in content.split("\n")[4:]]
                row = int(
                    list(NUM2EMOJI.keys())[
                        list(NUM2EMOJI.values()).index(reaction.name)
                    ]
                )

                x = 6
                while board[x][row] != "⚪":
                    x -= 1

                if x == 0:
                    await message.clear_reaction(reaction)
                else:
                    await message.remove_reaction(reaction, payload.member)

                board[x][row] = (
                    "🔴" if payload.member.name == message.mentions[0].name else "🔵"
                )
                nl = "\n"

                if check_for_win_fourinarow(board):
                    await message.clear_reactions()
                    await message.edit(
                        content=f"🔴🔴🔴🔴 - {message.mentions[0].mention} **VS** {message.mentions[1].mention} - 🔵🔵🔵🔵\n\n**THE WINNER IS:** `{player_turn}`!\n\n{nl.join([''.join(row) for row in board])}"
                    )
                    await message.add_reaction("💥")
                    return await message.add_reaction("🔄")

                await message.edit(
                    content=f"🔴🔴🔴🔴 - {message.mentions[0].mention} **VS** {message.mentions[1].mention} - 🔵🔵🔵🔵\n\n**It's `{message.mentions[0 if player_turn == message.mentions[1].name else 1].name}`'s turn**\n\n{nl.join([''.join(row) for row in board])}"
                )

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
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to remove the roles {roles} from the member `{payload.member}`!",
                            payload.guild_id,
                        )

                        try:
                            return await payload.member.send(
                                f"⚠️ - I don't have the right permissions to remove the roles {roles} from you so you can't pass the prestige! Please inform a server administrator! (Guild: {(self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id)).name}, ID: {payload.guild_id})"
                            )
                        except Forbidden:
                            try:
                                channel = self.bot.get_channel(
                                    payload.channel_id
                                ) or await self.bot.fetch_channel(payload.channel_id)
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
                        await self.bot.utils_class.send_message_to_mods(
                            f"⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to the member `{payload.member}`!",
                            payload.guild_id,
                        )

                        try:
                            return await payload.member.send(
                                f"⚠️ - I don't have the right permissions to add the role {self.bot.configs[payload.guild_id]['xp']['prestiges'][(int(db_user['prestige']) + 1) or 1]} to you so you can't pass the prestige! Please inform a server administrator! (Guild: {(self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id)).name}, ID: {payload.guild_id})"
                            )
                        except Forbidden:
                            channel = self.bot.get_channel(
                                payload.channel_id
                            ) or await self.bot.fetch_channel(payload.channel_id)

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
                    self.bot.get_channel(payload.channel_id)
                    or await self.bot.fetch_channel(payload.channel_id)
                ).fetch_message(payload.message_id)
                await message.remove_reaction("✅", self.bot.user)
                await message.remove_reaction("❌", self.bot.user)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
