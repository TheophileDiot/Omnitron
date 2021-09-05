from collections import OrderedDict
from discord.ext.tasks import loop
from os import getenv
from pyrebase import initialize_app

from data.constants import (
    FIREBASE_APIKEY,
    FIREBASE_AUTHDOMAIN,
    FIREBASE_DATABASEURL,
    FIREBASE_STORAGEBUCKET,
    FIREBASE_USER_EMAIL,
    FIREBASE_USER_PASSWORD,
)


class Model:
    @classmethod
    def setup(self):
        config = {
            "apiKey": FIREBASE_APIKEY or getenv("FIREBASE_APIKEY"),
            "authDomain": FIREBASE_AUTHDOMAIN or getenv("FIREBASE_AUTHDOMAIN"),
            "databaseURL": FIREBASE_DATABASEURL or getenv("FIREBASE_DATABASEURL"),
            "storageBucket": FIREBASE_STORAGEBUCKET or getenv("FIREBASE_STORAGEBUCKET"),
        }

        firebase = initialize_app(config)

        # Get a reference to the auth service
        self.auth = firebase.auth()

        # Log the user in
        self.user = self.auth.sign_in_with_email_and_password(
            FIREBASE_USER_EMAIL or getenv("FIREBASE_USER_EMAIL"),
            FIREBASE_USER_PASSWORD or getenv("FIREBASE_USER_PASSWORD"),
        )

        # Get a reference to the database service
        self.db = firebase.database()
        self.refrech_token.start(self)
        return self

    @classmethod
    def create(self, path: str, event: str = "set", *, args: dict = "") -> None:
        if event == "push":
            self.db.child(f"dev/{path}").push(args, token=self.user["idToken"])
        elif event == "set":
            self.db.child(f"dev/{path}").set(args, token=self.user["idToken"])

    @classmethod
    def update(self, path: str, *, args: dict) -> None:
        return self.db.child(f"dev/{path}").update(args, token=self.user["idToken"])

    @classmethod
    def delete(self, path: str) -> None:
        return self.db.child(f"dev/{path}").remove(token=self.user["idToken"])

    @classmethod
    def get(self, path: str) -> OrderedDict:
        return (
            self.db.child(f"dev/{path}").get(token=self.user["idToken"]).val()
            or OrderedDict()
        )

    """ LOOPS """

    @loop(minutes=58)
    async def refrech_token(self):
        self.user = self.auth.refresh(self.user["refreshToken"])
