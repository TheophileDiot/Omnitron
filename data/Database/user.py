from collections import OrderedDict
from data.utils import duration, to_lower
from datetime import datetime
from math import ceil

from data.utils import resolve_guild_path


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

    @resolve_guild_path
    def create_user(self, guild_id: int, _id: int, name: str) -> None:
        self.model.create(
            f"{self.path}/{_id}",
            args={
                "name": name,
                "muted": False,
                "identified": False,
                "xp": 0,
                "level": 1,
                "prestige": 0,
            },
        )

    @resolve_guild_path
    def delete_user(self, guild_id: int, _id: int) -> None:
        # self.model.delete(f"logs/xp/{_id}")
        # self.model.delete(f"logs/level/{_id}")
        # self.model.delete(f"logs/prestige/{_id}")
        self.model.delete(f"{self.path}/{_id}")

    """ SANCTIONS """

    @resolve_guild_path
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
                "at_ms": at,
                "by": by,
                "reason": reason,
            },
        )

    @resolve_guild_path
    @__check_user_exists
    def get_warns(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}/warns")

    @resolve_guild_path
    @__check_user_exists
    def clear_warns(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/warns")

    @resolve_guild_path
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
                "duration": duration(_duration),
                "duration_s": _duration,
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_ms": at,
                "by": by,
                "reason": reason,
            },
        )
        self.model.update(f"{self.path}/{_id}", args={"muted": True})

    @resolve_guild_path
    @__check_user_exists
    def unmute_user(self, guild_id: int, _id: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"muted": False})

    @resolve_guild_path
    @__check_user_exists
    def clear_mutes(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/mutes")

    @resolve_guild_path
    @__check_user_exists
    def get_last_mute(self, guild_id: int, _id: int) -> dict:
        path = f"{self.path}/{_id}/mutes"
        mutes = [mute for mute in self.model.get(f"{path}")]
        return mutes[-1] if len(mutes) > 0 else {}

    @resolve_guild_path
    @__check_user_exists
    def ban_user(
        self, guild_id: int, _id: int, _duration, at: float, by: str, reason: str = None
    ) -> None:
        self.model.create(
            f"logs/ban/{_id}",
            args={
                "id": _id,
                "duration": duration(_duration)
                if isinstance(_duration, int)
                else "all Eternity",
                "duration_s": _duration if isinstance(_duration, int) else "infinite",
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_ms": at,
                "by": by,
                "reason": reason,
                "still": True,
            },
        )

    @resolve_guild_path
    @__check_user_exists
    def unban_user(
        self, guild_id: int, _id: int, at: float, by: str, reason: str = None
    ) -> None:
        self.model.update(f"logs/ban/{_id}", args={"still": False})
        self.model.create(
            f"logs/unban/{_id}",
            args={
                "id": _id,
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_ms": at,
                "by": by,
                "reason": reason,
            },
        )

    @resolve_guild_path
    @__check_user_exists
    def kick_user(
        self, guild_id: int, _id: int, at: float, by: str, reason: str = None
    ) -> None:
        self.model.create(
            f"logs/kick/{_id}",
            args={
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_ms": at,
                "by": by,
                "reason": reason,
            },
        )

    """ XP """

    @resolve_guild_path
    @__check_user_exists
    def add_xp(self, guild_id: int, _id: int, value: int) -> None:
        path = f"{self.path}/{_id}"
        xp = (self.model.get(f"{path}"))["xp"]
        self.model.update(f"{self.path}/{_id}", args={"xp": xp + value})

    @resolve_guild_path
    @__check_user_exists
    @__check_user_level
    def add_levels(
        self, guild_id: int, _id: int, value: int, warn: bool = False
    ) -> tuple:
        path = f"{self.path}/{_id}"
        level = (self.model.get(f"{path}"))["level"]
        self.model.update(f"{self.path}/{_id}", args={"level": level + value})
        return (warn, value, level + value)

    @resolve_guild_path
    @__check_user_exists
    @__check_user_level_remove
    def remove_levels(
        self, guild_id: int, _id: int, value: int, warn: bool = False
    ) -> tuple:
        path = f"{self.path}/{_id}"
        level = (self.model.get(f"{path}"))["level"]
        self.model.update(f"{self.path}/{_id}", args={"level": level - value})
        return (warn, value, level - value)

    @resolve_guild_path
    @__check_user_exists
    def set_levels(self, guild_id: int, _id: int, level: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"level": level})

    @resolve_guild_path
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

    @resolve_guild_path
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

    @resolve_guild_path
    @__check_user_exists
    def prepare_prestige(self, guild_id: int, _id: int, confirmation_id: int) -> bool:
        self.model.create(
            f"{self.path}/{_id}/prestige_pending",
            args={"confirmation_id": confirmation_id},
        )

    @resolve_guild_path
    @__check_user_exists
    def cancel_prestige(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/prestige_pending")

    @resolve_guild_path
    @__check_user_exists
    def clear_xp(self, guild_id: int, _id: int) -> None:
        self.model.update(f"{self.path}/{_id}", args={"xp": 0})

    """ OTHERS """

    @resolve_guild_path
    @__check_user_exists
    def set_identification(self, guild_id: int, _id: int, value: bool = False) -> None:
        self.model.update(f"{self.path}/{_id}", args={"identified": value})

    @resolve_guild_path
    @__check_user_exists
    def get_user(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}")

    @resolve_guild_path
    def get_users(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}")

    @resolve_guild_path
    @__check_user_exists
    def new_invite(self, guild_id: int, _id: int, at: float, content: str) -> None:
        self.model.create(
            f"{self.path}/{_id}/invit_links/{ceil(at)}",
            args={
                "at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "at_ms": at,
                "content": content,
            },
        )

    @resolve_guild_path
    @__check_user_exists
    def get_invites(self, guild_id: int, _id: int) -> None:
        return self.model.get(f"{self.path}/{_id}/invit_links")

    @resolve_guild_path
    @__check_user_exists
    def clear_invites(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}/invit_links")

    @resolve_guild_path
    @__check_user_exists
    def set_game_score(
        self, guild_id: int, _id: int, game: to_lower, score: int
    ) -> None:
        self.model.create(f"{self.path}/{_id}/games", args={game: score})

    @resolve_guild_path
    @__check_user_exists
    def get_game_score(self, guild_id: int, _id: int, game: to_lower) -> int:
        return self.model.get(f"{self.path}/{_id}/games/{game}") or 0
