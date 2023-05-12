from typing import Union

from UM.Application import Application
from cura.OAuth2.Models import BaseModel
from cura.OAuth2.KeyringAttribute import KeyringAttribute


class HTTPTokenManager(BaseModel):
    """Manager for HTTP tokens."""

    PREFERENCE_KEY_TOKEN = "SnapmakerPlugin/tokens"

    instance = None

    @classmethod
    def getInstance(cls) -> "HTTPTokenManager":
        if not cls.instance:
            cls.instance = HTTPTokenManager()
            cls.instance.loadTokens()

        return cls.instance

    def __init__(self) -> None:
        self._attributes = {}

    def loadTokens(self) -> None:
        preferences = Application.getInstance().getPreferences()
        # Remove the preference we used on earlier version (<= 0.9.0)
        preferences.removePreference(self.PREFERENCE_KEY_TOKEN)

    def getToken(self, key: str) -> Union[str, None]:
        attribute = getattr(self, key, None)  # type: Union[KeyringAttribute, None]
        return attribute.__get__(self, type(self)) if attribute else None

    def setToken(self, key: str, token: str) -> None:
        attribute = getattr(self, key, None)  # type: Union[KeyringAttribute, None]
        if not attribute:
            # Note that we use dynamic descriptors instead static
            attribute = KeyringAttribute()
            attribute.__set_name__(self, key)
            setattr(self, key, attribute)

        # It's a bit tricky to call __get__ and __set__ directly, cuz we
        # can not call descriptor by acccess instance.attribute.
        saved_token = attribute.__get__(self, type(self))
        if saved_token != token:
            attribute.__set__(self, token)
