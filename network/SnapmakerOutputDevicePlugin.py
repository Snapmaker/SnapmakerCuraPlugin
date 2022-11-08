from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QNetworkInterface, QUdpSocket, QAbstractSocket, QHostAddress

from UM.Application import Application
from UM.Logger import Logger
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin

from .SnapmakerJ1OutputDevice import SnapmakerJ1OutputDevice

DISCOVER_PORT = 20054


class SnapmakerOutputDevicePlugin(OutputDevicePlugin):
    """Output device plugin that detects Snapmaker machines."""

    def __init__(self) -> None:
        super().__init__()

        self._discover_timer = QTimer()
        self._discover_timer.setInterval(10000)  # 10 seconds
        self._discover_timer.setSingleShot(False)
        self._discover_timer.timeout.connect(self.__discover)

        self._discover_sockets = []  # type: List[QUdpSocket]

        # TODO: Start only when global container is J1
        # Application.getInstance().globalContainerStackChanged.connect(self.start)
        Application.getInstance().applicationShuttingDown.connect(self.stop)

    def __prepare(self) -> None:
        self._discover_sockets = []
        for interface in QNetworkInterface.allInterfaces():
            for address_entry in interface.addressEntries():
                address = address_entry.ip()
                if address.isLoopback():
                    continue
                if address.protocol() != QAbstractSocket.NetworkLayerProtocol.IPv4Protocol:
                    continue

                Logger.info("Discovering printers on network interface: %s", address.toString())
                socket = QUdpSocket()
                socket.bind(address)
                socket.readyRead.connect(lambda: self._readSocket(socket))
                self._discover_sockets.append(socket)

    def __discover(self) -> None:
        if not self._discover_sockets:
            self.__prepare()

        for socket in self._discover_sockets:
            socket.writeDatagram(b"discover", QHostAddress.SpecialAddress.Broadcast, DISCOVER_PORT)

    def __parseMessage(self, ip: str, msg: str) -> None:
        """Parse message.

        e.g. Snapmaker J1@172.18.0.2|model:J1|status:IDLE
        """
        parts = msg.split("|")
        if len(parts) < 1 or "@" not in parts[0]:
            # invalid message
            return

        device_id = parts[0]
        name, address = device_id.split("@")

        properties = {}
        for part in parts[1:]:
            if ":" not in part:
                continue

            key, value = part.split(":")
            properties[key] = value

        # only accept Snapmaker J1 series
        model = properties.get("model", None)
        if model != "J1":
            return

        device = self.getOutputDeviceManager().getOutputDevice(device_id)
        if not device:
            Logger.info("Discovered Snapmaker J1: %s@%s", name, address)
            device = SnapmakerJ1OutputDevice(device_id, address, properties)
            self.getOutputDeviceManager().addOutputDevice(device)

    def _readSocket(self, socket: QUdpSocket) -> None:
        while socket.hasPendingDatagrams():
            data = socket.receiveDatagram()
            if data.isValid() and not data.senderAddress().isNull():
                ip = data.senderAddress().toString()
                try:
                    msg = bytes(data.data()).decode("utf-8")
                    self.__parseMessage(ip, msg)
                except UnicodeDecodeError:
                    pass

    def start(self) -> None:
        if not self._discover_timer.isActive():
            self._discover_timer.start()
            Logger.info("Snapmaker J1 discovering started.")

    def stop(self) -> None:
        if self._discover_timer.isActive():
            self._discover_timer.stop()

        for socket in self._discover_sockets:
            socket.abort()

        Logger.info("Snapmaker J1 discovering stopped.")

    def startDiscovery(self) -> None:
        self.__discover()
