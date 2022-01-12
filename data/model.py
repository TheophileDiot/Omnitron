from collections import OrderedDict
from os import getenv
from firebase_admin import credentials, db, initialize_app

from data.constants import FIREBASE_DATABASEURL


class Model:
    ref = None

    @classmethod
    def setup(self):
        cred = credentials.Certificate(
            {
                "type": getenv("type"),
                "project_id": getenv("project_id"),
                "private_key_id": getenv("private_key_id"),
                "private_key": getenv("private_key"),
                "client_email": getenv("client_email"),
                "client_id": getenv("client_id"),
                "auth_uri": getenv("auth_uri"),
                "token_uri": getenv("token_uri"),
                "auth_provider_x509_cert_url": getenv("auth_provider_x509_cert_url"),
                "client_x509_cert_url": getenv("client_x509_cert_url"),
            }
        )
        initialize_app(
            cred,
            {"databaseURL": FIREBASE_DATABASEURL or getenv("FIREBASE_DATABASEURL")},
        )

        # Get a reference to the database service
        self.ref = db.reference("dev/" if getenv("ENV") == "DEVELOPMENT" else "/")
        return self

    @classmethod
    def create(self, path: str, event: str = "set", *, args: dict = "") -> None:
        if event == "push":
            self.ref.child(path).push(args)
        elif event == "set":
            self.ref.child(path).set(args)

    @classmethod
    def update(self, path: str, *, args: dict) -> None:
        return self.ref.child(path).update(args)

    @classmethod
    def delete(self, path: str) -> None:
        return self.ref.child(path).remove()

    @classmethod
    def get(self, path: str) -> OrderedDict:
        return self.ref.child(path).get() or OrderedDict()
