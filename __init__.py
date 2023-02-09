from UM.FileHandler.FileWriter import FileWriter

from .settings_plugin.SnapmakerSettingsPlugin import SnapmakerSettingsPlugin
from .gcode_writer.SnapmakerGCodeWriter import SnapmakerGCodeWriter
from .network_plugin.SnapmakerOutputDevicePlugin import SnapmakerOutputDevicePlugin


def getMetaData():
    return {
        "mesh_writer": {
            "output": [{
                "extension": "gcode",
                "description": "Snapmaker Flavor G-code File",
                "mime_type": "text/x-gcode",
                "mode": FileWriter.OutputMode.TextMode,
            }]
        }
    }


def register(app):
    """Register plugins."""
    return {
        # Extends Snapmaker related settings
        "extension": SnapmakerSettingsPlugin(),

        # Writer to write Snapmaker J1 specific G-code
        "mesh_writer": SnapmakerGCodeWriter(),

        # Treat networked printers as output devices
        "output_device": SnapmakerOutputDevicePlugin(),
    }
