from disnake import CategoryChannel, StageChannel
from disnake.abc import GuildChannel
from disnake.ext.commands import Cog

from bot import Omnitron
from data import Utils


class Events(Cog, name="events.on_guild_channel_delete"):
    def __init__(self, bot: Omnitron):
        self.bot = bot

    @Cog.listener()
    @Utils.check_bot_starting()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        if isinstance(channel, StageChannel):
            return

        if "commands_channels" in self.bot.configs[
            channel.guild.id
        ] and channel.id in set(
            self.bot.configs[channel.guild.id]["commands_channels"]
        ):
            self.bot.config_repo.remove_commands_channel(channel.guild.id, channel.id)
            del self.bot.configs[channel.guild.id]["commands_channels"][
                self.bot.configs[channel.guild.id]["commands_channels"].index(
                    channel.id
                )
            ]

            if not self.bot.configs[channel.guild.id]["commands_channels"]:
                del self.bot.configs[channel.guild.id]["commands_channels"]

        if "music_channels" in self.bot.configs[channel.guild.id] and channel.id in set(
            self.bot.configs[channel.guild.id]["music_channels"]
        ):
            self.bot.config_repo.remove_music_channel(channel.guild.id, channel.id)
            del self.bot.configs[channel.guild.id]["music_channels"][
                self.bot.configs[channel.guild.id]["music_channels"].index(channel.id)
            ]

            if not self.bot.configs[channel.guild.id]["music_channels"]:
                del self.bot.configs[channel.guild.id]["music_channels"]

        if "xp_gain_channels" in self.bot.configs[
            channel.guild.id
        ] and channel.id in set(
            self.bot.configs[channel.guild.id]["xp_gain_channels"][
                type(channel).__name__
            ]
        ):
            self.bot.config_repo.remove_xp_gain_channel(channel.guild.id, channel.id)
            del self.bot.configs[channel.guild.id]["xp_gain_channels"][
                self.bot.configs[channel.guild.id]["xp_gain_channels"].index(channel.id)
            ]

            if not self.bot.configs[channel.guild.id]["xp_gain_channels"][
                type(channel).__name__
            ]:
                del self.bot.configs[channel.guild.id]["xp_gain_channels"][
                    type(channel).__name__
                ]

            if not self.bot.configs[channel.guild.id]["xp_gain_channels"]:
                del self.bot.configs[channel.guild.id]["xp_gain_channels"]

        if (
            "notify_channel" in self.bot.configs[channel.guild.id]["xp"]
            and self.bot.configs[channel.guild.id]["xp"]["notify_channel"] == channel
        ):
            self.bot.config_repo.set_xp_notify_channel(channel.guild.id, None)
            del self.bot.configs[channel.guild.id]["xp"]["notify_channel"]

        if (
            "polls_channel" in self.bot.configs[channel.guild.id]
            and self.bot.configs[channel.guild.id]["polls_channel"] == channel
        ):
            self.bot.config_repo.set_polls_channel(channel.guild.id, None)
            del self.bot.configs[channel.guild.id]["polls_channel"]

            polls = self.bot.poll_repo.get_polls(channel.guild.id)
            if len(polls) > 1 or polls and "old" not in polls:
                for poll in polls:
                    if poll == "old":
                        continue

                    self.bot.poll_repo.erase_poll(channel.guild.id, poll)
                    self.bot.configs[channel.guild.id]["polls"][int(poll)].cancel()
                    del self.bot.configs[channel.guild.id]["polls"][int(poll)]

        if (
            "select2role" in self.bot.configs[channel.guild.id]
            and "channel" in self.bot.configs[channel.guild.id]["select2role"]
            and self.bot.configs[channel.guild.id]["select2role"]["channel"] == channel
        ):
            self.bot.config_repo.set_select2role_channel(channel.guild.id, None)
            del self.bot.configs[channel.guild.id]["select2role"]["channel"]
            del self.bot.configs[channel.guild.id]["select2role"]["roles_msg"]

        if "tickets" in self.bot.configs[channel.guild.id] and (
            (
                "tickets_channel" in self.bot.configs[channel.guild.id]["tickets"]
                and self.bot.configs[channel.guild.id]["tickets"]["tickets_channel"]
                == channel
            )
            or (
                "tickets_category" in self.bot.configs[channel.guild.id]["tickets"]
                and self.bot.configs[channel.guild.id]["tickets"]["tickets_category"]
                == channel
            )
        ):
            self.bot.config_repo.remove_tickets(channel.guild.id)
            del self.bot.configs[channel.guild.id]["tickets"]

            if isinstance(channel, CategoryChannel):
                self.bot.ticket_repo.purge_tickets(channel.guild.id)

        if (
            "prevent_invites" in self.bot.configs[channel.guild.id]
            and "notify_channel"
            in self.bot.configs[channel.guild.id]["prevent_invites"]
            and self.bot.configs[channel.guild.id]["prevent_invites"]["notify_channel"]
            == channel
        ):
            self.bot.config_repo.set_invite_prevention(channel.guild.id, None)
            del self.bot.configs[channel.guild.id]["prevent_invites"]["notify_channel"]

        if (
            "mute_on_join" in self.bot.configs[channel.guild.id]
            and "notify_channel" in self.bot.configs[channel.guild.id]["mute_on_join"]
            and self.bot.configs[channel.guild.id]["mute_on_join"]["notify_channel"]
            == channel
        ):
            self.bot.config_repo.set_mute_on_join(
                channel.guild.id,
                self.bot.configs[channel.guild.id]["mute_on_join"]["duration"],
                None,
            )
            del self.bot.configs[channel.guild.id]["mute_on_join"]["notify_channel"]

        if (
            "mods_channel" in self.bot.configs[channel.guild.id]
            and self.bot.configs[channel.guild.id]["mods_channel"] == channel
        ):
            self.bot.config_repo.set_mods_channel(channel.guild.id, None)
            del self.bot.configs[channel.guild.id]["mods_channel"]


def setup(bot: Omnitron):
    bot.add_cog(Events(bot))
