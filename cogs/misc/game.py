from asyncio import sleep
from random import choice
from typing import Union

from disnake import (
    ApplicationCommandInteraction,
    ButtonStyle,
    CategoryChannel,
    Embed,
    Enum,
    Forbidden,
    Member,
    NotFound,
    PermissionOverwrite,
    Role,
    SelectOption,
    TextChannel,
    VoiceChannel,
    Message,
)
from disnake.abc import Snowflake
from disnake.ext.commands import (
    bot_has_guild_permissions,
    bot_has_permissions,
    BucketType,
    Context,
    Cog,
    group,
    guild_only,
    max_concurrency,
    Param,
    slash_command,
)
from disnake.ext.commands.errors import (
    BadArgument,
    BadUnionArgument,
    MissingRequiredArgument,
)

from bot import Omnitron
from data import DurationType, Utils, Xp_class

NUM2EMOJI = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣"}


def check_for_win_fourinarow(board) -> bool:
    board = [[col for col in row[1:-1]] for row in board[0:-1]]
    for x in range(len(board)):
        for y in range(len(board[0])):
            if x + 3 < 7:
                if (
                    board[x][y] != "⚪"
                    and board[x][y] == board[x + 1][y]
                    and board[x + 1][y] == board[x + 2][y]
                    and board[x + 2][y] == board[x + 3][y]
                ):
                    return True
            if y + 3 < 7:
                if (
                    board[x][y] != "⚪"
                    and board[x][y] == board[x][y + 1]
                    and board[x][y + 1] == board[x][y + 2]
                    and board[x][y + 2] == board[x][y + 3]
                ):
                    return True
            if x + 3 < 7 and y + 3 < 7:
                if (
                    board[x][y] != "⚪"
                    and board[x][y] == board[x + 1][y + 1]
                    and board[x + 1][y + 1] == board[x + 2][y + 2]
                    and board[x + 2][y + 2] == board[x + 3][y + 3]
                ):
                    return True
            if x - 3 > 0 and y + 3 < 7:
                if (
                    board[x][y] != "⚪"
                    and board[x][y] == board[x - 1][y + 1]
                    and board[x - 1][y + 1] == board[x - 2][y + 2]
                    and board[x - 2][y + 2] == board[x - 3][y + 3]
                ):
                    return True

    return False


class Game(Cog):
    def __init__(self, bot: Omnitron) -> None:
        self.bot = bot

    """ METHODS """

    async def get_last_game_message(self, channel: TextChannel) -> TextChannel or None:
        try:
            return channel.fetch_message(self.games[channel.guild.id][channel.id])
        except NotFound:
            return None

    """ MAIN GROUP """

    @group(
        pass_context=True,
        case_insensitive=True,
        name="game",
        aliases=["launch"],
        usage="(sub-command)",
        description="This command manage the server's games",
    )
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    @bot_has_permissions(send_messages=True)
    async def games_group(self, ctx: Context):
        """
        This command group manages the server's games

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        """
        if (
            "games_category" not in self.bot.configs[ctx.guild.id]
            or not self.bot.configs[ctx.guild.id]["games_category"]
        ) and ctx.invoked_subcommand is not None:
            return await ctx.reply("ℹ️ - Games are not configured on this server")

        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=self.bot.utils_class.get_embed_from_ctx(
                    ctx, title="Server's games"
                )
            )

    @slash_command(
        name="game",
        description="Manages the server's games",
    )
    @guild_only()
    @Utils.check_bot_starting()
    @Utils.check_moderator()
    async def games_slash_group(self, inter: ApplicationCommandInteraction):
        """
        This slash command group manages the server's games

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        """
        if (
            "games_category" not in self.bot.configs[inter.guild.id]
            or not self.bot.configs[inter.guild.id]["games_category"]
        ):
            return await inter.response.send_message(
                f"ℹ️ - Games are not configured on this server",
                ephemeral=True,
            )

        pass

    """ MAIN GROUP'S COMMAN(S) """

    @games_group.command(
        pass_context=True,
        name="fourinarow",
        aliases=["4inarow"],
        brief="4️⃣",
        description="Starts a four in a row game against another guild member",
        usage="@member",
    )
    @bot_has_guild_permissions(manage_channels=True)
    @max_concurrency(1, BucketType.member)
    async def game_fourinarow_command(self, ctx: Context, member: Member):
        """
        This command starts a four in a row game against another guild member

        Parameters
        ----------
        ctx: :class:`disnake.ext.commands.Context`
            The command context
        member: :class:`disnake.Member`
            The member to play against
        """
        await self.handle_fourinarow(ctx, member)

    @games_slash_group.sub_command(
        name="fourinarow",
        description="Starts a four in a row game against another guild member",
    )
    @bot_has_guild_permissions(manage_channels=True)
    @max_concurrency(1, BucketType.member)
    async def game_fourinarow_slash_command(
        self, inter: ApplicationCommandInteraction, member: Member
    ):
        """
        This slash command starts a four in a row game against another guild member

        Parameters
        ----------
        inter: :class:`disnake.ext.commands.ApplicationCommandInteraction`
            The application command interaction
        member: :class:`disnake.Member`
            The member to play against
        """
        await self.handle_fourinarow(inter, member)

    async def handle_fourinarow(
        self, source: Union[Context, ApplicationCommandInteraction], member: Member
    ):
        if isinstance(source, Context):
            if member.bot:
                return await source.reply(
                    f"⚠️ - {source.author.mention} - You cannot start a four in a row game against a bot"
                )
            elif source.author.id == member.id:
                return await source.reply(
                    f"⚠️ - {source.author.mention} - You cannot start a four in a row game against yourself"
                )
        else:
            if member.bot:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - You cannot start a four in a row game against a bot",
                    ephemeral=True,
                )
            elif source.author.id == member.id:
                return await source.response.send_message(
                    f"⚠️ - {source.author.mention} - You cannot start a four in a row game against yourself",
                    ephemeral=True,
                )

        channel_name = f"4inarow-{source.author.name.lower()}-{member.name.lower()}"
        channel_name_other = (
            f"4inarow-{member.name.lower()}-{source.author.name.lower()}"
        )
        channels = {channel.name: channel for channel in source.guild.text_channels}
        channel = None

        if channel_name in channels.keys() or channel_name_other in channels.keys():
            channel = (
                channels[channel_name]
                if channel_name in channels.keys()
                else channels[channel_name_other]
            )
            message = await self.get_last_game_message(channel)

            if message:
                if isinstance(source, Context):
                    return await source.reply(
                        f"ℹ️ - You already have a four in a row game against `{member.name}`! {channels[channel_name].mention if channel_name in channels.keys() else channels[channel_name_other].mention}"
                    )
                else:
                    return await source.response.send_message(
                        f"ℹ️ - You already have a four in a row game against `{member.name}`! {channels[channel_name].mention if channel_name in channels.keys() else channels[channel_name_other].mention}",
                        ephemeral=True,
                    )

        if not channel:
            channel = await source.guild.create_text_channel(
                name=channel_name,
                overwrites={
                    member: PermissionOverwrite(
                        **{"send_messages": True, "add_reactions": False}
                    ),
                    source.author: PermissionOverwrite(
                        **{"send_messages": True, "add_reactions": False}
                    ),
                    source.guild.default_role: PermissionOverwrite(
                        **{"send_messages": False, "add_reactions": False}
                    ),
                    self.bot.user: PermissionOverwrite(
                        **{"send_messages": True, "add_reactions": True}
                    ),
                },
                category=self.bot.configs[source.guild.id]["games_category"],
                reason=f"Creation of the {source.author} vs {member} 4 in a row game channel",
            )

            await source.channel.send(
                f"🔴🔴🔴🔴 - The four in a row game {channel.mention} opposing `{source.author.name}` and `{member.name}` has been created - 🔵🔵🔵🔵"
            )

        board = [
            ["⬛" if x == 0 or x == 8 or y == 7 else "⚪" for x in range(9)]
            for y in range(8)
        ]
        nl = "\n"

        msg = await channel.send(
            content=f"🔴🔴🔴🔴 - {source.author.mention} **VS** {member.mention} - 🔵🔵🔵🔵\n\n**This is `{choice([source.author, member]).name}`'s turn**\n\n{nl.join([''.join(row) for row in board])}"
        )

        if "games" not in self.bot.configs[source.guild.id]:
            self.bot.configs[source.guild.id]["games"] = {
                channel.id: {
                    "game_id": msg.id,
                    "players": {"player1": f"{source.author}", "player2": f"{member}"},
                }
            }
        else:
            self.bot.configs[source.guild.id]["games"][channel.id] = {
                "game_id": msg.id,
                "players": {"player1": f"{source.author}", "player2": f"{member}"},
            }

        self.bot.games_repo.create_game(
            source.guild.id,
            channel.id,
            msg.id,
            self.bot.configs[source.guild.id]["games"][channel.id]["players"],
        )

        await sleep(2)

        for x in range(1, 8):
            await msg.add_reaction(NUM2EMOJI[x])

        await msg.add_reaction("🔄")


def setup(bot):
    bot.add_cog(Game(bot))
