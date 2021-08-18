from discord import Message, Member, Embed
from discord.ext.tasks import loop
from discord.ext.commands import Context, check
from discord.ext.commands.errors import BadArgument
from math import floor
from typing import Union


# The `args` are the arguments passed into the loop
def task_launcher(function, param, **interval) -> loop:
    """Creates new instances of `tasks.Loop`"""
    # Creating the task
    # You can also pass a static interval and/or count
    new_task = loop(**interval)(function)
    # Starting the task
    new_task.start(*param)
    return new_task


def to_lower(argument):
    if argument.isdigit():
        raise BadArgument
    if isinstance(argument, str):
        return argument.lower()
    elif isinstance(argument, list):
        return [arg.lower() for arg in argument]


def check_moderator():
    def predicate(ctx: Context, *args, **kwargs):
        ctx.bot.last_check = "moderator"
        return is_mod(ctx.author, ctx.bot)

    return check(predicate)


def is_mod(member, bot) -> bool:
    return (
        set(member.roles) & set(bot.moderators)
        or member.guild_permissions.administrator
    )


def check_bot_starting():
    def predicate(ctx: Context, *args, **kwargs):
        return not ctx.bot.starting

    return check(predicate)


def have_xp_bonus(member, bot) -> bool:
    if "boosteds" not in bot.configs[member.guild.id]["xp"]:
        return False
    return set([str(r.id) for r in member.roles]) & set(
        bot.configs[member.guild.id]["xp"]["boosteds"]
    ) or str(member.id) in set(bot.configs[member.guild.id]["xp"]["boosteds"])


def resolve_guild_path(function):
    def check(self, guild_id: int, *args, **kwargs):
        self.path = f"guilds/{str(guild_id)}/{self.innerpath}"
        return function(self, guild_id, *args, **kwargs)

    return check


def get_guild_pre(bot, arg: Union[Message, Member]) -> list:
    try:
        prefix = bot.configs[arg.guild.id]["prefix"]
    except Exception:
        prefix = "o!"

    return [prefix, prefix.lower(), prefix.upper()]


def get_embed_from_ctx(bot, ctx: Context, title: str) -> Embed:
    em = Embed(
        colour=bot.color,
        title=title,
        description=f"Use the command format `{get_guild_pre(bot, ctx.message)[0]}{ctx.command.qualified_name} <option>` to view more info about an option.",
    )

    em.set_thumbnail(url=bot.user.avatar_url)
    em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    em.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

    for cmd in ctx.command.commands:
        em.add_field(
            name=f"{cmd.brief} {cmd.name}",
            value=f"{cmd.description}"
            + (
                f"\n**Alias"
                + ("es" if len(cmd.aliases) > 1 else "")
                + "**: "
                + ", ".join([f"`{a}`" for a in cmd.aliases])
                if cmd.aliases
                else ""
            )
            + (f"\n**Usage**: `{cmd.usage}`" if cmd.usage else "")
            + (
                f"\n**Sub-commands:** {', '.join([f'`{cmd.name}`' for cmd in cmd.commands])}"
                if "all_commands" in vars(cmd).keys() and cmd.commands
                else ""
            ),
            inline=True,
        )

    return em


def duration(s: int) -> str:
    seconds = s
    minutes = floor(seconds / 60)
    hours = 0
    days = 0

    if minutes >= 60:
        hours = floor(minutes / 60)
        minutes = minutes - hours * 60

    if hours >= 24:
        days = floor(hours / 24)
        hours = hours - days * 24

    seconds = floor(seconds % 60)
    response = ""
    seperator = ""

    if days > 0:
        plurial = "s" if days > 1 else ""
        response = f"{days} day{plurial}"
        seperator = ", "
        response += f", {hours}h" if hours > 0 else ""
    elif hours > 0:
        response = f"{hours}h"
        seperator = ", "

    if (days > 0 or hours > 0) and minutes > 0:
        response += f", {minutes}m"
    elif minutes > 0:
        response = f"{minutes}m"
        seperator = ", "

    if seconds > 0:
        response += f"{seperator}{seconds}s"

    return response


async def parse_duration(
    bot, _duration: int, type_duration: to_lower, ctx: Context
) -> bool or int:
    if _duration <= 0:
        await ctx.reply(
            f"⚠️ - {ctx.author.mention} - Please provide a minimum duration greater than 0! `{get_guild_pre(bot, ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
            delete_after=15,
        )
        return False

    if type_duration == "s":
        return _duration * 1
    elif type_duration == "m":
        return _duration * 60
    elif type_duration == "h":
        return _duration * 3600
    elif type_duration == "j":
        return _duration * 86400
    else:
        await ctx.reply(
            f"⚠️ - {ctx.author.mention} - Please provide a valid duration type! `{get_guild_pre(bot, ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
            delete_after=15,
        )
        return False
