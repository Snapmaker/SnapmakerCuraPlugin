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


class SnapmakerJ1Plugin(Extension):

    def __init__(self) -> None:
        super().__init__()

        self._plugin_path = None  # type: Optional[str]

        self._preferences = None  # type: Optional[PluginPreferences]

        self._previous_version = "0.0.0"

        Application.getInstance().pluginsLoaded.connect(self._onPluginsLoaded)
        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

    def _onPluginsLoaded(self) -> None:
        # when plugins are loaded, we can actually get plugin id
        self._plugin_path = PluginRegistry.getInstance().getPluginPath(self.getPluginId())

        self._preferences = PluginPreferences(self.getPluginId())
        self._preferences.addPrefenrece("version", "0.0.0")

        self._previous_version = self._preferences.getValue("version")
        self.installResources()

    def _onEngineCreated(self) -> None:
        # preferences is initialized, we can set values by now
        self._preferences.setValue("version", self.getVersion())

    def __shouldUpdateResources(self) -> bool:
        # debugging mode, always update
        if self.getVersion() == "0.0.0":
            return True

        # Once plugin version changed, update profiles
        if self._previous_version is None or self._previous_version != self.getVersion():
            return True

        return False

    def __updateMachineProfiles(self) -> None:
        plugin_profile_root_folder = os.path.join(self._plugin_path, "resources", "snapmaker_j1_profiles")
        plugin_machine_folder = os.path.join(plugin_profile_root_folder, "definitions")
        plugin_extruder_folder = os.path.join(plugin_profile_root_folder, "extruders")
        plugin_quality_folder = os.path.join(plugin_profile_root_folder, "quality")

        definition_dir = Resources.getStoragePath(Resources.DefinitionContainers)
        extruder_dir = Resources.getStoragePath(CuraApplication.ResourceTypes.ExtruderStack)
        quality_dir = Resources.getStoragePath(CuraApplication.ResourceTypes.QualityInstanceContainer)

        # copy machine definitions
        for filename in os.listdir(plugin_machine_folder):
            if filename.endswith(".def.json"):
                file_path = os.path.join(plugin_machine_folder, filename)
                shutil.copy2(file_path, definition_dir)

        # copy extruders
        for filename in os.listdir(plugin_extruder_folder):
            if filename.endswith(".def.json"):
                file_path = os.path.join(plugin_extruder_folder, filename)
                shutil.copy2(file_path, extruder_dir)

        # copy quality files
        for filename in os.listdir(plugin_quality_folder):
            file_path = os.path.join(plugin_quality_folder, filename)
            if os.path.isdir(file_path):  # machine quality folder
                shutil.copytree(file_path, os.path.join(quality_dir, filename), dirs_exist_ok=True)

    def __updateMaterials(self) -> None:
        plugin_material_dir = os.path.join(self._plugin_path, "resources", "materials")

        material_dir = Resources.getStoragePath(CuraApplication.ResourceTypes.MaterialInstanceContainer)

        for filename in os.listdir(plugin_material_dir):
            if filename.endswith(".xml.fdm_material"):
                file_path = os.path.join(plugin_material_dir, filename)
                shutil.copy2(file_path, material_dir)

    def installResources(self) -> None:
        if not self.__shouldUpdateResources():
            return

        Logger.info("Preparing profiles for Snapmaker J1...")
        self.__updateMachineProfiles()
        self.__updateMaterials()
