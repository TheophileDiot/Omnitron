from typing import Union

from disnake import ApplicationCommandInteraction
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    command,
    Context,
    guild_only,
    max_concurrency,
    slash_command,
)

from data import Utils


class Dj(Cog, name="dj.pause"):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pause", description="Pauses the current music!")
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @bot_has_permissions(send_messages=True)
    @max_concurrency(1, per=BucketType.guild)
    async def pause_command(self, ctx: Context):
        """
        This command Pauses the current music!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        await self.handle_pause(ctx)

    @slash_command(name="pause", description="Pauses the current music!")
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @max_concurrency(1, per=BucketType.guild)
    async def pause_slash_command(self, inter: ApplicationCommandInteraction):
        """
        This slash command Pauses the current music!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        await self.handle_pause(inter)

    """ METHOD(S) """

    async def handle_pause(self, source: Union[Context, ApplicationCommandInteraction]):
        """pause the player."""
        player = self.bot.lavalink.player_manager.get(source.guild.id)

        if not player or not player.is_playing:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The bot isn't playing!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The bot isn't playing!",
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
        elif player.paused:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - The bot is already paused!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The bot is already paused!",
                    ephemeral=True,
                )

        await player.set_pause(True)

        if isinstance(source, Context):
            await source.send(f"⏸️ - Pausing the music!")
        else:
            await source.response.send_message(f"⏸️ - Pausing the music!")


def setup(bot):
    bot.add_cog(Dj(bot))
