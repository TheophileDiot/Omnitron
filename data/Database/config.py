from collections import OrderedDict
from typing import Union

from data import Utils


class Config:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = "config"

    """ GUILD MODERATORS """

    @Utils.resolve_guild_path
    def add_moderator(
        self, guild_id: int, mod_id: int, mod_name: str, mod_type: str
    ) -> None:
        self.model.create(
            f"{self.path}/moderators/{mod_id}",
            args={"name": mod_name, "type": mod_type},
        )

    @Utils.resolve_guild_path
    def remove_moderator(self, guild_id: int, mod_id: int) -> None:
        self.model.delete(f"{self.path}/moderators/{mod_id}")

    @Utils.resolve_guild_path
    def purge_moderators(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/moderators")

    @Utils.resolve_guild_path
    def get_moderators(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/moderators")

    """ GUILD DJS """

    @Utils.resolve_guild_path
    def add_dj(self, guild_id: int, dj_id: int, dj_name: str, dj_type: str) -> None:
        self.model.create(
            f"{self.path}/djs/{dj_id}",
            args={"name": dj_name, "type": dj_type},
        )

    @Utils.resolve_guild_path
    def remove_dj(self, guild_id: int, dj_id: int) -> None:
        self.model.delete(f"{self.path}/djs/{dj_id}")

    @Utils.resolve_guild_path
    def purge_djs(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/djs")

    @Utils.resolve_guild_path
    def get_djs(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/djs")

    """ GUILD COMMANDS CHANNELS """

    @Utils.resolve_guild_path
    def add_commands_channel(
        self, guild_id: int, channel_id: int, channel_name: str
    ) -> None:
        self.model.create(
            f"{self.path}/commands_channels/{channel_id}",
            args={"name": channel_name},
        )

    @Utils.resolve_guild_path
    def remove_commands_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.delete(f"{self.path}/commands_channels/{channel_id}")

    @Utils.resolve_guild_path
    def purge_commands_channels(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/commands_channels")

    @Utils.resolve_guild_path
    def get_commands_channels(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/commands_channels")

    """ GUILD MUSIC CHANNELS """

    @Utils.resolve_guild_path
    def add_music_channel(
        self, guild_id: int, channel_id: int, channel_name: str
    ) -> None:
        self.model.create(
            f"{self.path}/music_channels/{channel_id}",
            args={"name": channel_name},
        )

    @Utils.resolve_guild_path
    def remove_music_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.delete(f"{self.path}/music_channels/{channel_id}")

    @Utils.resolve_guild_path
    def purge_music_channels(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/music_channels")

    @Utils.resolve_guild_path
    def get_music_channels(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/music_channels")

    """ GUILD XP GAIN CHANNELS """

    @Utils.resolve_guild_path
    def add_xp_gain_channel(
        self, guild_id: int, channel_id: int, channel_name: str, channel_type: str
    ) -> None:
        self.model.create(
            f"{self.path}/xp_gain_channels/{channel_id}",
            args={"name": channel_name, "type": channel_type},
        )

    @Utils.resolve_guild_path
    def remove_xp_gain_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.delete(f"{self.path}/xp_gain_channels/{channel_id}")

    @Utils.resolve_guild_path
    def purge_xp_gain_channels(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp_gain_channels")

    @Utils.resolve_guild_path
    def get_xp_gain_channels(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp_gain_channels")

    """ PREFIX """

    @Utils.resolve_guild_path
    def set_prefix(self, guild_id: int, prefix: str = "o!") -> None:
        self.model.update(f"{self.path}", args={"prefix": prefix})

    @Utils.resolve_guild_path
    def get_prefix(self, guild_id: int) -> str:
        return self.model.get(f"{self.path}/prefix") or "o!"

    """ POLLS """

    @Utils.resolve_guild_path
    def set_polls_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.update(f"{self.path}", args={"polls_channel": channel_id})

    @Utils.resolve_guild_path
    def get_polls_channel(self, guild_id: int) -> int:
        return self.model.get(f"{self.path}/polls_channel")

    """ XP """

    @Utils.resolve_guild_path
    def set_xp(self, guild_id: int, val: bool) -> None:
        self.model.update(f"{self.path}/xp", args={"is_on": val})

    @Utils.resolve_guild_path
    def set_xp_max_lvl(self, guild_id: int, val: int) -> None:
        self.model.update(f"{self.path}/xp", args={"max_lvl": val})

    @Utils.resolve_guild_path
    def set_xp_notify_channel(self, guild_id: int, channel_id: int) -> None:
        self.model.update(f"{self.path}/xp", args={"notify_channel": channel_id})

    @Utils.resolve_guild_path
    def get_xp(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp")

    @Utils.resolve_guild_path
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

    @Utils.resolve_guild_path
    def get_xp_boosted(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/boosteds")

    @Utils.resolve_guild_path
    def remove_xp_boosted(self, guild_id: int, boosted_id: int) -> None:
        self.model.delete(f"{self.path}/xp/boosteds/{boosted_id}")

    @Utils.resolve_guild_path
    def purge_xp_boosted(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/boosteds")

    @Utils.resolve_guild_path
    def add_xp_lvl2role(
        self, guild_id: int, level: int, role_name: str, role_id: int
    ) -> None:
        self.model.create(
            f"{self.path}/xp/lvl2role/{level}",
            args={"name": role_name, "role_id": role_id},
        )

    @Utils.resolve_guild_path
    def get_xp_lvl2role(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/lvl2role")

    @Utils.resolve_guild_path
    def remove_xp_lvl2role(self, guild_id: int, level: int) -> None:
        self.model.delete(f"{self.path}/xp/lvl2role/{level}")

    @Utils.resolve_guild_path
    def purge_xp_lvl2role(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/lvl2role")

    @Utils.resolve_guild_path
    def add_xp_prestiges(
        self, guild_id: int, prestige: str, role_name: str, role_id: int
    ) -> None:
        self.model.create(
            f"{self.path}/xp/prestiges/{prestige}",
            args={"name": role_name, "role_id": role_id},
        )

    @Utils.resolve_guild_path
    def get_xp_prestiges(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/xp/prestiges")

    @Utils.resolve_guild_path
    def remove_xp_prestiges(self, guild_id: int) -> None:
        self.model.delete(
            f"{self.path}/xp/prestiges/p_{len(self.get_xp_prestiges(guild_id))}"
        )

    @Utils.resolve_guild_path
    def purge_xp_prestiges(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/xp/prestiges")

    """ INVITE PREVENTION """

    @Utils.resolve_guild_path
    def set_invite_prevention(self, guild_id: int, channel_id: int) -> None:
        self.model.update(
            f"{self.path}/prevent_invites",
            args={"notify_channel_id": channel_id, "is_on": True},
        )

    @Utils.resolve_guild_path
    def remove_invite_prevention(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/prevent_invites")

    @Utils.resolve_guild_path
    def get_invite_prevention(self, guild_id: int) -> bool:
        return self.model.get(f"{self.path}/prevent_invites") or False

    """ MUTE ON JOIN """

    @Utils.resolve_guild_path
    def set_mute_on_join(
        self, guild_id: int, duration: float, channel_id: Union[int, None]
    ) -> None:
        self.model.update(
            f"{self.path}/mute_on_join",
            args={
                "duration": duration,
                "notify_channel_id": channel_id,
            },
        )

    @Utils.resolve_guild_path
    def remove_mute_on_join(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/mute_on_join")

    @Utils.resolve_guild_path
    def get_mute_on_join(self, guild_id: int) -> bool:
        return self.model.get(f"{self.path}/mute_on_join") or None

    """ TICKETS """

    @Utils.resolve_guild_path
    def set_tickets(
        self, guild_id: int, val: bool, channel_id: int, category_id: int
    ) -> None:
        self.model.update(
            f"{self.path}/tickets",
            args={"tickets_channel_id": channel_id, "tickets_category_id": category_id},
        )

    @Utils.resolve_guild_path
    def remove_tickets(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/tickets")

    @Utils.resolve_guild_path
    def get_tickets(self, guild_id: int) -> bool:
        return self.model.get(f"{self.path}/tickets") or False

    """ SELECT TO ROLE """

    @Utils.resolve_guild_path
    def add_select2role(
        self, guild_id: int, title: str, role_name: str, role_id: int, description: str
    ) -> None:
        self.model.create(
            f"{self.path}/select2role/selects/{title}",
            args={"name": role_name, "role_id": role_id, "description": description},
        )

    @Utils.resolve_guild_path
    def get_select2role(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/select2role")

    @Utils.resolve_guild_path
    def remove_select2role(self, guild_id: int, title: str) -> None:
        self.model.delete(f"{self.path}/select2role/selects/{title}")

    @Utils.resolve_guild_path
    def purge_select2role(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}/select2role/selects")

    @Utils.resolve_guild_path
    def set_select2role_channel(
        self, guild_id: int, channel_id: int, roles_msg_id: int
    ) -> None:
        self.model.update(
            f"{self.path}/select2role",
            args={"channel_id": channel_id, "roles_msg_id": roles_msg_id},
        )

    """ MUTED ROLE """

    @Utils.resolve_guild_path
    def set_muted_role(self, guild_id: int, role_id: Union[int, None]) -> None:
        self.model.update(f"{self.path}", args={"muted_role": role_id})

    @Utils.resolve_guild_path
    def get_muted_role(self, guild_id: int) -> int:
        return self.model.get(f"{self.path}/muted_role")

    """ MODS CHANNEL """

    @Utils.resolve_guild_path
    def set_mods_channel(self, guild_id: int, channel_id: Union[int, None]) -> None:
        self.model.update(f"{self.path}", args={"mods_channel_id": channel_id})

    @Utils.resolve_guild_path
    def get_mods_channel(self, guild_id: int) -> int:
        return self.model.get(f"{self.path}/mods_channel_id")

    """ GAMES CATEGORY """

    @Utils.resolve_guild_path
    def set_games_category(self, guild_id: int, category_id: Union[int, None]) -> None:
        self.model.update(f"{self.path}", args={"games_category_id": category_id})

    @Utils.resolve_guild_path
    def get_games_category(self, guild_id: int) -> int:
        return self.model.get(f"{self.path}/games_category_id")
