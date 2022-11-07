from UM.FileHandler.FileWriter import FileWriter

from .SnapmakerJ1Plugin import SnapmakerJ1Plugin
from .gcode_writer.SnapmakerJ1GCodeWriter import SnapmakerJ1GCodeWriter
from .network.SnapmakerOutputDevicePlugin import SnapmakerOutputDevicePlugin


def getMetaData():
    return {
        "mesh_writer": {
            "extension": "gcode",
            "description": "Snapmaker J1 G-code File",
            "mime_type": "text/x-gcode",
            "mode": FileWriter.OutputMode.TextMode,
        }
    }


def register(app):
    return {
        "extension": SnapmakerJ1Plugin(),
        "mesh_writer": SnapmakerJ1GCodeWriter(),
        "output_device": SnapmakerOutputDevicePlugin(),
    }
