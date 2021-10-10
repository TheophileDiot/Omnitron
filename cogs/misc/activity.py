from typing import Union

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
    youtube = "755600276941176913"
    poker = "755827207812677713"
    betrayal = "773336526917861400"
    fishing = "814288819477020702"
    chess = "832012774040141894"
    letter_tile = "879863686565621790"
    word_snack = "879863976006127627"
    doodle_crew = "878067389634314250"


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
        description="This command manage the server's activities",
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
        name="youtube_together",
        aliases=["yt_together", "ytt"],
        brief="⏯️",
        usage="#voice_channel",
        description="Create an instant invite link into the activity YouTube Together in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_youtube_together_command(
        self, ctx: Context, channel: VoiceChannel
    ):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 755600276941176913)
        )

    @activity_group.command(
        name="poker_night",
        aliases=["p_n"],
        brief="♣️",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Poker Night in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_poker_night_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 755827207812677713)
        )

    @activity_group.command(
        name="betrayal_io",
        aliases=["b_io"],
        brief="🔫️",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Betrayal.io in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_betrayal_io_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 773336526917861400)
        )

    @activity_group.command(
        name="fishington_io",
        aliases=["f_io"],
        brief="🎣",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Fishington.io in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_fishington_io_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 814288819477020702)
        )

    @activity_group.command(
        name="chess",
        aliases=["chess_in_the_park"],
        brief="♟️",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Chess In The Park in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_chess_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 832012774040141894)
        )

    @activity_group.command(
        name="letter_tile",
        aliases=["l_tile"],
        brief="🇱",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Letter Tile in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_letter_tile_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879863686565621790)
        )

    @activity_group.command(
        name="word_snack",
        aliases=["w_snack"],
        brief="💬",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Word Snack in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_word_snack_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 879863976006127627)
        )

    @activity_group.command(
        name="doodle_crew",
        aliases=["d_crew"],
        brief="🖌️",
        usage="#voice_channel",
        description="Create an instant invite link into the activity Doodle Crew in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_doodle_crew_command(self, ctx: Context, channel: VoiceChannel):
        await ctx.send(
            embed=await self.create_activity(ctx, channel, 878067389634314250)
        )

    @activity_group.command(
        name="custom",
        aliases=["cstm"],
        brief="❓",
        usage="#voice_channel <application_id>",
        description="Create an instant invite link into a custom activity in the specified channel",
    )
    @bot_has_guild_permissions(create_instant_invite=True)
    async def activity_custom_command(
        self, ctx: Context, channel: VoiceChannel, activity: int
    ):
        await ctx.send(embed=await self.create_activity(ctx, channel, activity))

    """ METHOD(S) """

    async def create_activity(
        self,
        source: Union[Context, ApplicationCommandInteraction],
        channel: VoiceChannel,
        activity: int,
    ) -> Embed or None:
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
