from discord import Member, VoiceState
from discord.ext.commands import Cog

from bot import Omnitron
from data import Xp_class


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.voice_intervals = {}
        self.xp_class = Xp_class(bot)

    """ EVENT """

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.bot:
            return

        _id = f"{member.guild.id}.{member.id}"

        if after.channel:
            if _id not in self.voice_intervals:
                if self.bot.configs[member.guild.id]["xp"]["is_on"]:
                    self.voice_intervals[_id] = self.bot.utils_class.task_launcher(
                        self.vocal_interval, (member,), minutes=7
                    )
            elif member.voice.channel == member.guild.afk_channel:
                self.voice_intervals.pop(_id).cancel()
        else:
            if _id in self.voice_intervals:
                self.voice_intervals.pop(_id).cancel()

        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.bot.utils_class.clear_playlist(member.guild)

    """ METHOD(S) """

    async def vocal_interval(self, member: Member):
        """This method manage the vocal xp cooldown"""
        await self.xp_class.manage_xp(member, "vocal")


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
