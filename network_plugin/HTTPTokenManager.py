import json
from typing import Union

from UM.Application import Application
from UM.Logger import Logger


class HTTPTokenManager:
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
        self._tokens = {}  # type: Dict[str, str]

        self._dirty = False

    def loadTokens(self) -> None:
        preferences = Application.getInstance().getPreferences()
        preferences.addPreference(self.PREFERENCE_KEY_TOKEN, "{}")

        try:
            self._tokens = json.loads(
                preferences.getValue(self.PREFERENCE_KEY_TOKEN)
            )
        except ValueError:
            # failed to parse JSON
            self._tokens = {}
            self._dirty = True

        if not isinstance(self._tokens, dict):
            self._tokens = {}
            self._dirty = True

    def saveTokens(self) -> None:
        if self._dirty:
            try:
                preferences = Application.getInstance().getPreferences()
                preferences.setValue(self.PREFERENCE_KEY_TOKEN, json.dumps(self._tokens))
            except ValueError:
                pass

            self._dirty = False

    def getToken(self, key: str) -> Union[str, None]:
        return self._tokens.get(key, None)

    def setToken(self, key: str, token: str) -> None:
        saved_token = self._tokens.get(key, "")
        if not saved_token or token != saved_token:
            self._tokens[key] = token
            self._dirty = True
