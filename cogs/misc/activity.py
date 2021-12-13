from typing import Union, Optional

from disnake import (
    ApplicationCommandInteraction,
    Embed,
    Enum,
    HTTPException,
    VoiceChannel,
)
from disnake.ext.commands import (
    bot_has_guild_permissions,
    bot_has_permissions,
    Cog,
    Context,
    group,
    guild_only,
    slash_command,
)
from disnake.http import Route

from bot import Omnitron
from data import Utils


class PartyType(Enum):
    awkword = "879863881349087252"
    betrayal = "773336526917861400"
    checkers = "832013003968348200"
    chess = "832012774040141894"
    doodle_crew = "878067389634314250"
    fishing = "814288819477020702"
    letter_tile = "879863686565621790"
    poker = "755827207812677713"
    sketchy_artist = "879864070101172255"
    spellcast = "852509694341283871"
    watch_together = "880218394199220334"
    word_snack = "879863976006127627"
    youtube = "755600276941176913"


class Miscellaneous(Cog, name="misc.activity"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ GROUP """

    @group(
        pass_context=True,
        name="activity",
        aliases=["activities"],
        usage="(sub-command)",
        description="This command manage the server's activities",
    )
    @Utils.check_bot_starting()
    @bot_has_permissions(send_messages=True)
    async def activity_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's activity feature"
                )
            )

    """ SLASH COMMAND """

    @slash_command(
        name="activity",
        description="Manages the server's activities",
    )
    @guild_only()
    @Utils.check_bot_starting()
    async def activity_slash_command(
        self,
        inter: ApplicationCommandInteraction,
        channel: VoiceChannel,
        activity: PartyType = None,
        custom_activity: int = None,
    ):
        """
        This slash command manages the server's activities

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        activity: :class:`PartyType` optional
            Choose one of the default activities available
        custom_activity: :class:`int` optional
            If you know an activity that is not shown in the activity section then enter it's ID here!
        """
        if not isinstance(channel, VoiceChannel):
            return await inter.response.send_message(
                "The channel precised must be a valid VoiceChannel!", ephemeral=True
            )
        elif not activity and custom_activity:
            activity = custom_activity
        elif not activity:
            return await inter.response.send_message(
                "Select at least an activity or enter a custom one!", ephemeral=True
            )

        await inter.response.send_message(
            embed=await self.create_activity(inter, channel, activity)
        )

    """ COMMAND(S) """

    @activity_group.command(
        name="awkword",
        aliases=["awkw"],
        brief="📝",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity awkword in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_awkword_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity awkword in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879863881349087252)
        )

    @activity_group.command(
        name="betrayal_io",
        aliases=["b_io"],
        brief="🔫️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Betrayal.io in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_betrayal_io_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Betrayal.io in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 773336526917861400)
        )

    @activity_group.command(
        name="checkers",
        aliases=["chkrs"],
        brief="♚",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Checkers In The Park in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_checkers_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Checkers In The Park in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 832013003968348200)
        )

    @activity_group.command(
        name="chess",
        aliases=["chess_in_the_park"],
        brief="♟️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Chess In The Park in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_chess_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Chess In The Park in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 832012774040141894)
        )

    @activity_group.command(
        name="doodle_crew",
        aliases=["d_crew"],
        brief="🖌️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Doodle Crew in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_doodle_crew_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Doodle Crew in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 878067389634314250)
        )

    @activity_group.command(
        name="fishington_io",
        aliases=["f_io"],
        brief="🎣",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Fishington.io in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_fishington_io_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Fishington.io in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 814288819477020702)
        )

    @activity_group.command(
        name="letter_tile",
        aliases=["l_tile"],
        brief="🇱",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Letter Tile in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_letter_tile_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Letter Tile in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879863686565621790)
        )

    @activity_group.command(
        name="poker_night",
        aliases=["p_n"],
        brief="♣️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Poker Night in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_poker_night_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Poker Night in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 755827207812677713)
        )

    @activity_group.command(
        name="sketchy_artist",
        aliases=["s_a"],
        brief="✍️️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Sketchy Artist in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_sketchy_artist_command(
        self, ctx: Context, channel: VoiceChannel
    ):
        """
        This command creates an instant invite link into the activity Sketchy Artist in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879864070101172255)
        )

    @activity_group.command(
        name="spellcast",
        aliases=["spell"],
        brief="🪄",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Spellcast in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_spellcast_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Spellcast in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 852509694341283871)
        )

    @activity_group.command(
        name="watch_together",
        aliases=["w_t"],
        brief="📺",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity WatchTogether in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_watch_together_command(
        self, ctx: Context, channel: VoiceChannel
    ):
        """
        This command creates an instant invite link into the activity WatchTogether in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 880218394199220334)
        )

    @activity_group.command(
        name="word_snack",
        aliases=["w_snack"],
        brief="💬",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity Word Snack in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_word_snack_command(self, ctx: Context, channel: VoiceChannel):
        """
        This command creates an instant invite link into the activity Word Snack in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879863976006127627)
        )

    @activity_group.command(
        name="youtube_together",
        aliases=["yt_together", "ytt"],
        brief="⏯️",
        usage="#voice_channel",
        description="Creates an instant invite link into the activity YouTube Together in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_youtube_together_command(
        self, ctx: Context, channel: VoiceChannel
    ):
        """
        This command creates an instant invite link into the activity Youtube Together in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 755600276941176913)
        )

    @activity_group.command(
        name="custom",
        aliases=["cstm"],
        brief="❓",
        usage="#voice_channel <application_id>",
        description="Creates an instant invite link into a custom activity in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_custom_command(
        self, ctx: Context, channel: VoiceChannel, activity: int
    ):
        """
        This command creates an instant invite link into a custom activity in the specified channel

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        channel: :class:`disnake.VoiceChannel`
            The voice channel where the activity will take place
        """
        await ctx.send(embed=await self.create_activity(ctx, channel, activity))

    """ METHOD(S) """

    async def create_activity(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        channel: VoiceChannel,
        activity: int,
    ) -> Optional[Embed]:
        data = {
            "max_age": 0,
            "max_uses": 0,
            "target_application_id": activity,
            "target_type": 2,
            "temporary": False,
        }

        try:
            resp = await self.bot.http.request(
                Route("POST", f"/channels/{channel.id}/invites"), json=data
            )
        except HTTPException as e:
            if e.code == 50035:
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - The application ID you gave is not an available one!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"⚠️ - {source.author.mention} - The application ID you gave is not an available one!",
                        ephemeral=True,
                    )
            else:
                if isinstance(source, Context):
                    return await source.reply(
                        f"⚠️ - {source.author.mention} - An error happened, please try again in a few seconds!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"⚠️ - {source.author.mention} - An error happened, please try again in a few seconds!",
                        ephemeral=True,
                    )

        em = Embed(
            colour=self.bot.color,
            title="The channel is ready!",
            description=f"Added **{resp['target_application']['name']}** to {channel.mention}\n> Click on the hyperlink to join.",
            url=f"https://discord.gg/{resp['code']}",
        )
        em.set_thumbnail(
            url=f"https://cdn.discordapp.com/app-icons/{resp['target_application']['id']}/{resp['target_application']['icon']}.png"
        )
        em.set_author(
            name=f"{source.author}",
            icon_url=source.author.avatar.url if source.author.avatar else None,
        )

        if self.bot.user.avatar:
            em.set_footer(
                text=f"Requested by {source.author}", icon_url=self.bot.user.avatar.url
            )
        else:
            em.set_footer(text=f"Requested by {source.author}")

        return em


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
