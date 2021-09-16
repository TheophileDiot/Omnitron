from discord import Embed, NotFound
from discord.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    Context,
    group,
    max_concurrency,
)
from dislash import ActionRow, Button
from time import time

from bot import Omnitron
from data import Utils


class Moderation(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    """ GROUP """

    @group(
        pass_context=True,
        name="poll",
        aliases=["polls"],
        usage="(sub-command)",
        description="This command manage the server's polls",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def poll_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's poll feature"
                )
            )

    """ COMMAND(S) """

    @poll_group.command(
        name="create",
        aliases=["new"],
        brief="🎛️",
        usage='"title" <duration> <type_of_duration (d == days, h == hours, m == minutes, s == seconds)> choice 1 choice 2 ...',
        description="Create a poll of a specific duration! (10 m minimum) (25 choices max)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_create_command(
        self,
        ctx: Context,
        title: str,
        duration: int,
        type_duration: Utils.to_lower,
        *choices: str,
    ):
        if "polls_channel" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - Please configure a polls channel before creating one! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.qualified_name}` to get more help.",
                delete_after=20,
            )
        elif len(choices) > 25:
            return await ctx.reply(
                f"⚠️ - {ctx.author.mention} - A poll can only contain a maximum of 25 choices! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.qualified_name}` to get more help.",
                delete_after=20,
            )

        duration_s = await self.bot.utils_class.parse_duration(
            duration, type_duration, ctx
        )
        if not duration_s:
            return

        em = Embed(
            colour=self.bot.color,
            title=title,
            description="Please click on the button of your choice, you can only answer once!",
        )

        em.set_thumbnail(url=ctx.guild.icon_url)
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        em.add_field(name="**Number of answers:**", value="`0`", inline=False)

        poll_msg = await self.bot.configs[ctx.guild.id]["polls_channel"].send(
            content=None, embed=em
        )
        buttons_rows = [[]]
        x = 0

        for choice in range(0, len(choices), 5):
            for c in range(
                choice, (choice + 5) if choice + 5 <= len(choices) else len(choices)
            ):
                buttons_rows[x].append(Button(style=2, label=f"{c} - {choices[c]}"))
            if c < len(choices) - 1:
                x += 1
                buttons_rows.append([])

        await poll_msg.edit(
            content=None,
            embed=em,
            components=[ActionRow(*row) for row in buttons_rows],
        )
        self.bot.poll_repo.create_poll(
            ctx.guild.id, poll_msg.id, duration_s, time(), buttons_rows
        )
        poll = self.bot.poll_repo.get_poll(ctx.guild.id, poll_msg.id)

        if "polls" not in self.bot.configs[ctx.guild.id]:
            self.bot.configs[ctx.guild.id]["polls"] = {}

        self.bot.configs[ctx.guild.id]["polls"][
            poll_msg.id
        ] = self.bot.utils_class.task_launcher(
            self.bot.utils_class.poll_completion, (ctx.guild, poll), count=1
        )

    @poll_group.command(
        name="info",
        aliases=["infos"],
        brief="🎛️",
        usage="<id_of_the_poll_message>",
        description="Retrieves information from the specified poll. (if no identifier is specified then retrieves information from all polls)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_infos_command(self, ctx: Context, id_message: int = None):
        if "polls_channel" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - Please configure a polls channel before getting informations about one! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.qualified_name}` to get more help.",
                delete_after=20,
            )

        poll = None
        if id_message:
            try:
                poll_message = await self.bot.configs[ctx.guild.id][
                    "polls_channel"
                ].fetch_message(id_message)
                poll = self.bot.poll_repo.get_poll(ctx.guild.id, id_message)
            except NotFound:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - The poll you are looking for does not exist!",
                    delete_after=20,
                )
        else:
            polls = [
                poll
                for key, poll in (self.bot.poll_repo.get_polls(ctx.guild.id)).items()
                if key != "old"
            ]
            if not polls:
                return await ctx.reply(
                    f"ℹ️ - {ctx.author.mention} - There is no poll going on!",
                    delete_after=20,
                )
            if len(polls) == 1:
                try:
                    poll = polls[0]
                    poll_message = await self.bot.configs[ctx.guild.id][
                        "polls_channel"
                    ].fetch_message(poll["id"])
                except NotFound:
                    await self.bot.poll_repo.delete_poll(poll["id"])
                    return await ctx.reply(
                        f"ℹ️ - {ctx.author.mention} - There is no poll going on!",
                        delete_after=20,
                    )

        em = Embed(
            colour=self.bot.color,
        )

        em.set_thumbnail(url=ctx.guild.icon_url)
        em.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        if poll:
            em.title = f"Poll information *{poll_message.embeds[0].title}*!"

            em.add_field(
                name="**⏲️ - Time remaining:**",
                value=self.bot.utils_class.duration(
                    poll["duration_s"] - (time() - poll["created_at_s"])
                ),
                inline=True,
            )
            em.add_field(
                name="**🔘 - Number of choices:**",
                value=len(poll["choices"]),
                inline=True,
            )
            em.add_field(
                name="**🔢 - Number of answers:**",
                value=len(poll["responses"])
                if "responses" in poll
                else "No answers recorded.",
                inline=True,
            )

            winner_choices = [
                f"`{key}`"
                for key, val in poll["choices"].items()
                if val == max(poll["choices"].values())
            ]
            em.add_field(
                name="**🏆 - Leading choice:**",
                value=", ".join(winner_choices)
                if len(winner_choices) != len(poll["choices"])
                else "No leading choice.",
                inline=True,
            )
        else:
            deleted_polls = 0
            em.title = "Information about the different polls in progress!"
            x = 0
            nl = "\n"
            while x < len(polls) and x <= 24:
                if x == 24:
                    em.add_field(
                        name="**Too many polls to display them all**",
                        value="...",
                        inline=False,
                    )
                else:
                    poll = polls[x]
                    try:
                        poll_message = await self.bot.configs[ctx.guild.id][
                            "polls_channel"
                        ].fetch_message(poll["id"])
                    except NotFound:
                        await self.bot.poll_repo.erase_poll(poll["id"])
                        deleted_polls += 1
                        if deleted_polls == len(polls):
                            return await ctx.reply(
                                f"ℹ️ - {ctx.author.mention} - There is no poll going on!",
                                delete_after=20,
                            )
                        x += 1
                        continue
                    winner_choices = [
                        f"`{key}`"
                        for key, val in poll["choices"].items()
                        if val == max(poll["choices"].values())
                    ]
                    em.add_field(
                        name=f'Poll "*{poll_message.embeds[0].title}*":',
                        value=f"**⏲️ - Time remaining:** {self.bot.utils_class.duration(poll['duration_s'] - (time() - poll['created_at_s']))}{nl}**🔘 - Number of choices:** {len(poll['choices'])}{nl}**🔢 - Number of answers:** {len(poll['responses']) if 'responses' in poll else 'No answers recorded.'}{nl}**🏆 - Leading choice:** {', '.join(winner_choices) if len(winner_choices) != len(poll['choices']) else 'No leading choice.'}",
                        inline=True,
                    )
                x += 1

        await ctx.send(content=None, embed=em)

    @poll_group.command(
        name="end",
        aliases=["ends", "finish"],
        brief="🛑",
        usage="<id_of_the_poll_message>",
        description="Stops a poll prematurely",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_end_command(self, ctx: Context, id_message: int):
        if "polls_channel" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - Please configure a polls channel before ending about one! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.qualified_name}` to get more help.",
                delete_after=20,
            )

        try:
            poll_msg = await self.bot.configs[ctx.guild.id][
                "polls_channel"
            ].fetch_message(id_message)
            poll = self.bot.poll_repo.get_poll(ctx.guild.id, id_message)
        except NotFound:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - The poll you are looking for does not exist!",
                delete_after=20,
            )

        self.bot.configs[ctx.guild.id]["polls"][poll_msg.id].cancel()
        self.bot.configs[ctx.guild.id]["polls"][
            poll_msg.id
        ] = self.bot.utils_class.task_launcher(
            self.bot.utils_class.poll_completion, (ctx.guild, poll, True), count=1
        )

        await ctx.send(
            f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been ended prematurely successfully!"
        )

    @poll_group.command(
        name="delete",
        aliases=["del", "remove"],
        brief="🚫",
        usage="<id_of_the_poll_message>",
        description="Delete a poll prematurely (unlike the command end it will erase completely the poll and not just end it)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_delete_command(self, ctx: Context, id_message: int):
        if "polls_channel" not in self.bot.configs[ctx.guild.id]:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - Please configure a polls channel before deleting about one! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {ctx.command.qualified_name}` to get more help.",
                delete_after=20,
            )

        try:
            poll_msg = await self.bot.configs[ctx.guild.id][
                "polls_channel"
            ].fetch_message(id_message)
        except NotFound:
            return await ctx.reply(
                f"ℹ️ - {ctx.author.mention} - The poll you are looking for does not exist!",
                delete_after=20,
            )

        self.bot.configs[ctx.guild.id]["polls"][poll_msg.id].cancel()
        del self.bot.configs[ctx.guild.id]["polls"][poll_msg.id]
        self.bot.poll_repo.erase_poll(ctx.guild.id, poll_msg.id)
        await poll_msg.delete()

        await ctx.send(
            f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been deleted prematurely successfully!"
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
