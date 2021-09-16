# -----------------------------------------------------------
# A discord bot that has every features you want in a discord server !
#
# (C) 2021 TheophileDiot
# Released under MIT License (MIT)
# email theophile.diot900@gmail.com
# linting: black
# -----------------------------------------------------------
from asyncio import get_event_loop
from datetime import date
from itertools import chain
from logging import basicConfig, DEBUG, error, info
from multiprocessing import Process
from os import getenv, listdir, makedirs, name, path, system, remove
from ratelimiter import RateLimiter
from subprocess import PIPE, call
from time import time
from sys import exc_info
from traceback import format_exc

from aiohttp import ClientSession
from discord import Colour, Forbidden, Intents, Message
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import (
    BotMissingPermissions,
    BadArgument,
    BadUnionArgument,
    CheckFailure,
    CommandOnCooldown,
    MaxConcurrencyReached,
    MissingAnyRole,
    MissingRequiredArgument,
    MissingPermissions,
    NotOwner,
)
from dislash import InteractionClient
from dotenv import load_dotenv


async def limited(until):
    return int(round(until - time()))


class Omnitron(Bot):
    def __init__(self, **kwargs):
        """Initialize the bot"""
        super().__init__(
            command_prefix=Utils.get_guild_pre or BOT_PREFIX,
            intents=self.get_intents(),
            help_command=None,
            case_insensitive=True,
            case_insensitive_prefix=True,
            strip_after_prefix=True,
            self_bot=False,
            **kwargs,
        )

        [remove(f) for f in listdir(".") if f.startswith("hs_err_pid")]
        [remove(path.join("temp", "musics", f)) for f in listdir("temp/musics")]

        with open(path.join("logs", "spring.log"), "w"):
            pass

        with open(path.join("temp", "musics.txt"), "w"):
            pass

        dirs = chain.from_iterable(
            [
                [
                    f"{f}.{_f.replace('.py', '')}"
                    if path.isfile(path.join("cogs", f, _f))
                    else f"{f}.{_f}"
                    for _f in listdir(path.join("cogs", f))
                    if _f not in "__pycache__"
                ]
                for f in listdir("cogs")
                if path.isdir(path.join("cogs", f))
                and f not in ("__init__", "__pycache__")
            ]
        )
        self._extensions = [f for f in dirs]
        self.load_extensions()
        self.session = ClientSession(loop=self.loop)
        self.limiter = RateLimiter(max_calls=1, period=1, callback=limited)

        self.starting = True
        self.model = Model.setup()
        self.last_check = None

        self.utils_class = Utils(self)
        self.main_repo = Main(self.model)
        self.config_repo = Config(self.model)
        self.poll_repo = Poll(self.model)
        self.ticket_repo = Ticket(self.model)
        self.user_repo = User(self.model, self)
        print("Database successfully initialized.")
        info("Database loaded")

        self.configs = {}
        self.moderators = {}
        self.djs = {}
        self.playlists = {}
        self.tasks = {}

        process = Process(target=self.start_lavalink)
        process.start()  # start the process
        print("Lavalink successfully initialized.")
        info("Lavalink started")

        self.color = Colour(BOT_COLOR) or self.user.color
        InteractionClient(self)

    """ EVENTS """

    async def on_command_error(self, ctx: Context, _error):
        """Override default command error handler to log errors and prevent the bot from crashing."""
        if isinstance(_error, MissingRequiredArgument):
            resp = f"ℹ️ - The `{ctx.command.qualified_name}` command is missing an argument! Missing parameter: `{_error.param.name}`. `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help."
        elif isinstance(_error, MissingPermissions):
            resp = f"⛔ - You do not have the necessary perms to run this command! Required perms: `{', '.join(_error.missing_perms)}`"
        elif isinstance(_error, MissingAnyRole):
            resp = f"⛔ - You do not have one of the required roles to run this command! One of these roles is required: `{', '.join(_error.missing_roles)}`"
        elif isinstance(_error, NotOwner):
            resp = f"⛔ - The `{ctx.command.qualified_name}` command is reserved for the bot owner!"
        elif isinstance(_error, BotMissingPermissions):
            resp = f"⛔ - I don't have the necessary perms to run this command! Required perms: `{', '.join(_error.missing_perms)}`"
        elif isinstance(_error, CommandOnCooldown):
            resp = f"ℹ️ - The `{ctx.command.qualified_name}`command is currently in cooldown, please try again in `{'%.2f' % _error.retry_after}` seconds, this command can be used `{_error.cooldown.rate}` times every `{_error.cooldown.per}` seconds."
        elif isinstance(_error, MaxConcurrencyReached):
            resp = f"ℹ️ - The `{ctx.command.qualified_name}` command has too many executions in progress (`{_error.number}` executions), please try again in a few seconds, this command can only be used a maximum of `{_error.number}` times simultaneously."
        elif isinstance(_error, BadArgument):
            resp = f"⚠️ - Please provide valid arguments! `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help."
        elif isinstance(_error, BadUnionArgument):
            resp = f"⚠️ - Please provide valid arguments! The argument `{_error.param.name}` should be within these types: ({', '.join([f'`{c.__name__}`' for c in _error.converters])})! `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help."
        elif isinstance(_error, CheckFailure):
            if self.last_check == "moderator":
                resp = f"⛔ - {ctx.author.mention} - You must be moderator of this server to use this command!"
            elif self.last_check == "dj":
                resp = f"⛔ - {ctx.author.mention} - You must be a dj in this server to use this command!"
            else:
                raise _error

            self.last_check = None
        else:
            raise _error.original

        try:
            await ctx.reply(resp, delete_after=20)
        except Forbidden as f:
            f.text = f"⚠️ - I don't have the right permissions to send messages in the channel {ctx.channel.mention} (message (replying to {ctx.author}): `{resp}`)!"
            raise

    async def on_error(self, event, *args, **kwargs):
        error(format_exc())
        print(event)
        print(format_exc())
        _error = exc_info()[1]
        if isinstance(_error, Forbidden):
            try:
                await self.utils_class.send_message_to_mods(
                    _error.text, args[0].guild.id
                )
            except AttributeError:
                await self.utils_class.send_message_to_mods(
                    _error.text, args[0].guild_id
                )
        else:
            # Log that the bot had an error
            await (await self.fetch_user(self.owner_id)).send(
                f"{exc_info()[0]}\n{exc_info()[1]}\n{exc_info()[2]}\n\n{format_exc()}\n\nIn guild `{args[0].guild if args else 'not found'}` (ID: `{args[0].guild.id if args else 'not found'}`)"
            )

    async def on_message(self, message: Message):
        if (
            message.is_system()
            or message.author.bot
            or not message.guild
            or self.starting
        ):
            return

        prefix = self.utils_class.get_guild_pre(message)

        if message.content.lower().startswith(prefix[0].lower()):
            await self.process_commands(message)

    """ METHOD(S) """

    async def process_commands(self, message: Message):
        """This function processes the commands that the user has sent"""
        await self.wait_until_ready()
        ctx = await self.get_context(message=message)

        if ctx.command is None:
            return await ctx.reply(
                f"ℹ️ - This command doesn't exist or is deactivated! Command: `{message.content[len(self.utils_class.get_guild_pre(message)[0])::]}`",
                delete_after=15,
            )
        elif (
            "commands_channels" in self.configs[ctx.guild.id]
            and ctx.channel.id not in self.configs[ctx.guild.id]["commands_channels"]
            and not ctx.author.guild_permissions.administrator
        ):
            return await ctx.reply(
                f"⛔ - Commands are not allowed in this channel!",
                delete_after=15,
            )

        await self.invoke(ctx)

    def load_extensions(self, cogs: Context = None, path: str = "cogs."):
        """Loads the default set of extensions or a seperate one if given"""
        for extension in cogs or self._extensions:
            try:
                if extension.startswith("dj"): # TODO temporary delete dj commands due to issues with YouTube
                    continue
                self.load_extension(f"{path}{extension}")
                print(f"Loaded cog: {extension}")
            except Exception as e:
                print(f"LoadError: {extension}\n" f"{type(e).__name__}: {e}")
                error(f"LoadError: {extension}\n" f"{type(e).__name__}: {e}")
        info("All cogs loaded")

    @staticmethod
    def start_lavalink():
        """starts lavalink."""
        call(["java", "-jar", "data/Lavalink.jar"], stdout=PIPE, stderr=PIPE)

    @staticmethod
    def get_ownerid():
        """Returns the owner id."""
        return getenv("OWNER_ID") or OWNER_ID or "559057271737548810"

    @staticmethod
    def get_intents():
        """Configure the intents for the bot"""
        intents = Intents(
            guilds=True,
            members=True,
            guild_messages=True,
            guild_reactions=True,
            voice_states=True,
        )
        return intents

    @classmethod
    async def setup(self, **kwargs):
        """Setup the bot with a token from data.constants or the .env file"""
        bot = self()
        try:
            await bot.start(BOT_TOKEN or getenv("BOT_TOKEN"), **kwargs)
        except KeyboardInterrupt:
            await bot.close()


if __name__ == "__main__":
    from data import (
        Model,
        Utils,
        BOT_TOKEN,
        BOT_PREFIX,
        BOT_COLOR,
        OWNER_ID,
    )
    from data.Database import Main, Config, Poll, Ticket, User

    load_dotenv(path.join(".", ".env"))  # Load data from the .env file

    if not path.exists("logs"):  # Create logs folder if it doesn't exist
        makedirs("logs")
    if not path.exists("temp"):
        makedirs("temp")
        info("temp dir created")
    if not path.exists("temp/musics"):
        makedirs("temp/musics")
        info("temp/musics dir created")

    basicConfig(
        filename=f"logs/{date.today().strftime('%d-%m-%Y_')}app.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
        level=DEBUG,
    )  # Configure the logging

    system("cls" if name == "nt" else "clear")
    print("Omnitron is starting...")
    loop = get_event_loop()
    try:
        loop.run_until_complete(Omnitron.setup())  # Starts the bot
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
