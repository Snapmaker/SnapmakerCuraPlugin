from UM.FileHandler.FileWriter import FileWriter
from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.i18n import i18nCatalog
from UM.Application import Application

catalog = i18nCatalog("cura")


class SnapmakerJ1GCodeWriter(MeshWriter):
    """GCode Writer that writes G-code in Snapmaker J1 favour.

    - Add Snapmaker J1 specific headers and thumbnail
    """

    def __init__(self) -> None:
        super().__init__(add_to_recent_files=True)

    def write(self, stream, node, mode=FileWriter.OutputMode.BinaryMode) -> None:
        """Writes the G-code for the entire scene to a stream.

        Copied from GCodeWriter, do little modifications.
        """

        if mode != MeshWriter.OutputMode.TextMode:
            Logger.log("e", "GCodeWriter does not support non-text mode.")
            self.setInformation(catalog.i18nc("@error:not supported", "GCodeWriter does not support non-text mode."))
            return False

        active_build_plate = Application.getInstance().getMultiBuildPlateModel().activeBuildPlate
        scene = Application.getInstance().getController().getScene()
        if not hasattr(scene, "gcode_dict"):
            self.setInformation(catalog.i18nc("@warning:status", "Please prepare G-code before exporting."))
            return False

        gcode_dict = getattr(scene, "gcode_dict")
        gcode_list = gcode_dict.get(active_build_plate, None)
        if gcode_list is not None:
            for gcode in gcode_list:
                stream.write(gcode)
            return True

        self.setInformation(catalog.i18nc("@warning:status", "Please prepare G-code before exporting."))
        return False

