from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional

from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Message import Message
from UM.Mesh.MeshWriter import MeshWriter

from cura.PrinterOutput.PrinterOutputDevice import ConnectionState
from ..gcode_writer.SnapmakerGCodeWriter import SnapmakerGCodeWriter
from .HTTPNetworkedPrinterOutputDevice import HTTPNetworkedPrinterOutputDevice

if TYPE_CHECKING:
    from UM.FileHandler.FileHandler import FileHandler
    from UM.Scene.SceneNode import SceneNode


class Snapmaker2OutputDevice(HTTPNetworkedPrinterOutputDevice):

    def __init__(self, device_id: str, address: str, properties: Dict[str, str]) -> None:
        super().__init__(device_id, address, properties)

        self._setInterfaceElements()

    def _setInterfaceElements(self) -> None:
        self.setPriority(2)
        self.setShortDescription("Send to {}".format(self._address))
        self.setDescription("Send to {}".format(self.getId()))
        self.setConnectionText("Connected to {}".format(self.getId()))

    def requestWrite(self, nodes: List["SceneNode"], file_name: Optional[str] = None,
                     limit_mimetypes: bool = False, file_handler: Optional["FileHandler"] = None,
                     filter_by_machine: bool = False, **kwargs) -> None:
        if self.connectionState == ConnectionState.Busy:
            Message(title="Unable to send request",
                    text="Machine {} is busy".format(self.getId())).show()
            return

        self.writeStarted.emit(self)

        message = Message(
            text="Preparing to upload",
            progress=-1,
            lifetime=0,
            dismissable=False,
            use_inactivity_timer=False,
        )
        message.show()

        self._stream = StringIO()  # create a new io stream

        writer = SnapmakerGCodeWriter()

        job = WriteFileJob(writer, self._stream, nodes, MeshWriter.OutputMode.TextMode)
        job.finished.connect(self._writeFileJobFinished)
        job.setMessage(message)
        job.start()
