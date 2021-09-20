from disnake import Forbidden, Role, Member
from math import floor, ceil
from random import randint

from bot import Omnitron


class Xp_class:
    def __init__(self, bot: Omnitron) -> None:
        self.bot = bot

    """ METHODS """

    async def new_level_role(self, member: Member, new_role: Role, _type: str):
        try:
            await member.remove_roles(
                *[
                    role
                    for role in member.roles
                    if role
                    in self.bot.configs[member.guild.id]["xp"]["lvl2role"].values()
                ]
            )
            await member.add_roles(new_role)
        except Forbidden:
            try:
                await member.send(
                    f"⛔ - I do not have the rights to add or remove roles for members! Moderators have been informed about this!"
                )
            except Forbidden:
                pass

            await self.bot.utils_class.send_message_to_mods(
                f"⚠️ - I don't have the right permissions to manage these roles {', '.join([f'`@{role.name}`' for role in [role for role in member.roles if role in self.bot.configs[member.guild.id]['xp']['lvl2role'].values()] + [new_role]])} (i tried to remove the level roles from {member})!",
                member.guild.id,
            )

        if "notify_channel" in self.bot.configs[member.guild.id]["xp"]:
            msg = f"⚠️ - Message not defined for the event {_type} ! - ⚠️"

            try:
                if _type == "new_lvl":
                    msg = f"🎉 - {member.mention} - You have just passed a rank and have now the `@{new_role.name}` role! - 🎉"
                elif _type == "set_lvl":
                    msg = f"🎉 - {member.mention} - Your level has changed and since you have the required level you have now the `@{new_role.name}` role! - 🎉"
                elif _type == "new_r_2_l":
                    msg = f"🎉 - {member.mention} - A new level to role has juste been created and since you have the required level you have now the `@{new_role.name}` role! - 🎉"

                await self.bot.configs[member.guild.id]["xp"]["notify_channel"].send(
                    msg
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[member.guild.id]['xp'].mention} (message: `{msg}`)!"
                raise

    async def manage_levels(self, member: Member, level: int, _type: str = ""):
        if "lvl2role" in self.bot.configs[member.guild.id]["xp"]:
            for key in sorted(
                self.bot.configs[member.guild.id]["xp"]["lvl2role"], reverse=True
            ):
                if level >= key:
                    if self.bot.configs[member.guild.id]["xp"]["lvl2role"][
                        key
                    ] not in set(member.roles):
                        await self.new_level_role(
                            member,
                            self.bot.configs[member.guild.id]["xp"]["lvl2role"][key],
                            _type,
                        )
                    break

    def calculate_bonus(self, member: Member, value: int):
        member_roles = set([str(r.id) for r in member.roles])
        for _id in self.bot.configs[member.guild.id]["xp"]["boosteds"]:
            if str(member.id) == _id or _id in member_roles:
                value = floor(
                    value
                    * (
                        1
                        + self.bot.configs[member.guild.id]["xp"]["boosteds"][_id] / 100
                    )
                )
        return value

    async def manage_xp(self, member: Member, _type: str):
        if (
            member.voice
            and len([_ for _ in member.voice.channel.members if not _.bot]) < 2
        ):
            return

        db_user = self.bot.user_repo.get_user(member.guild.id, member.id)

        if _type == "vocal":
            xp_gain = floor(randint(15, 25))
            if member.voice.self_deaf:
                xp_gain = ceil(xp_gain * 0.25)
        else:
            xp_gain = floor(randint(10, 15))

        xp_gain = floor(
            xp_gain
            * (
                1
                + ((db_user["prestige"] if "prestige" in db_user else 0) * 10)
                / int(self.bot.configs[member.guild.id]["xp"]["max_lvl"])
            )
        )

        if self.have_xp_bonus(member):
            xp_gain = self.calculate_bonus(member, xp_gain)

        if (db_user["xp"] + xp_gain) < 5 * (db_user["level"] ^ 2) + 50 * db_user[
            "level"
        ] + 100 or db_user["level"] == int(
            self.bot.configs[member.guild.id]["xp"]["max_lvl"]
        ):
            self.bot.user_repo.add_xp(member.guild.id, member.id, xp_gain)
        else:
            self.bot.user_repo.clear_xp(member.guild.id, member.id)
            self.bot.user_repo.add_levels(member.guild.id, member.id, 1)

            if "notify_channel" in self.bot.configs[member.guild.id]["xp"]:
                msg = f"⚠️ - Message not defined for the event {_type} ! - ⚠️"

                try:
                    if db_user["level"] + 1 == int(
                        self.bot.configs[member.guild.id]["xp"]["max_lvl"]
                    ):
                        msg = f"🎉 - {member.mention} - You've just reached level `int({self.bot.configs[member.guild.id]['xp']['max_lvl']})`, you have reached the maximum level! You can now pass a prestige with the command `{self.bot.utils_class.get_guild_pre(member)[0]}prestige`! - 🎉"
                    else:
                        msg = f"🎉 - {member.mention} - You've just passed to the level `{db_user['level'] + 1}`! - 🎉"
                except Forbidden as f:
                    f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {self.bot.configs[member.guild.id]['xp'].mention} (message: `{msg}`)!"
                    raise

            await self.manage_levels(member, db_user["level"] + 1, "new_lvl")

    async def manage_prestige(self, member: Member, _type: str):
        db_user = self.bot.user_repo.get_user(member.guild.id, member.id)

        xp = db_user["xp"]
        if _type == "removed_prestige":
            for lvl in range(1, int(db_user["level"])):
                xp += 5 * (lvl ^ 2) + 50 * lvl + 100

            self.bot.user_repo.remove_prestige(member.guild.id, member.id, xp)
        elif _type == "added_prestige":
            level = 1
            for lvl in range(1, int(db_user["level"])):
                xp -= 5 * (lvl ^ 2) + 50 * lvl + 100

                if xp < 0:
                    break
                elif level < self.bot.configs[member.guild.id]["xp"]["max_lvl"]:
                    level += 1

            self.bot.user_repo.add_prestige(
                member.guild.id,
                member.id,
                1,
                level,
                xp + (5 * (lvl ^ 2) + 50 * lvl + 100),
            )
        elif _type == "purged_prestiges":
            for prestige in range(0, int(db_user["prestige"])):
                for lvl in range(
                    1,
                    self.bot.configs[member.guild.id]["xp"]["max_lvl"]
                    if prestige >= 1
                    else int(db_user["level"]),
                ):
                    xp += 5 * (lvl ^ 2) + 50 * lvl + 100

            self.bot.user_repo.remove_prestige(
                member.guild.id, member.id, xp, db_user["prestige"]
            )

        await self.manage_levels(
            member,
            self.bot.user_repo.get_user(member.guild.id, member.id)["level"],
            "set_lvl",
        )

    def have_xp_bonus(self, member: Member) -> bool:
        if "boosteds" not in self.bot.configs[member.guild.id]["xp"]:
            return False

        return set([str(r.id) for r in member.roles]) & set(
            self.bot.configs[member.guild.id]["xp"]["boosteds"]
        ) or str(member.id) in set(self.bot.configs[member.guild.id]["xp"]["boosteds"])
