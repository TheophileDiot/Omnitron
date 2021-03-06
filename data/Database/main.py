from collections import OrderedDict
from typing import Optional

from data import Utils


class Main:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = ""

    """ CREATE & DELETE """

    @Utils.resolve_guild_path
    def create_guild(
        self, guild_id: int, guild_name: str, guild_owner: str, present: bool = True
    ) -> None:
        self.model.create(
            self.path,
            args={"name": guild_name, "owner": guild_owner, "present": present},
        )
        self.model.create(
            f"{self.path}/config",
            args={"prefix": "o!", "xp": {"is_on": False, "max_lvl": 100}},
        )

    @Utils.resolve_guild_path
    def kicked_from_guild(self, guild_id: int, present: bool = False) -> None:
        self.model.update(self.path, args={"present": present})

    """ GETTERS & SETTERS """

    @Utils.resolve_guild_path
    def get_guild(self, guild_id: int) -> Optional[OrderedDict]:
        return self.model.get(self.path) or None

    def get_guilds(self) -> OrderedDict:
        return self.model.get("guilds/")

    @Utils.resolve_guild_path
    def update_guild(self, guild_id: int, updates: dict) -> None:
        self.model.update(self.path, args=updates)
