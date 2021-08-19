from asyncio import sleep
from discord import Member
from discord.ext.commands import Cog
from time import time

from bot import Omnitron
from data import Utils


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_member_join(self, member: Member, tries: int = 0):
        """When a member joins a guild, add him to the database and if the mute_on_join option is on then mute him for a limited amount of time"""
        await self.bot.wait_until_ready()
        if member.bot:
            return
        self.bot.user_repo.create_user(member.guild.id, member.id, f"{member}")
        roles = []
        try:
            if "mute_on_join" in self.bot.configs[member.guild.id]:
                roles += [
                    self.bot.configs[member.guild.id]["mute_on_join"]["muted_role"]
                ]
                await member.add_roles(*roles, reason="Has just joined the server.")
                self.bot.user_repo.mute_user(
                    member.guild.id,
                    member.id,
                    self.bot.configs[member.guild.id]["mute_on_join"]["duration"],
                    time(),
                    f"{self.bot.user}",
                    "joined the server",
                )
                self.bot.utils_class.task_launcher(
                    self.bot.utils_class.mute_completion,
                    (
                        self,
                        self.bot.user_repo.get_user(member.guild.id, member.id),
                        member.guild.id,
                    ),
                    count=1,
                )
        except KeyError:
            if tries < 3:
                await sleep(5)
                await self.on_member_join(member, tries=tries + 1)


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
