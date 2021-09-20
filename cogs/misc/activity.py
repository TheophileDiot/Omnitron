from disnake import Embed, HTTPException, VoiceChannel
from disnake.ext.commands import (
    bot_has_guild_permissions,
    bot_has_permissions,
    Cog,
    Context,
    group,
)
from disnake.http import Route

from bot import Omnitron
from data import Utils


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
        self, ctx: Context, channel: VoiceChannel, activity: int
    ) -> Embed:
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
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - The application ID you gave is not an available one!",
                    delete_after=20,
                )
            else:
                return await ctx.reply(
                    f"⚠️ - {ctx.author.mention} - An error happened, please try again in a few seconds!",
                    delete_after=20,
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
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
        )
        em.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        return em


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
