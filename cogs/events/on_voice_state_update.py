from time import time

from disnake import Member, VoiceState
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils, Xp_class


class Events(Cog, name="events.on_voice_state_update"):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.voice_intervals = {}
        self.count_intervals = {}
        self.xp_class = Xp_class(bot)

    """ EVENT """

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        _id = f"{member.guild.id}.{member.id}"

        if _id in self.count_intervals:
            self.bot.user_repo.add_voice_time(
                member.guild.id,
                member.id,
                self.count_intervals[_id]["voice_channel"].id,
                time() - self.count_intervals[_id]["joining_time"],
            )

            del self.count_intervals[_id]

        if after.channel:
            if member.voice.channel != member.guild.afk_channel:
                self.count_intervals[_id] = {
                    "joining_time": time(),
                    "voice_channel": after.channel,
                }

            if _id not in self.voice_intervals:
                if self.bot.configs[member.guild.id]["xp"]["is_on"]:
                    if (
                        "xp_gain_channels" in self.bot.configs[member.guild.id]
                        and "VoiceChannel"
                        in self.bot.configs[member.guild.id]["xp_gain_channels"]
                        and (
                            not self.bot.configs[member.guild.id]["xp_gain_channels"][
                                "VoiceChannel"
                            ]
                            or after.channel.id
                            in self.bot.configs[member.guild.id]["xp_gain_channels"][
                                "VoiceChannel"
                            ]
                        )
                    ):
                        self.voice_intervals[_id] = self.bot.utils_class.task_launcher(
                            self.vocal_interval, (member,), minutes=7
                        )
            elif (
                member.voice.channel == member.guild.afk_channel
                or "xp_gain_channels" in self.bot.configs[member.guild.id]
                and "VoiceChannel"
                in self.bot.configs[member.guild.id]["xp_gain_channels"]
                and self.bot.configs[member.guild.id]["xp_gain_channels"][
                    "VoiceChannel"
                ]
                and after.channel.id
                not in self.bot.configs[member.guild.id]["xp_gain_channels"][
                    "VoiceChannel"
                ]
            ):
                self.voice_intervals.pop(_id).cancel()
        else:
            if _id in self.voice_intervals:
                self.voice_intervals.pop(_id).cancel()

        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                if member.guild.voice_client:
                    await member.guild.voice_client.disconnect(force=True)

                self.bot.playlists[member.guild.id].clear()

    """ METHOD(S) """

    async def vocal_interval(self, member: Member):
        """This method manage the vocal xp cooldown"""
        await self.xp_class.manage_xp(member, "vocal")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
