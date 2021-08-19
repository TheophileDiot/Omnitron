from collections import OrderedDict
from discord.ext.commands import Cog

from bot import Omnitron


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        """Check on start if any guilds that the bot is in are not in the DB else initialise moderators list for every guild in the DB"""
        db_guilds = set([int(k) for k in self.bot.main_repo.get_guilds().keys()])
        guilds = set(self.bot.guilds)
        for guild in guilds:
            if guild.id not in db_guilds:
                self.bot.main_repo.create_guild(
                    guild.id, guild.name, f"{guild.owner}"
                )  # If guild is not in DB, create it

            db_users = set(self.bot.user_repo.get_users(guild.id).keys())
            members = set(
                [m for m in guild.members if not m.bot and str(m.id) not in db_users]
            )
            for member in members:
                self.bot.user_repo.create_user(guild.id, member.id, f"{member}")

            self.bot.moderators[guild.id] = list(
                [int(k) for k in self.bot.config_repo.get_moderators(guild.id).keys()]
            )  # Initialize moderators list for every guilds
            self.bot.configs[guild.id] = {
                "prefix": self.bot.config_repo.get_prefix(guild.id)
            }

            xp = self.bot.config_repo.get_xp(guild.id)
            self.bot.configs[guild.id]["xp"] = dict(xp)

            if "boosteds" in xp:
                self.bot.configs[guild.id]["xp"]["boosteds"] = {
                    key: int(value["bonus"]) for key, value in xp["boosteds"].items()
                }

            if "lvl2role" in xp:
                self.bot.configs[guild.id]["xp"]["lvl2role"] = {
                    int(key): guild.get_role(value["role_id"])
                    for key, value in xp["lvl2role"].items()
                }

            if "prestiges" in xp:
                self.bot.configs[guild.id]["xp"]["prestiges"] = {
                    int(key[2]): guild.get_role(value["role_id"])
                    for key, value in xp["prestiges"].items()
                }

            if "notify_channel" in xp:
                self.bot.configs[guild.id]["xp"]["notify_channel"] = guild.get_channel(
                    xp["notify_channel"]
                )

            mute_on_join = self.bot.config_repo.get_mute_on_join(guild.id)
            if mute_on_join:
                self.bot.configs[guild.id]["mute_on_join"] = {
                    "duration": mute_on_join["duration"],
                    "muted_role": guild.get_role(int(mute_on_join["muted_role_id"])),
                }
                if "notify_channel_id" in mute_on_join:
                    self.bot.configs[guild.id]["mute_on_join"][
                        "notify_channel"
                    ] = guild.get_channel(int(mute_on_join["notify_channel_id"]))

            prevent_invites = self.bot.config_repo.get_invit_prevention(guild.id)
            self.bot.configs[guild.id]["prevent_invites"] = (
                {
                    "notify_channel": guild.get_channel(
                        int(prevent_invites["notify_channel_id"])
                    )
                }
                if isinstance(prevent_invites, OrderedDict)
                else None
            )
        self.bot.starting = False


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
