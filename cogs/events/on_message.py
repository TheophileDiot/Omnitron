from asyncio import sleep
from discord import Forbidden, Message
from discord.ext.commands import Cog

from bot import Omnitron
from data import Utils, Xp_class


class Events(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot
        self.limitation = []
        self.xp_class = Xp_class(bot)

    """ EVENT """

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_message(self, message: Message, tries: int = 0):
        """When a message is sent, if the prevent_invites option is on check if there is an invitation link to another discord server in the message and is the xp is on then manage the user's xp"""
        await self.bot.wait_until_ready()
        if message.is_system() or message.author.bot or not message.guild:
            return

        ctx = await self.bot.get_context(message=message)

        if (
            ctx.message.mentions
            and self.bot.user in ctx.message.mentions
            and (
                len(ctx.message.content) == len(f"{self.bot.user.mention}")
                or len(ctx.message.content) == len(f"{self.bot.user.mention}") + 1
            )
        ):
            try:
                msg = await ctx.send(
                    f"ℹ️ - {ctx.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`!"
                )
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message: `ℹ️ - {ctx.author.mention} - Here's my prefix for this guild: `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`!`)!"
                raise

            try:
                await msg.add_reaction("👀")
            except Forbidden as f:
                f.text = f"⚠️ - I don't have the right permissions to add reactions in the channel {ctx.channel.mention} (message: {msg.jump_url}, reaction: 👀)!"
                raise

        try:
            if "prevent_invites" in self.bot.configs[message.guild.id]:
                await self.bot.utils_class.check_invite(ctx)
            if self.bot.configs[message.guild.id]["xp"]["is_on"]:
                if (
                    "xp_gain_channels" not in self.bot.configs[message.guild.id]
                    or "xp_gain_channels" in self.bot.configs[message.guild.id]
                    and (
                        message.channel.id
                        in self.bot.configs[message.guild.id]["xp_gain_channels"][
                            "TextChannel"
                        ]
                        or not self.bot.configs[message.guild.id]["xp_gain_channels"][
                            "TextChannel"
                        ]
                    )
                ):
                    _id = f"{message.guild.id}.{message.author.id}"
                    if _id not in self.limitation:
                        await self.xp_class.manage_xp(message.author, "message")
                        self.limitation.append(_id)
                        await self.cooldown_messages(_id)
        except KeyError:
            if tries < 3:
                await sleep(5)
                await self.on_message(message, tries=tries + 1)

    """ METHODS """

    async def cooldown_messages(self, _id: str):
        """This method manage the messages cooldown"""
        await sleep(5)
        del self.limitation[self.limitation.index(_id)]


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
