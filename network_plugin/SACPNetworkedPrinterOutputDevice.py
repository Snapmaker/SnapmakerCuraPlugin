import hashlib
import struct
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional

from cura.CuraApplication import CuraApplication
from cura.PrinterOutput.NetworkedPrinterOutputDevice import \
    NetworkedPrinterOutputDevice
from cura.PrinterOutput.PrinterOutputDevice import ConnectionState
from PyQt6.QtNetwork import QTcpSocket
from UM.Logger import Logger
from UM.Message import Message

from .SACP import SACP_PACKAGE, SACP_pack, SACP_unpack, SACP_validData

if TYPE_CHECKING:
    from UM.FileHandler.FileHandler import FileHandler
    from UM.Scene.SceneNode import SceneNode


class SACPNetworkedPrinterOutputDevice(NetworkedPrinterOutputDevice):

    def __init__(self, device_id: str, address: str, properties: Dict[str, str]) -> None:
        super().__init__(device_id, address, properties)

        self._setInterfaceElements()

        self._stream = StringIO()
        self._data = ""
        self._data_md5 = ""

        self._socket = QTcpSocket()

        self.connectionStateChanged.connect(self.__onConnectionStateChanged)

        self.writeFinished.connect(self.__onWriteFinished)

    def _setInterfaceElements(self) -> None:
        self.setPriority(2)
        self.setShortDescription("Send to {}".format(self._address))
        self.setDescription("Send to {}".format(self.getId()))
        self.setConnectionText("Connected to {}".format(self.getId()))

    def requestWrite(self, nodes: List["SceneNode"], file_name: Optional[str] = None,
                     limit_mimetypes: bool = False, file_handler: Optional["FileHandler"] = None,
                     filter_by_machine: bool = False, **kwargs) -> None:
        """Custom request in subclass."""
        raise NotImplementedError

    def _writeFileJobFinished(self, job) -> None:
        self.connect()

    def connect(self) -> None:
        self.disconnect()

        self.setConnectionState(ConnectionState.Connecting)
        self._socket.connected.connect(self.__socketConnected)
        self._socket.readyRead.connect(self.__socketReadyRead)
        self._socket.connectToHost(self._address, 8888)

        Logger.info("Disconnected from output device.")

    def disconnect(self) -> None:
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            self._socket.connected.disconnect(self.__socketConnected)
            self._socket.readyRead.disconnect(self.__socketReadyRead)
            self._socket.close()

    def __socketConnected(self) -> None:
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            self.__sacpConnect()

    def __socketReadyRead(self) -> None:
        if self._socket.state() != QTcpSocket.SocketState.ConnectedState:
            Logger.debug("Socket not connected, abort read.")
            return

        while True:
            data = self._socket.read(4)
            if not data or len(data) < 4:
                break
            if data[0] != 0xAA and data[1] != 0x55:
                # discard this 4 bytes
                continue

            data_len = (data[2] | data[3] << 8) & 0xFFFF
            residue_data = self._socket.read(data_len + 3)
            data += residue_data
            receiver_data = SACP_unpack(data)

            if receiver_data.command_set == 0x01 and receiver_data.command_id == 0x05:
                token_length = receiver_data.valid_data[1]
                receiver_valid_data = SACP_validData(
                    receiver_data.valid_data, "<BH{0}s".format(token_length))

                if receiver_valid_data[0] == 0:  # connected
                    self.setConnectionState(ConnectionState.Connected)

            elif receiver_data.command_set == 0x01 and receiver_data.command_id == 0x05:
                receiver_valid_data = SACP_validData(
                    receiver_data.valid_data, "<B")
                if receiver_valid_data[0] == 0:  # connected
                    self.setConnectionState(ConnectionState.Closed)

            elif receiver_data.command_set == 0xb0 and receiver_data.command_id == 0x01:
                md5_length = receiver_data.valid_data[0]
                receiver_valid_data = SACP_validData(
                    receiver_data.valid_data, "<H{0}sH".format(md5_length))
                package_index = receiver_valid_data[-1]
                sequence = receiver_data.sequence

                package_data = self._data[(
                    SACP_PACKAGE * package_index):(SACP_PACKAGE * (package_index + 1))]
                self.__sacpSendGcodoFile(
                    self._data_md5, package_data, package_index, sequence)

            elif receiver_data.command_set == 0xb0 and receiver_data.command_id == 0x02:
                receiver_valid_data = SACP_validData(
                    receiver_data.valid_data, "<B")
                if receiver_valid_data[0] == 0:
                    self._sendFileFinished()

    def __onConnectionStateChanged(self, device_id: str) -> None:
        if self.connectionState == ConnectionState.Connected:
            # once connected, we send file right away
            self._sendFile()

    def __onWriteFinished(self):
        # disconnect from remote
        self.__sacpDisconnect()

        # disconnect socket
        self.disconnect()

    def _sendFile(self) -> None:
        self._prepareSendFile()

    def _sendFileFinished(self) -> None:
        self.writeFinished.emit()
        message = Message(
            title="Sent G-code file to {}".format(self.getId()),
            text="Please start print on the touchscreen.",
            lifetime=60,
        )
        message.show()

        Logger.info("Send G-code file successfully")

    def _prepareSendFile(self) -> None:
        print_info = CuraApplication.getInstance().getPrintInformation()

        job_name = print_info.jobName.strip()
        print_time = print_info.currentPrintTime
        material_name = "-".join(print_info.materialNames)

        self._data = self._stream.getvalue()
        self._data_md5 = hashlib.md5(self._data.encode("utf-8")).hexdigest()
        package_count = int(len(self._data) / SACP_PACKAGE) + 1

        filename = "{}_{}_{}.gcode".format(
            job_name,
            material_name,
            "{}h{}m{}s".format(
                print_time.days * 24 + print_time.hours,
                print_time.minutes,
                print_time.seconds)
        )

        # TODO: upload
        self.__sacpPrepareSendGcode(
            self._data, filename, self._data_md5, package_count)

    def __sacpString(self, s: str) -> bytes:
        s_utf = s.encode("utf-8")
        return struct.pack("<H", len(s_utf)) + s_utf

    def __sacpConnect(self) -> None:
        # device name, client name, token
        data = self.__sacpString(
            "Destop") + self.__sacpString("Cura") + self.__sacpString("")
        # struct.pack("<HHH", 0, 0, 0)

        packet = SACP_pack(receiver_id=2,
                           sender_id=0,
                           attribute=0,
                           sequence=1,
                           command_set=0x01,
                           command_id=0x05,
                           send_data=data)
        self._socket.write(packet)

    def __sacpDisconnect(self) -> None:
        packet = SACP_pack(receiver_id=2,
                           sender_id=0,
                           attribute=0,
                           sequence=1,
                           command_set=0x01,
                           command_id=0x06,
                           send_data=b'')
        self._socket.write(packet)

    def __sacpPrepareSendGcode(self, data: str, gcode_name, file_md5, package_count) -> None:
        data = data.encode("utf-8")
        gcode_name = gcode_name.encode("utf-8")
        file_md5 = file_md5.encode("utf-8")

        gcode_name_length = len(gcode_name)
        file_md5_length = len(file_md5)
        data_format = "H{0}sIHH{1}s".format(gcode_name_length, file_md5_length)
        packet_data = struct.pack(
            '<{0}'.format(data_format),
            gcode_name_length,
            gcode_name,
            len(data),
            package_count,
            file_md5_length,
            file_md5,
        )
        packet = SACP_pack(receiver_id=2,
                           sender_id=0,
                           attribute=0,
                           sequence=1,
                           command_set=0xb0,
                           command_id=0x00,
                           send_data=packet_data)
        self._socket.write(packet)

    def __sacpSendGcodoFile(self, file_md5, data: str, index, sequence):
        gcode_data_length = len(data.encode('utf-8'))
        file_md5_length = len(file_md5.encode('utf-8'))
        data_format = "BH{0}sHH{1}s".format(file_md5_length, gcode_data_length)
        data = struct.pack('<{0}'.format(data_format),
                           0,
                           file_md5_length,
                           file_md5.encode('utf-8'),
                           index,
                           gcode_data_length,
                           data.encode('utf-8'),
                           )
        packet = SACP_pack(receiver_id=2,
                           sender_id=0,
                           attribute=1,
                           sequence=sequence,
                           command_set=0xb0,
                           command_id=0x01,
                           send_data=data)
        self._socket.write(packet)
