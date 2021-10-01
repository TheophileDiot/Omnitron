from time import time
from typing import Union

from disnake import (
    ButtonStyle,
    Embed,
    GuildCommandInteraction,
    NotFound,
    Option,
    OptionChoice,
    OptionType,
)
from disnake.ext.commands import (
    bot_has_permissions,
    BucketType,
    Cog,
    Context,
    group,
    max_concurrency,
    slash_command,
)
from disnake.ui import Button, View

from bot import Omnitron
from data import Utils


class Moderation(Cog, name="moderation.poll"):
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

    @slash_command(
        name="poll",
        description="This command manage the server's polls",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def poll_slash_group(self, inter: GuildCommandInteraction):
        pass

    """ COMMAND(S) """

    """ CREATE """

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
        await self.handle_create(ctx, title, duration, type_duration, choices)

    @poll_slash_group.sub_command(
        name="create",
        description="Create a poll of a specific duration! (10 m minimum) (25 choices max)",
        options=[
            Option(
                name="title",
                description="The title of the poll",
                type=OptionType.string,
                required=True,
            ),
            Option(
                name="choices",
                description='Enter your different choices separated with ";"',
                type=OptionType.string,
                required=True,
            ),
            Option(
                name="duration",
                description='The value of the duration of the poll (default "10")',
                type=OptionType.integer,
                required=False,
            ),
            Option(
                name="type_duration",
                description='The type of the duration of the poll (default "m")',
                choices=[
                    OptionChoice(name="seconds", value="s"),
                    OptionChoice(name="minutes", value="m"),
                    OptionChoice(name="hours", value="h"),
                    OptionChoice(name="days", value="d"),
                ],
                required=False,
            ),
        ],
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_create_slash_command(
        self,
        inter: GuildCommandInteraction,
        title: str,
        choices: str,
        duration: int = 10,
        type_duration: Utils.to_lower = "m",
    ):
        await self.handle_create(
            inter,
            title,
            duration,
            type_duration,
            [c.strip() for c in choices.split(";")],
        )

    async def handle_create(
        self,
        source: Union[Context, GuildCommandInteraction],
        title: str,
        duration: int,
        type_duration: str,
        choices: list,
    ):
        if "polls_channel" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before creating one! `{self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.qualified_name}` to get more help.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before creating one!",
                    ephemeral=True,
                )
        elif len(choices) > 25:
            if isinstance(source, Context):
                return await source.reply(
                    f"⚠️ - {source.author.mention} - A poll can only contain a maximum of 25 choices! `{self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.qualified_name}` to get more help.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - A poll can only contain a maximum of 25 choices!",
                    ephemeral=True,
                )

        duration_s = await self.bot.utils_class.parse_duration(
            duration, type_duration, source
        )
        if not duration_s:
            return

        em: Embed = Embed(
            colour=self.bot.color,
            title=title,
            description="Please click on the button of your choice, you can only answer once!",
        )

        if source.guild.icon:
            em.set_thumbnail(url=source.guild.icon.url)
            em.set_author(name=source.guild.name, icon_url=source.guild.icon.url)
        else:
            em.set_author(name=source.guild.name)

        if self.bot.user.avatar:
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            em.set_footer(text=self.bot.user.name)

        em.add_field(name="**Number of answers:**", value="`0`", inline=False)
        view = View(timeout=None)

        for choice in range(0, len(choices), 5):
            for c in range(
                choice, (choice + 5) if choice + 5 <= len(choices) else len(choices)
            ):
                view.add_item(
                    Button(style=ButtonStyle.secondary, label=f"{c} - {choices[c]}")
                )

        poll_msg = await self.bot.configs[source.guild.id]["polls_channel"].send(
            embed=em,
            view=view,
        )
        self.bot.poll_repo.create_poll(
            source.guild.id,
            poll_msg.id,
            duration_s,
            time(),
            view,
        )
        poll = self.bot.poll_repo.get_poll(source.guild.id, poll_msg.id)

        if "polls" not in self.bot.configs[source.guild.id]:
            self.bot.configs[source.guild.id]["polls"] = {}

        self.bot.configs[source.guild.id]["polls"][
            poll_msg.id
        ] = self.bot.utils_class.task_launcher(
            self.bot.utils_class.poll_completion, (source.guild, poll), count=1
        )

        if isinstance(source, Context):
            await source.send(f'The poll "{title}" was created successfully!')
        else:
            await source.response.send_message(
                f'The poll "{title}" was created successfully!'
            )

    """ INFO """

    @poll_group.command(
        name="info",
        aliases=["infos"],
        brief="🎛️",
        usage="<id_of_the_poll_message>",
        description="Retrieves information from the specified poll. (if no identifier is specified then retrieves information from all polls)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_infos_command(self, ctx: Context, id_message: int = None):
        await self.handle_info(ctx, id_message)

    @poll_slash_group.sub_command(
        name="info",
        description="Retrieves information from the specified poll or every polls if none specified.",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_infos_slash_command(
        self, inter: GuildCommandInteraction, id_message: int = None
    ):
        if id_message and not isinstance(id_message, int):
            return await inter.response.send_message(
                f"ℹ️ - {inter.author.mention} - Please enter a valid message ID!"
            )

        await self.handle_info(inter, id_message)

    async def handle_info(
        self,
        source: Union[Context, GuildCommandInteraction],
        poll_id: Union[int, None] = None,
    ):
        if "polls_channel" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before getting information from one! `{self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.qualified_name}` to get more help.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before getting information from one!",
                    ephemeral=True,
                )

        poll = None

        if poll_id:
            try:
                poll_message = await self.bot.configs[source.guild.id][
                    "polls_channel"
                ].fetch_message(poll_id)
                poll = self.bot.poll_repo.get_poll(source.guild.id, poll_id)
            except NotFound:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                        ephemeral=True,
                    )
        else:
            polls = [
                poll
                for key, poll in (self.bot.poll_repo.get_polls(source.guild.id)).items()
                if key != "old"
            ]

            if not polls:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - {source.author.mention} - There is no poll going on!",
                        delete_after=20,
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - {source.author.mention} - There is no poll going on!",
                        ephemeral=True,
                    )
            elif len(polls) == 1:
                try:
                    poll = polls[0]
                    poll_message = await self.bot.configs[source.guild.id][
                        "polls_channel"
                    ].fetch_message(poll["id"])
                except NotFound:
                    await self.bot.poll_repo.delete_poll(poll["id"])

                    if isinstance(source, Context):
                        return await source.reply(
                            f"ℹ️ - {source.author.mention} - There is no poll going on!",
                            delete_after=20,
                        )
                    else:
                        return await source.response.send_message(
                            f"ℹ️ - {source.author.mention} - There is no poll going on!",
                            ephemeral=True,
                        )

        if isinstance(source, GuildCommandInteraction):
            await source.response.defer()

        em = Embed(
            colour=self.bot.color,
        )

        if source.guild.icon:
            em.set_thumbnail(url=source.guild.icon.url)
            em.set_author(name=source.guild.name, icon_url=source.guild.icon.url)
        else:
            em.set_author(name=source.guild.name)

        if self.bot.user.avatar:
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            em.set_footer(text=self.bot.user.name)

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
                        poll_message = await self.bot.configs[source.guild.id][
                            "polls_channel"
                        ].fetch_message(poll["id"])
                    except NotFound:
                        await self.bot.poll_repo.erase_poll(poll["id"])
                        deleted_polls += 1

                        if deleted_polls == len(polls):
                            if isinstance(source, Context):
                                return await source.reply(
                                    f"ℹ️ - {source.author.mention} - There is no poll going on!",
                                    delete_after=20,
                                )
                            else:
                                return await source.edit_original_message(
                                    content=f"ℹ️ - {source.author.mention} - There is no poll going on!"
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

        if isinstance(source, Context):
            await source.send(embed=em)
        else:
            await source.edit_original_message(embed=em)

    """ END """

    @poll_group.command(
        name="end",
        aliases=["ends", "finish"],
        brief="🛑",
        usage="<id_of_the_poll_message>",
        description="Stops a poll prematurely",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_end_command(self, ctx: Context, id_message: int):
        await self.handle_end(ctx, id_message)

    @poll_slash_group.sub_command(
        name="end",
        description="Stops a poll prematurely",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_end_slash_command(
        self, inter: GuildCommandInteraction, id_message: int = None
    ):
        if id_message and not isinstance(id_message, int):
            return await inter.response.send_message(
                f"ℹ️ - {inter.author.mention} - Please enter a valid message ID!"
            )

        await self.handle_end(inter, id_message)

    async def handle_end(
        self,
        source: Union[Context, GuildCommandInteraction],
        poll_id: Union[int, None] = None,
    ):
        if "polls_channel" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before ending one! `{self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.qualified_name}` to get more help.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before ending one!",
                    ephemeral=True,
                )

        try:
            poll_msg = await self.bot.configs[source.guild.id][
                "polls_channel"
            ].fetch_message(poll_id)
            poll = self.bot.poll_repo.get_poll(source.guild.id, poll_id)
        except NotFound:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                    ephemeral=True,
                )

        self.bot.configs[source.guild.id]["polls"][poll_msg.id].cancel()
        self.bot.configs[source.guild.id]["polls"][
            poll_msg.id
        ] = self.bot.utils_class.task_launcher(
            self.bot.utils_class.poll_completion, (source.guild, poll, True), count=1
        )

        if isinstance(source, Context):
            await source.send(
                f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been ended prematurely successfully!"
            )
        else:
            await source.response.send_message(
                f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been ended prematurely successfully!"
            )

    """ DELETE """

    @poll_group.command(
        name="delete",
        aliases=["del", "remove"],
        brief="🚫",
        usage="<id_of_the_poll_message>",
        description="Delete a poll prematurely (unlike the command end it will erase completely the poll and not just end it)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_delete_command(self, ctx: Context, id_message: int):
        await self.handle_delete(ctx, id_message)

    @poll_slash_group.sub_command(
        name="delete",
        description="Delete a poll prematurely (unlike the command end it will erase completely the poll)",
    )
    @max_concurrency(1, per=BucketType.guild)
    async def poll_delete_slash_command(
        self, inter: GuildCommandInteraction, id_message: int = None
    ):
        if id_message and not isinstance(id_message, int):
            return await inter.response.send_message(
                f"ℹ️ - {inter.author.mention} - Please enter a valid message ID!"
            )

        await self.handle_delete(inter, id_message)

    async def handle_delete(
        self,
        source: Union[Context, GuildCommandInteraction],
        poll_id: Union[int, None] = None,
    ):
        if "polls_channel" not in self.bot.configs[source.guild.id]:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before deleting one! `{self.bot.utils_class.get_guild_pre(source.message)[0]}help {source.command.qualified_name}` to get more help.",
                    delete_after=20,
                )
            else:
                return await source.response.send_message(
                    f"ℹ️ - {source.author.mention} - Please configure a polls channel before deleting one!",
                    ephemeral=True,
                )

        try:
            poll_msg = await self.bot.configs[source.guild.id][
                "polls_channel"
            ].fetch_message(poll_id)
        except NotFound:
            if isinstance(source, Context):
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                    delete_after=20,
                )
            else:
                return await source.reply(
                    f"ℹ️ - {source.author.mention} - The poll you are looking for does not exist!",
                    ephemeral=True,
                )

        self.bot.configs[source.guild.id]["polls"][poll_msg.id].cancel()
        del self.bot.configs[source.guild.id]["polls"][poll_msg.id]
        self.bot.poll_repo.erase_poll(source.guild.id, poll_msg.id)
        await poll_msg.delete()

        if isinstance(source, Context):
            await source.send(
                f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been deleted prematurely successfully!"
            )
        else:
            await source.response.send_message(
                f"ℹ️ - The poll `{poll_msg.embeds[0].title}` (ID: `{poll_msg.id}`) has been deleted prematurely successfully!"
            )


def setup(bot):
    bot.add_cog(Moderation(bot))
