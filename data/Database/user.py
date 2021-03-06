from collections import OrderedDict
from datetime import datetime
from math import ceil

from data import Utils


class User:
    def __init__(self, model, bot) -> None:
        self.model = model
        self.innerpath = "users"
        self.bot = bot

    """ CHECKS """

    def __check_user_exists(function):
        """Checks if the user exists in the database

        Keyword arguments:
        function -- the function to be invoked after the check
        """

        def check(self, guild_id: int, user_id: int, *args, **kargs):
            if not self.model.get(f"{self.path}/{user_id}"):
                self.create_user(
                    guild_id,
                    user_id,
                    f"{self.bot.get_guild(guild_id).get_member(user_id)}",
                )
            return function(self, guild_id, user_id, *args, **kargs)

        return check

    def __check_user_level(function):
        """Checks if the user has less than the maximum server level

        Keyword arguments:
        function -- the function to be invoked after the check
        """

        def check(self, guild_id: int, user_id: int, value, *args, **kargs):
            level = self.get_user(guild_id, user_id)["level"]
            warn = False
            if (level + value) > self.bot.configs[guild_id]["xp"]["max_lvl"]:
                value = self.bot.configs[guild_id]["xp"]["max_lvl"] - level
                warn = True
            return function(self, guild_id, user_id, value, warn, *args, **kargs)

        return check

    def __check_user_level_remove(function):
        """Checks if the user has more than 1 level

        Keyword arguments:
        function -- the function to be invoked after the check
        """

        def check(self, guild_id: int, user_id: int, value, *args, **kargs):
            level = self.get_user(guild_id, user_id)["level"]
            warn = False
            if (level - value) <= 0:
                value = level - 1
                warn = True
            return function(self, guild_id, user_id, value, warn, *args, **kargs)

        return check

    def __check_user_prestige(function):
        """Checks if the user has less than the maximum server prestige

        Keyword arguments:
        function -- the function to be invoked after the check
        """

        def check(
            self,
            guild_id: int,
            user_id: int,
            value: int = 1,
            level: int = 1,
            xp: int = 0,
            warn: bool = False,
            *args,
            **kargs,
        ):
            prestige = self.get_user(guild_id, user_id)["prestige"]
            warn = False
            value = 1
            if (prestige + 1) > len(self.bot.configs[guild_id]["xp"]["prestiges"]):
                value = 0
                warn = True
            return function(
                self, guild_id, user_id, value, level, xp, warn, *args, **kargs
            )

        return check

    """ CREATION & DELETION """

    @Utils.resolve_guild_path
    def create_user(self, guild_id: int, _id: int, name: str) -> None:
        self.model.create(
            f"{self.path}/{_id}",
            args={
                "id": _id,
                "name": name,
                "muted": False,
                "xp": 0,
                "level": 1,
                "prestige": 0,
            },
        )

    @Utils.resolve_guild_path
    def update_user(self, guild_id: int, _id: int, name: str) -> None:
        self.model.update(
            f"{self.path}/{_id}",
            args={
                "name": name,
            },
        )

    """ SANCTIONS """

    @Utils.resolve_guild_path
    @__check_user_exists
    def warn_user(
        self, guild_id: int, _id: int, at: float, by: str, reason: str = None
    ) -> None:
        path = f"{self.path}/{_id}/warns"
        x = len([warn for warn in self.model.get(f"{path}")])

        self.model.create(
            f"{path}/{x}",
            args={
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_s": at,
                "by": by,
                "reason": reason,
            },
        )

    @Utils.resolve_guild_path
    @__check_user_exists
    def get_warns(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}/warns")

    @Utils.resolve_guild_path
    @__check_user_exists
    def clear_warns(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/warns")

    @Utils.resolve_guild_path
    @__check_user_exists
    def mute_user(
        self,
        guild_id: int,
        _id: int,
        _duration: int,
        at: float,
        by: str,
        reason: str = None,
    ) -> None:
        path = f"{self.path}/{_id}/mutes"
        x = len([mute for mute in self.model.get(f"{path}")])

        self.model.create(
            f"{path}/{x}",
            args={
                "duration": self.bot.utils_class.duration(_duration),
                "duration_s": _duration,
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_s": at,
                "by": by,
                "reason": reason,
            },
        )
        self.model.update(f"{self.path}/{_id}", args={"muted": True})

    @Utils.resolve_guild_path
    @__check_user_exists
    def unmute_user(self, guild_id: int, _id: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"muted": False})

    @Utils.resolve_guild_path
    @__check_user_exists
    def clear_join_mutes(self, guild_id: int, _id: int) -> None:
        db_user = self.get_user(guild_id, _id)

        if "mutes" in db_user:
            x = 0
            for mute in db_user["mutes"]:
                if "reason" in mute and mute["reason"] == "joined the server":
                    self.model.delete(f"{self.path}/{_id}/mutes/{x}")

                x += 1

    @Utils.resolve_guild_path
    @__check_user_exists
    def get_last_mute(self, guild_id: int, _id: int) -> dict:
        path = f"{self.path}/{_id}/mutes"
        mutes = [mute for mute in self.model.get(f"{path}")]
        return mutes[-1] if len(mutes) > 0 else {}

    @Utils.resolve_guild_path
    @__check_user_exists
    def ban_user(
        self, guild_id: int, _id: int, _duration, at: float, by: str, reason: str = None
    ) -> None:
        self.model.create(
            f"{self.path}/{_id}/ban",
            args={
                "duration": self.bot.utils_class.duration(_duration)
                if isinstance(_duration, int)
                else "all Eternity",
                "duration_s": _duration if isinstance(_duration, int) else "infinite",
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_s": at,
                "by": by,
                "reason": reason,
            },
        )

    @Utils.resolve_guild_path
    @__check_user_exists
    def unban_user(
        self, guild_id: int, _id: int, at: float, by: str, reason: str = None
    ) -> None:
        self.model.create(
            f"{self.path}/{_id}/unban/{int(at)}",
            args={
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_s": at,
                "by": by,
                "reason": reason,
                "original_ban": self.model.get(f"{self.path}/{_id}/ban"),
            },
        )
        self.model.delete(f"{self.path}/{_id}/ban")

    """ XP """

    @Utils.resolve_guild_path
    @__check_user_exists
    def add_xp(self, guild_id: int, _id: int, value: int) -> None:
        path = f"{self.path}/{_id}"
        xp = (self.model.get(f"{path}"))["xp"]
        self.model.update(f"{self.path}/{_id}", args={"xp": xp + value})

    @Utils.resolve_guild_path
    @__check_user_exists
    @__check_user_level
    def add_levels(
        self, guild_id: int, _id: int, value: int, warn: bool = False
    ) -> tuple:
        path = f"{self.path}/{_id}"
        level = (self.model.get(f"{path}"))["level"]
        self.model.update(f"{self.path}/{_id}", args={"level": level + value})
        return warn, value, level + value

    @Utils.resolve_guild_path
    @__check_user_exists
    @__check_user_level_remove
    def remove_levels(
        self, guild_id: int, _id: int, value: int, warn: bool = False
    ) -> tuple:
        path = f"{self.path}/{_id}"
        level = (self.model.get(f"{path}"))["level"]
        self.model.update(f"{self.path}/{_id}", args={"level": level - value})
        return warn, value, level - value

    @Utils.resolve_guild_path
    @__check_user_exists
    def set_levels(self, guild_id: int, _id: int, level: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"level": level})

    @Utils.resolve_guild_path
    @__check_user_exists
    @__check_user_prestige
    def add_prestige(
        self,
        guild_id: int,
        _id: int,
        value: int = 1,
        level: int = 1,
        xp: int = 0,
        warn: bool = False,
    ) -> bool:
        db_user = self.get_user(guild_id, _id)
        self.model.update(
            f"{self.path}/{_id}",
            args={"prestige": db_user["prestige"] + value, "level": level, "xp": xp},
        )
        return warn

    @Utils.resolve_guild_path
    @__check_user_exists
    def remove_prestige(self, guild_id: int, _id: int, xp: int, value: int = 1) -> None:
        db_user = self.get_user(guild_id, _id)
        self.model.update(
            f"{self.path}/{_id}",
            args={
                "prestige": db_user["prestige"] - value
                if db_user["prestige"] > 0
                else 0,
                "level": self.bot.configs[guild_id]["xp"]["max_lvl"],
                "xp": xp,
            },
        )

    @Utils.resolve_guild_path
    @__check_user_exists
    def prepare_prestige(self, guild_id: int, _id: int, confirmation_id: int) -> bool:
        self.model.create(
            f"{self.path}/{_id}/prestige_pending",
            args={"confirmation_id": confirmation_id},
        )

    @Utils.resolve_guild_path
    @__check_user_exists
    def cancel_prestige(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/prestige_pending")

    @Utils.resolve_guild_path
    @__check_user_exists
    def clear_xp(self, guild_id: int, _id: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"xp": 0})

    """ OTHERS """

    @Utils.resolve_guild_path
    @__check_user_exists
    def get_user(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}")

    @Utils.resolve_guild_path
    def get_users(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}")

    @Utils.resolve_guild_path
    @__check_user_exists
    def new_invite(self, guild_id: int, _id: int, at: float, content: str) -> None:
        self.model.create(
            f"{self.path}/{_id}/invit_links/{ceil(at)}",
            args={
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_s": at,
                "content": content,
            },
        )

    @Utils.resolve_guild_path
    @__check_user_exists
    def get_invites(self, guild_id: int, _id: int) -> None:
        return self.model.get(f"{self.path}/{_id}/invit_links")

    @Utils.resolve_guild_path
    @__check_user_exists
    def clear_invites(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/invit_links")

    @Utils.resolve_guild_path
    @__check_user_exists
    def get_commands_count(
        self, guild_id: int, _id: int, details: bool = False
    ) -> int or OrderedDict:
        if details:
            return self.model.get(f"{self.path}/{_id}/commands_count")

        count = 0
        commands = self.model.get(f"{self.path}/{_id}/commands_count")

        for command in commands.values():
            count += command

        return count

    @Utils.resolve_guild_path
    @__check_user_exists
    def add_messages_count(self, guild_id: int, _id: int, channel_id: int) -> None:
        counts = self.model.get(f"{self.path}/{_id}/messages_count")

        if counts:
            self.model.update(
                f"{self.path}/{_id}/messages_count",
                args={
                    **{
                        channel_id: (
                            counts.pop(str(channel_id))
                            if str(channel_id) in counts
                            else 0
                        )
                        + 1
                    },
                    **counts,
                },
            )
        else:
            self.model.create(f"{self.path}/{_id}/messages_count", args={channel_id: 1})

    @Utils.resolve_guild_path
    @__check_user_exists
    def add_command_count(self, guild_id: int, _id: int, command: str) -> None:
        counts = self.model.get(f"{self.path}/{_id}/commands_count")

        if counts:
            self.model.update(
                f"{self.path}/{_id}/commands_count",
                args={
                    **{command: (counts.pop(command) if command in counts else 0) + 1},
                    **counts,
                },
            )
        else:
            self.model.create(f"{self.path}/{_id}/commands_count", args={command: 1})

    @Utils.resolve_guild_path
    @__check_user_exists
    def add_voice_time(
        self, guild_id: int, _id: int, channel_id: int, value: int = 1
    ) -> None:
        counts = self.model.get(f"{self.path}/{_id}/voice_count")

        if counts:
            self.model.update(
                f"{self.path}/{_id}/voice_count",
                args={
                    **{
                        channel_id: (
                            counts.pop(str(channel_id))
                            if str(channel_id) in counts
                            else 0
                        )
                        + value
                    },
                    **counts,
                },
            )
        else:
            self.model.create(
                f"{self.path}/{_id}/voice_count", args={channel_id: value}
            )
