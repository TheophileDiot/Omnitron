# -----------------------------------------------------------
# A discord bot that has every features you want in a discord server !
#
# (C) 2021 TheophileDiot
# Released under MIT License (MIT)
# email theophile.diot900@gmail.com
# linting: black
# -----------------------------------------------------------
from aiohttp import ClientSession
from asyncio import get_event_loop
from datetime import date
from discord import Intents, Colour, Member, Message
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import (
    MissingRequiredArgument,
    MissingPermissions,
    BotMissingPermissions,
    CommandOnCooldown,
    BadArgument,
    NotOwner,
    MissingAnyRole,
    MaxConcurrencyReached,
    BadUnionArgument,
    CheckFailure,
)
from dotenv import load_dotenv
from itertools import chain
from logging import basicConfig, INFO, error, info
from os import getenv, listdir, makedirs, name, path, system
from traceback import format_exc


class Omnitron(Bot):
    def __init__(self, **kwargs):
        """Initialize the bot"""
        super().__init__(
            command_prefix=Utils.get_guild_pre or BOT_PREFIX,
            intents=self.get_intents(),
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
            self_bot=False,
            **kwargs,
        )
        dirs = chain.from_iterable(
            [
                [
                    f"{f}.{_f.replace('.py', '')}"
                    for _f in listdir(path.join("cogs", f))
                    if path.isfile(path.join("cogs", f, _f))
                ]
                for f in listdir("cogs")
                if path.isdir(path.join("cogs", f))
                and f not in ("__init__", "__pycache__")
            ]
        )
        self._extensions = [f for f in dirs]
        self.load_extensions()
        self.session = ClientSession(loop=self.loop)

    """ EVENTS """

    async def on_connect(self):
        """Connect DB before bot is ready to assure that no calls are made before its ready"""
        self.starting = True
        self.model = Model.setup()
        await self.init()
        print("Database successfully initialized.")
        info("Database loaded")

    async def on_ready(self):
        self.color = Colour(BOT_COLOR) or self.user.color
        print("Omnitron is ready.")
        info("Omnitron successfully started")

    async def on_command_error(self, ctx: Context, _error):
        """Override default command error handler to log errors and prevent the bot from crashing."""
        if isinstance(_error, MissingRequiredArgument):
            await ctx.reply(
                f"ℹ️ - The `{ctx.command.qualified_name}` command is missing an argument! Missing parameter: `{_error.param.name}`. `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=20,
            )
        elif isinstance(_error, MissingPermissions):
            await ctx.reply(
                f"⛔ - You do not have the necessary perms to run this command! Required perms: `{', '.join(_error.missing_perms)}`",
                delete_after=20,
            )
        elif isinstance(_error, MissingAnyRole):
            await ctx.reply(
                f"⛔ - You do not have one of the required roles to run this command! One of these roles is required: `{', '.join(_error.missing_roles)}`",
                delete_after=20,
            )
        elif isinstance(_error, NotOwner):
            await ctx.reply(
                f"⛔ - The `{ctx.command.qualified_name}` command is reserved for the bot owner!",
                delete_after=20,
            )
        elif isinstance(_error, BotMissingPermissions):
            await ctx.reply(
                f"⛔ - I don't have the necessary perms to run this command! Required perms: `{', '.join(_error.missing_perms)}`",
                delete_after=20,
            )
        elif isinstance(_error, CommandOnCooldown):
            await ctx.reply(
                f"ℹ️ - The `{ctx.command.qualified_name}`command is currently in cooldown, please try again in `{'%.2f' % _error.retry_after}` seconds, this command can be used `{_error.cooldown.rate}` times every `{_error.cooldown.per}` seconds.",
                delete_after=20,
            )
        elif isinstance(_error, MaxConcurrencyReached):
            await ctx.reply(
                f"ℹ️ - The `{ctx.command.qualified_name}` command has too many executions in progress (`{_error.number}` executions), please try again in a few seconds, this command can only be used a maximum of `{_error.number}` times simultaneously.",
                delete_after=20,
            )
        elif isinstance(_error, BadArgument):
            await ctx.reply(
                f"⚠️ - Please provide valid arguments! `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=20,
            )
        elif isinstance(_error, BadUnionArgument):
            await ctx.reply(
                f"⚠️ - Please provide valid arguments! The argument `{_error.param.name}` should be within these types: ({', '.join([f'`{c.__name__}`' for c in _error.converters])})! `{self.utils_class.get_guild_pre(ctx.message)[0]}{f'{ctx.command.parents[0]}' if ctx.command.parents else f'help {ctx.command.qualified_name}'}` to get more help.",
                delete_after=20,
            )
        elif isinstance(_error, CheckFailure):
            if self.last_check == "moderator":
                await ctx.reply(
                    f"⛔ - {ctx.author.mention} - You must be moderator of this server to use this command!",
                    delete_after=15,
                )
            else:
                raise _error
        else:
            print(f"{type(_error)} {_error}")
            print(format_exc())
            await ctx.reply(
                content=f"❌ - An error occurred with the command `{ctx.command.qualified_name}`! Please contact a server administrator, error type: `{type(_error)}`",
                delete_after=60,
            )
            raise _error

    async def on_error(self, event, *args, **kwargs):
        # Log that the bot had an error
        error(format_exc())
        print(event)
        print(format_exc())
        if args:
            message = args[0]  # Gets the message object
            # send the message to the channel
            if isinstance(message, Member):
                return await message.send(
                    f"An error occured! Please contact server administrator",
                    delete_after=20,
                )
            await message.channel.send(
                f"An error occured! Please contact server administrator",
                delete_after=20,
            )

    async def on_message(self, message: Message):
        if message.is_system() or message.author.bot or not message.guild:
            return

        try:
            prefix = self.utils_class.get_guild_pre(message)
            has_prefix = message.content[: len(prefix[0])] in prefix
        except Exception:
            return

        if has_prefix:
            await self.process_commands(message, prefix)

    """ METHOD(S) """

    async def process_commands(self, message: Message, prefix: str):
        """This function processes the commands that the user has sent"""
        await self.wait_until_ready()
        ctx = await self.get_context(message=message)

        if ctx.command is None:
            return await ctx.reply(
                f"ℹ️ - This command doesn't exist or is deactivated! Command: `{message.content[len(prefix) - 1::]}`",
                delete_after=15,
            )

        await self.invoke(ctx)

    async def init(self):
        """When the bot is starting, init the database methods"""
        self.utils_class = Utils(self)
        self.main_repo = Main(self.model)
        self.config_repo = Config(self.model)
        self.user_repo = User(self.model, self)
        self.configs = {}
        self.moderators = {}

    def load_extensions(self, cogs: Context = None, path: str = "cogs."):
        """Loads the default set of extensions or a seperate one if given"""
        for extension in cogs or self._extensions:
            try:
                self.load_extension(f"{path}{extension}")
                print(f"Loaded cog: {extension}")
            except Exception as e:
                print(f"LoadError: {extension}\n" f"{type(e).__name__}: {e}")
                error(f"LoadError: {extension}\n" f"{type(e).__name__}: {e}")
        info("All cogs loaded")

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
    from data.Database import Main, Config, User

    load_dotenv(path.join(".", ".env"))  # Load data from the .env file

    if not path.exists("logs"):  # Create logs folder if it doesn't exist
        makedirs("logs")

    basicConfig(
        filename=f"logs/{date.today().strftime('%d-%m-%Y_')}app.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
        level=INFO,
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
