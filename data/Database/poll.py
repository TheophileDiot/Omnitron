from collections import OrderedDict
from datetime import datetime
from itertools import chain
from typing import Union

from data import Utils


class Poll:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = "polls"

    """ CREATION & DELETION """

    @Utils.resolve_guild_path
    def create_poll(
        self,
        guild_id: int,
        _id: int,
        _duration: int,
        at: float,
        choices: Union[list, OrderedDict],
        responses: list = None,
    ) -> None:
        self.model.create(
            f"{self.path}/{_id}",
            args={
                "id": _id,
                "duration": Utils.duration(_duration),
                "duration_s": _duration,
                "created_at": datetime.fromtimestamp(at).strftime("%d/%m/%Y, %H:%M:%S"),
                "created_at_s": at,
                "choices": {
                    choice.label: 0 for choice in list(chain.from_iterable(choices))
                }
                if isinstance(choices, list)
                else choices,
                "responses": responses,
            },
        )

    @Utils.resolve_guild_path
    def get_poll(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}")

    @Utils.resolve_guild_path
    def get_polls(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}")

    @Utils.resolve_guild_path
    def delete_poll(self, guild_id: int, _id: int) -> bool:
        poll = self.model.get(f"{self.path}/{_id}") or None
        if poll:
            self.model.create(
                f"{self.path}/old/{_id}",
                args={
                    "id": _id,
                    "duration": poll["duration"],
                    "duration_s": poll["duration_s"],
                    "created_at": poll["created_at"],
                    "created_at_s": poll["created_at_s"],
                    "choices": poll["choices"],
                    "responses": poll["responses"] if "responses" in poll else None,
                },
            )
            self.model.delete(f"{self.path}/{_id}")
            return True
        return False

    @Utils.resolve_guild_path
    def erase_poll(self, guild_id: int, _id: int) -> None:
        self.model.delete(f"{self.path}/{_id}")

    @Utils.resolve_guild_path
    def create_response(
        self, guild_id: int, _id: int, label: str, user_id: int
    ) -> None:
        current_value = (self.model.get(f"{self.path}/{_id}/choices"))[label]
        self.model.create(
            f"{self.path}/{_id}/responses/{user_id}", args={"response": label}
        )
        self.model.update(f"{self.path}/{_id}/choices", args={label: current_value + 1})

    @Utils.resolve_guild_path
    def get_responses(self, guild_id: int, _id: int) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}/responses")
