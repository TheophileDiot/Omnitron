from discord.ext.commands import (
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
        name="stop",
        aliases=["end", "leave", "disconnect"],
        description="Stop the music in progress!",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @max_concurrency(1, per=BucketType.guild)
    async def stop_command(self, ctx: Context):
        """Disconnects the player from the voice channel and clears its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player or not player.is_playing:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The bot is not playing!",
                delete_after=20,
            )
        elif not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - The player is not connected!",
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

        await self.bot.utils_class.clear_playlist(ctx.guild)
        await ctx.send(f"⏹️ - Music off!")


def setup(bot):
    bot.add_cog(Dj(bot))
