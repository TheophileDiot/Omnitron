from typing import Union, OrderedDict

from data.utils import resolve_guild_path


class Config:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = "config"

    """ GUILD MODERATORS """

    @resolve_guild_path
    def add_moderator(
        self, guild_id: int, mod_id: int, mod_name: str, mod_type: str
    ) -> None:
        self.model.create(
            f"{self.path}/moderators/{mod_id}",
            args={"name": mod_name, "type": mod_type},
        )

    @resolve_guild_path
    def remove_moderator(self, guild_id: int, mod_id: int) -> None:
        self.model.delete(f"{self.path}/moderators/{mod_id}")

    @resolve_guild_path
    def purge_moderator(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/moderators")

    @resolve_guild_path
    def get_moderators(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/moderators")

    """ PREFIX """

    @resolve_guild_path
    def set_prefix(self, guild_id: int, prefix: str = "o!") -> None:
        self.model.update(f"{self.path}", args={"prefix": prefix})

    @resolve_guild_path
    def get_prefix(self, guild_id: int) -> str:
        return self.model.get(f"{self.path}/prefix") or "o!"

    """ XP """

    @resolve_guild_path
    def set_xp(self, guild_id: int, val: bool) -> None:
        self.model.update(f"{self.path}/xp", args={"is_on": val})

    @resolve_guild_path
    def set_xp_max_lvl(self, guild_id: int, val: int) -> None:
        self.model.update(f"{self.path}/xp", args={"max_lvl": val})

    @resolve_guild_path
    def set_xp_notify_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.update(f"{self.path}/xp", args={"notify_channel": channel_id})

    @resolve_guild_path
    def get_xp(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp")

    @resolve_guild_path
    def add_xp_boosted(
        self,
        guild_id: int,
        boosted_id: int,
        boosted_name: str,
        bonus: int,
        boosted_type: str,
    ) -> None:
        self.model.create(
            f"{self.path}/xp/boosteds/{boosted_id}",
            args={"name": boosted_name, "bonus": bonus, "type": boosted_type},
        )

    @resolve_guild_path
    def get_xp_boosted(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/boosteds")

    @resolve_guild_path
    def remove_xp_boosted(self, guild_id: int, boosted_id: int) -> None:
        self.model.delete(f"{self.path}/xp/boosteds/{boosted_id}")

    @resolve_guild_path
    def purge_xp_boosted(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/boosteds")

    @resolve_guild_path
    def add_xp_lvl2role(
        self, guild_id: int, level: int, role_name: str, role_id: int
    ) -> None:
        self.model.create(
            f"{self.path}/xp/lvl2role/{level}",
            args={"name": role_name, "role_id": role_id},
        )

    @resolve_guild_path
    def get_xp_lvl2role(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/lvl2role")

    @resolve_guild_path
    def remove_xp_lvl2role(self, guild_id: int, level: int) -> None:
        self.model.delete(f"{self.path}/xp/lvl2role/{level}")

    @resolve_guild_path
    def purge_xp_lvl2role(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/lvl2role")

    @resolve_guild_path
    def add_xp_prestiges(
        self, guild_id: int, prestige: str, role_name: str, role_id: int
    ) -> None:
        self.model.create(
            f"{self.path}/xp/prestiges/{prestige}",
            args={"name": role_name, "role_id": role_id},
        )

    @resolve_guild_path
    def get_xp_prestiges(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/prestiges")

    @resolve_guild_path
    def remove_xp_prestiges(self, guild_id: int) -> None:
        self.model.delete(
            f"{self.path}/xp/prestiges/p_{len(self.get_xp_prestiges(guild_id))}"
        )

    @resolve_guild_path
    def purge_xp_prestiges(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/prestiges")

    """ INVIT PREVENTION """

    @resolve_guild_path
    def set_invit_prevention(
        self, guild_id: int, val: bool, channel_id: Union[int, None]
    ) -> None:
        self.model.update(
            f"{self.path}/prevent_invites", args={"notify_channel_id": channel_id}
        )

    @resolve_guild_path
    def remove_invit_prevention(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/prevent_invites")

    @resolve_guild_path
    def get_invit_prevention(self, guild_id: int) -> bool:
        return self.model.get(f"{self.path}/prevent_invites") or False

    """ MUTE ON JOIN """

    @resolve_guild_path
    def set_mute_on_join(
        self, guild_id: int, duration: float, role_id: int, channel_id: Union[int, None]
    ) -> None:
        self.model.update(
            f"{self.path}/mute_on_join",
            args={
                "duration": duration,
                "muted_role_id": role_id,
                "notify_channel_id": channel_id,
            },
        )

    @resolve_guild_path
    def remove_mute_on_join(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/mute_on_join")

    @resolve_guild_path
    def get_mute_on_join(self, guild_id: int) -> bool:
        return self.model.get(f"{self.path}/mute_on_join") or None
