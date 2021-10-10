from disnake import Role
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_guild_role_delete"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_role_delete(self, role: Role):
        """When a guild role is deleted, if it corresponds to an assigned one to something then removes it from the database"""
        resp = None

        if (
            "muted_role" in self.bot.configs[role.guild.id]
            and self.bot.configs[role.guild.id]["muted_role"] == role
        ):
            self.bot.config_repo.set_muted_role(role.guild.id, None)
            del self.bot.configs[role.guild.id]["muted_role"]
            self.bot.config_repo.remove_mute_on_join(role.guild.id)
            del self.bot.configs[role.guild.id]["mute_on_join"]
            resp = f"⚠️ - Someone just deleted the muted role, therefore the mute_on_join feature has been deactivated (please set a new muted_role and use the command `{self.bot.utils_class.get_guild_pre(role.guild.id)[0]}config security mute_on_join on` to resolve it)!"
        elif role.id in set(self.bot.moderators[role.guild.id]):
            self.bot.config_repo.remove_moderator(role.guild.id, role.id)
            del self.bot.moderators[role.guild.id][
                self.bot.moderators[role.guild.id].index(role.id)
            ]
            resp = f"⚠️ - Someone just deleted a moderator role, therefore the role has been deleted from the list!"
        elif role.id in set(self.bot.djs[role.guild.id]):
            self.bot.config_repo.remove_dj(role.guild.id, role.id)
            del self.bot.djs[role.guild.id][self.bot.djs[role.guild.id].index(role.id)]
            resp = f"⚠️ - Someone just deleted a dj role, therefore the role has been deleted from the list!"
        elif "prestiges" in self.bot.configs[role.guild.id]["xp"] and role in set(
            self.bot.configs[role.guild.id]["xp"]["prestiges"].values()
        ):
            prestige = list(self.bot.configs[role.guild.id]["xp"]["prestiges"].keys())[
                list(self.bot.configs[role.guild.id]["xp"]["prestiges"].values()).index(
                    role
                )
            ]
            self.bot.config_repo.add_xp_prestiges(
                role.guild.id, f"p_{prestige}", "deleted_role", role.id
            )
            self.bot.configs[role.guild.id]["xp"]["prestiges"][prestige] = None
            resp = f"⚠️ - Someone just deleted a role corresponding to one of the existing prestiges (prestige: `{prestige}`), (please use the command `{self.bot.utils_class.get_guild_pre(role.guild.id)[0]}config xp prestiges update` to resolve it)!"
        elif "lvl2role" in self.bot.configs[role.guild.id]["xp"] and role in set(
            self.bot.configs[role.guild.id]["xp"]["lvl2role"].values()
        ):
            lvl = list(self.bot.configs[role.guild.id]["xp"]["lvl2role"].keys())[
                list(self.bot.configs[role.guild.id]["xp"]["lvl2role"].values()).index(
                    role
                )
            ]
            self.bot.config_repo.remove_xp_lvl2role(role.guild.id, lvl)
            del self.bot.configs[role.guild.id]["xp"]["lvl2role"][lvl]
            resp = f"⚠️ - Someone just deleted a role corresponding to one of the existing lvl to role (level: `{lvl}`), therefore the role has been deleted from the list!"
        elif (
            "select2role" in self.bot.configs[role.guild.id]
            and "selects" in self.bot.configs[role.guild.id]["select2role"]
            and role
            in {
                v["role"]
                for v in self.bot.configs[role.guild.id]["select2role"][
                    "selects"
                ].values()
            }
        ):
            title = None
            for v in self.bot.configs[role.guild.id]["select2role"]["selects"]:
                if (
                    self.bot.configs[role.guild.id]["select2role"]["selects"][v]["role"]
                    == role
                ):
                    title = v
                    break

            self.bot.config_repo.remove_select2role(role.guild.id, title)
            del self.bot.configs[role.guild.id]["select2role"]["selects"][title]
            resp = f"⚠️ - Someone just deleted a role corresponding to one of the existing select to role (select: `{title}`), therefore the role has been deleted from the list, (please use the command `{self.bot.utils_class.get_guild_pre(role.guild.id)[0]}select_to_role resolve` to resolve the feature)!!"

        if resp:
            await self.bot.utils_class.send_message_to_mods(
                resp + f"\nThe role was `{role.name}` (ID: `{role.id}`)",
                role.guild.id,
            )


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
