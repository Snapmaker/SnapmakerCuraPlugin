import os.path
import shutil
from typing import Optional

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.Resources import Resources

from cura.CuraApplication import CuraApplication
from .PluginPreferences import PluginPreferences

SNAPMAKER_J1_DEFINITION_NAME = "snapmaker_j1.def.json"


class SnapmakerJ1Plugin(Extension):

    def __init__(self) -> None:
        super().__init__()

        self._plugin_path = None  # type: Optional[str]

        self._preferences = None  # type: Optional[PluginPreferences]

        self._previous_version = "0.0.0"

        Application.getInstance().pluginsLoaded.connect(self._onPluginsLoaded)

    def _onPluginsLoaded(self) -> None:
        self._plugin_path = PluginRegistry.getInstance().getPluginPath(self.getPluginId())

        self._preferences = PluginPreferences(self.getPluginId())
        self._preferences.addPrefenrece("version", "0.0.0")

        self._previous_version = self._preferences.getValue("version")
        self._preferences.setValue("version", self.getVersion())

        self.installMachineProfiles()

    def __shouldUpdateMachineProfiles(self) -> bool:
        # debugging mode, always update
        if self.getVersion() == "0.0.0":
            return True

        # Once plugin version changed, update profiles
        if self._previous_version is None or self._previous_version != self.getVersion():
            return True

        return False

    def installMachineProfiles(self) -> None:
        if not self.__shouldUpdateMachineProfiles():
            return

        plugin_profile_root_folder = os.path.join(self._plugin_path, "resources", "snapmaker_j1_profiles")
        plugin_machine_folder = os.path.join(plugin_profile_root_folder, "definitions")
        plugin_extruder_folder = os.path.join(plugin_profile_root_folder, "extruders")
        plugin_quality_folder = os.path.join(plugin_profile_root_folder, "quality")

        definitions_path = Resources.getStoragePath(Resources.DefinitionContainers)
        extruder_path = Resources.getStoragePath(CuraApplication.ResourceTypes.ExtruderStack)
        quality_folder = Resources.getStoragePath(CuraApplication.ResourceTypes.QualityInstanceContainer)

        # copy machine definitions
        for filename in os.listdir(plugin_machine_folder):
            if filename.endswith(".def.json"):
                file_path = os.path.join(plugin_machine_folder, filename)
                shutil.copy2(file_path, definitions_path)

        for filename in os.listdir(plugin_extruder_folder):
            if filename.endswith(".def.json"):
                file_path = os.path.join(plugin_extruder_folder, filename)
                shutil.copy2(file_path, extruder_path)

        for filename in os.listdir(plugin_quality_folder):
            file_path = os.path.join(plugin_quality_folder, filename)
            Logger.debug("-------------- file_path = %s %s", plugin_quality_folder, filename)
            if os.path.isdir(file_path):  # machine quality folder
                Logger.debug("-------------- file_path = %s %s", file_path, quality_folder)
                shutil.copytree(file_path, quality_folder, dirs_exist_ok=True)
