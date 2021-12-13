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


class Dj(Cog, name="dj.skip"):
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
        """
        This command skips the music a given number of times!

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        skips: :class:`int` optional
            The number of skips to do
        """
        await self.handle_skip(ctx, skips)

    @slash_command(
        name="skip",
        description="Skips the music a given number of times!",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_dj()
    @max_concurrency(1, per=BucketType.guild)
    async def skip_slash_command(
        self, inter: ApplicationCommandInteraction, skips: int = 1
    ):
        """
        This slash command skips the music a given number of times!

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        skips: :class:`int` optional
            The number of skips to do
        """
        await self.handle_skip(inter, skips)

    """ METHOD(S) """

    async def handle_skip(
        self, source: Union[Context, ApplicationCommandInteraction], skips: int
    ):
        """skip the musics a given number of times."""
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
                    f"⚠️ - {source.author.mention} - The player isn't connected!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - The player isn't connected!",
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

        for _ in range(skips):
            await player.skip()

        if isinstance(source, Context):
            await source.send(
                f"⏭️ - Skipping `{skips}` music{'s' if skips > 1 else ''}!"
            )
        else:
            await source.response.send_message(
                f"⏭️ - Skipping `{skips}` music{'s' if skips > 1 else ''}!"
            )


def setup(bot):
    bot.add_cog(Dj(bot))
