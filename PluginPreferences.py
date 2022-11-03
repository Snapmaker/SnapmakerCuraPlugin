from UM.Application import Application
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from UM.Preferences import Preferences


class PluginPreferences:

    def __init__(self, category: str) -> None:
        self._category = category

    def getFullKey(self, key) -> str:
        if self._category:
            return "{}/{}".format(self._category, key)
        return key

    def addPrefenrece(self, key: str, default_value: Any) -> None:
        preferences = Application.getInstance().getPreferences()  # type: Preferences
        preferences.addPreference(self.getFullKey(key), default_value)

    def getValue(self, key: str) -> Any:
        preferences = Application.getInstance().getPreferences()  # type: Preferences
        return preferences.getValue(self.getFullKey(key))

    def setValue(self, key: str, value: Any) -> None:
        preferences = Application.getInstance().getPreferences()  # type: Preferences
        preferences.setValue(self.getFullKey(key), value)
