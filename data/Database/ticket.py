from collections import OrderedDict

from data import Utils


class Ticket:
    def __init__(self, model) -> None:
        self.model = model
        self.innerpath = "tickets"

    """ CREATION & DELETION """

    @Utils.resolve_guild_path
    def create_ticket(self, guild_id: int, _id: int, user_id: int) -> None:
        self.model.create(f"{self.path}/{_id}", args={"user_id": user_id})

    @Utils.resolve_guild_path
    def delete_ticket(self, guild_id: int, _id: str) -> None:
        self.model.delete(f"{self.path}/{_id}")

    @Utils.resolve_guild_path
    def purge_tickets(self, guild_id: int) -> None:
        self.model.delete(f"{self.path}")

    """ MANAGEMENT """

    @Utils.resolve_guild_path
    def prepare_deletion(self, guild_id: int, _id: str, user_id: int) -> None:
        self.model.create(
            f"{self.path}/{_id}/deletion_pending", args={"author": user_id}
        )

    @Utils.resolve_guild_path
    def cancel_deletion(self, guild_id: int, _id: str) -> None:
        self.model.delete(f"{self.path}/{_id}/deletion_pending")

    @Utils.resolve_guild_path
    def get_ticket(self, guild_id: int, _id: str) -> OrderedDict:
        return self.model.get(f"{self.path}/{_id}")

    @Utils.resolve_guild_path
    def get_tickets(self, guild_id: int) -> OrderedDict:
        return self.model.get(f"{self.path}")
