from collections import OrderedDict

from data import Utils


class Games:
    def __init__(self, model, bot) -> None:
        self.model = model
        self.innerpath = "games"
        self.bot = bot

    """ CREATION & DELETION """

    @Utils.resolve_guild_path
    def create_game(
        self, guild_id: int, channel_id: int, game_id: int, players: dict
    ) -> None:
        self.model.create(
            f"{self.path}/{channel_id}",
            args={
                "game_id": game_id,
                "players": players,
            },
        )

    @Utils.resolve_guild_path
    def remove_game(self, guild_id: int, channel_id: int) -> None:
        self.model.delete(f"{self.path}/{channel_id}")

    """ OTHERS """

    @Utils.resolve_guild_path
    def get_game(self, guild_id: int, channel_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{channel_id}/{_id}")

    @Utils.resolve_guild_path
    def get_game_channel(self, guild_id: int, channel_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{channel_id}")

    @Utils.resolve_guild_path
    def get_game_channels(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}")
