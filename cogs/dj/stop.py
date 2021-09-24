from typing import Union

from disnake import ApplicationCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    max_concurrency,
    slash_command,
)

from data import Utils


class Dj(Cog, name="dj.stop"):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name="stop",
        aliases=["end", "leave", "disconnect"],
        description="Stop the music in progress!",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_permissions(send_messages=True)
    @max_concurrency(1, per=BucketType.guild)
    async def stop_command(self, ctx: Context):
        await self.handle_stop(ctx)

    @slash_command(
        name="stop",
        description="Stop the music in progress!",
    )
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @max_concurrency(1, per=BucketType.guild)
    async def stop_command(self, inter: ApplicationCommandInteraction):
        await self.handle_stop(inter)

    """ METHOD(S) """

    async def handle_stop(self, source: Union[Context, ApplicationCommandInteraction]):
        """Disconnects the player from the voice channel and clears its queue."""
        player = self.bot.lavalink.player_manager.get(source.guild.id)

        if not player or not player.is_playing:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The bot is not playing!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The bot is not playing!",
                    ephemeral=True,
                )
        elif not player.is_connected:
            # We can't disconnect, if we're not connected.
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The player is not connected!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The player is not connected!",
                    ephemeral=True,
                )
        elif not source.author.voice or (
            player.is_connected
            and source.author.voice.channel.id != int(player.channel_id)
        ):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - Please be in the same voice room as the bot to control the music!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - Please be in the same voice room as the bot to control the music!",
                    ephemeral=True,
                )

        await self.bot.utils_class.clear_playlist(source.guild)

        if isinstance(source, Context):
            await source.send(f"⏹️ - Music off!")
        else:
            await source.response.send_message(f"⏹️ - Music off!")


def setup(bot):
    bot.add_cog(Dj(bot))
