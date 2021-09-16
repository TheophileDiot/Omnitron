from discord.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
)

from data import Utils


class Dj(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="skip",
        aliases=["next"],
        usage="(number of skip(s))",
        description="Skip the music a given number of times!",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_permissions(send_messages=True)
    @max_concurrency(1, per=BucketType.guild)
    async def skip_command(self, ctx: Context, skips: int = 1):
        """skip the musics a given number of times."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The player isn't connected!",
                delete_after=20,
            )
        elif not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - Please be in the same voice room as the bot to control the music!",
                delete_after=20,
            )

        for _ in range(skips):
            await player.skip()
        await ctx.send(f"⏭️ - Skipping `{skips}` music{'s' if skips > 1 else ''}!")


def setup(bot):
    bot.add_cog(Dj(bot))
