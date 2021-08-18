from collections import OrderedDict

from data.utils import resolve_guild_path


class Main:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = ""

    """ CREATE & DELETE """

    @resolve_guild_path
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

    @resolve_guild_path
    def kicked_from_guild(self, guild_id: int, present: bool = False) -> None:
        self.model.update(self.path, args={"present": present})

    """ GETTERS & SETTERS """

    @resolve_guild_path
    def get_guild(self, guild_id: int) -> OrderedDict or None:
        return self.model.get(self.path) or None

    def get_guilds(self) -> OrderedDict:
        return self.model.get("guilds/")

    @resolve_guild_path
    def update_guild(self, guild_id: int, updates: dict) -> None:
        self.model.update(self.path, args=updates)
