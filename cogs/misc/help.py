from collections import OrderedDict
from discord import Embed
from discord.ext.commands import Cog, command, Context, Group

from bot import Omnitron
from data import Utils


class Miscellaneous(Cog):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @command(
        name="help",
        aliases=["h", "halp"],
        usage="(command)",
        description="Show every bot's command or infos about a specific one",
    )
    async def help_command(
        self, ctx: Context, _command: Utils.to_lower = None, *args: Utils.to_lower
    ):
        em = Embed(colour=self.bot.color)

        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        em.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)

        if _command:
            if _command in self.bot.all_commands.keys():
                _command = self.bot.all_commands[_command]

                if isinstance(_command, Group) and _command.all_commands and args:
                    for arg in args:
                        if isinstance(_command, Group) and _command.all_commands:
                            try:
                                _command = _command.all_commands[arg]
                            except KeyError:
                                return await ctx.reply(
                                    f"⛔ - {ctx.author.mention} - This command isn't available! command: `{_command.qualified_name} {arg}`! `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}help {_command.qualified_name}` to get more help.",
                                    delete_after=20,
                                )

                em.description = (
                    f"The bot prefix is: `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`\n\n"
                    + f"**Command:** {_command.qualified_name.lower()}\n"
                    + f"**Description:** {_command.description or 'No description.'}\n"
                    + f"**Usage:** {f'{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`{_command.qualified_name}` ' + ' '.join([f'`{u}`' for u in _command.usage.split(' ')]) if _command.usage else 'No usage.'}\n"
                    + f"**Aliases:** {', '.join([f'`{c}`' for c in _command.aliases]) if _command.aliases else 'None.'}"
                )

                em.description += (
                    f"\n**Emoji:** {_command.brief}" if _command.brief else ""
                )
                em.description += (
                    f"\n**Sub-commands:** {', '.join([f'`{cmd.name}`' for cmd in _command.commands])}"
                    if isinstance(_command, Group) and _command.commands
                    else ""
                )
                em.description += "\n**Hidden command**" if _command.hidden else ""
            else:
                return await ctx.reply(
                    f"⛔ - {ctx.author.mention} - This command isn't available! command: `{_command}`",
                    delete_after=20,
                )
        else:
            em.description = f"Here are all the available commands for {ctx.guild.me.display_name}\nThe bot prefix is: `{self.bot.utils_class.get_guild_pre(ctx.message)[0]}`"

            cogs = OrderedDict(
                sorted(
                    {cog: [] for cog in set(self.bot.cogs) if cog != "Events"}.items()
                )
            )
            cmds = OrderedDict(
                sorted(
                    {
                        c.name: {"cog_name": c.cog_name, "hidden": c.hidden}
                        for c in set(self.bot.commands)
                    }.items()
                )
            )

            for k, v in cmds.items():
                cogs[v["cog_name"]].append([k, v])

            for cog, cmds in cogs.items():
                if cog == "Events":
                    continue
                em.add_field(
                    name=cog,
                    value=" ".join(
                        ["`" + cmd[0] + "`" for cmd in cmds if not cmd[1]["hidden"]]
                    )
                    or "**No commands**",
                    inline=False,
                )

        await ctx.send(content=None, embed=em)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
