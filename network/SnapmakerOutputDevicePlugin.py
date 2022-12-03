import socket

from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QNetworkInterface, QUdpSocket, QAbstractSocket, QHostAddress, QNetworkAddressEntry
from UM.Application import Application
from UM.Logger import Logger
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.Platform import Platform
from UM.Signal import signalemitter, Signal

from .SnapmakerJ1OutputDevice import SnapmakerJ1OutputDevice
from ..config import MACHINE_NAME

DISCOVER_PORT = 20054


@signalemitter
class DiscoverSocket:
    dataReady = Signal()

    def __init__(self, address_entry: QNetworkAddressEntry) -> None:
        self._address_entry = address_entry
        self._broadcast_address = address_entry.broadcast()

        self._socket = None  # internal socket

        self._collect_timer = QTimer()
        self._collect_timer.setInterval(200)
        self._collect_timer.setSingleShot(True)
        self._collect_timer.timeout.connect(self.__collect)

    @property
    def address(self) -> QHostAddress:
        return self._address_entry.ip()

    def bind(self) -> bool:
        sock = QUdpSocket()

        bind_result = sock.bind(self._address_entry.ip(), mode=QAbstractSocket.BindFlag.DontShareAddress |
                                                               QAbstractSocket.BindFlag.ReuseAddressHint)
        if not bind_result:
            return False

        if Platform.isWindows():
            # On Windows, QUdpSocket is unable to receive broadcast data, we use original socket instead
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(0.2)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            self._socket = sock
        else:
            # On Unix, we use socket interface provided by Qt 6
            self._socket = sock
            sock.readyRead.connect(self.__read)

        return True

    def discover(self, message: bytes) -> None:
        if isinstance(self._socket, QUdpSocket):
            self._socket.writeDatagram(message, self._broadcast_address, DISCOVER_PORT)
        else:
            self._socket.sendto(message, (self._broadcast_address.toString(), DISCOVER_PORT))
            self._collect_timer.start()

    def abort(self) -> None:
        if not self._socket:
            return

        if isinstance(self._socket, QUdpSocket):
            self._socket.abort()
        else:
            self._socket.close()

        self._socket = None

    def __read(self) -> None:
        while self._socket.hasPendingDatagrams():
            data = self._socket.receiveDatagram()
            if data.isValid() and not data.senderAddress().isNull():
                try:
                    message = bytes(data.data()).decode("utf-8")
                    self.dataReady.emit(message)
                except UnicodeDecodeError:
                    pass

    def __collect(self) -> None:
        # the socket has abort and discover is cancelled
        if not self._socket:
            return

        if isinstance(self._socket, QUdpSocket):
            return

        while True:
            try:
                msg, _ = self._socket.recvfrom(128)
            except (TimeoutError, ConnectionError):
                # normal timeout, or ConnectionError (including ConnectionAbortedError, ConnectionRefusedError,
                # ConnectionResetError) errors raise by the peer
                break

            try:
                message = msg.decode("utf-8")
                self.dataReady.emit(message)
            except UnicodeDecodeError:
                pass


class SnapmakerOutputDevicePlugin(OutputDevicePlugin):
    """Output device plugin that detects Snapmaker machines."""

    def __init__(self) -> None:
        super().__init__()

        self._discover_timer = QTimer()
        self._discover_timer.setInterval(10000)  # 10 seconds
        self._discover_timer.setSingleShot(False)
        self._discover_timer.timeout.connect(self.__discover)

        self._discover_sockets = []  # type: List[QUdpSocket]

        Application.getInstance().globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
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

                sock = DiscoverSocket(address_entry)
                if sock.bind():
                    Logger.info("Discovering printers on network interface: %s", address.toString())
                    sock.dataReady.connect(self.__onData)
                    self._discover_sockets.append(sock)

    def __discover(self) -> None:
        if not self._discover_sockets:
            self.__prepare()

        for sock in self._discover_sockets:
            Logger.info("Discovering networked printer... (interface: %s)", sock.address.toString())
            sock.discover(b"discover")

        # TODO: remove output devices that not reply message for a period of time

    def __onData(self, msg: str) -> None:
        """Parse message.

        e.g. Snapmaker J1@172.18.0.2|model:J1|status:IDLE
        """
        parts = msg.split("|")
        if len(parts) < 1 or "@" not in parts[0]:
            # invalid message
            return

        device_id = parts[0]
        name, address = device_id.rsplit("@", 1)

        properties = {}
        for part in parts[1:]:
            if ":" not in part:
                continue

            key, value = part.split(":")
            properties[key] = value

        # only accept Snapmaker J1 series
        model = properties.get("model", "")
        if not model.startswith(MACHINE_NAME):
            return

        device = self.getOutputDeviceManager().getOutputDevice(device_id)
        if not device:
            Logger.info("Discovered Snapmaker J1 printer: %s@%s", name, address)
            device = SnapmakerJ1OutputDevice(device_id, address, properties)
            self.getOutputDeviceManager().addOutputDevice(device)

    def start(self) -> None:
        # check for current global container
        global_stack = Application.getInstance().getGlobalContainerStack()
        machine_name = global_stack.getProperty("machine_name", "value")
        if not machine_name.startswith(MACHINE_NAME):
            return

        if not self._discover_timer.isActive():
            self._discover_timer.start()
            Logger.info("Snapmaker J1 discovering started.")

    def stop(self) -> None:
        if self._discover_timer.isActive():
            self._discover_timer.stop()

        for sock in self._discover_sockets:
            sock.abort()

        # clear all discover sockets
        self._discover_sockets.clear()

        Logger.info("Snapmaker J1 discovering stopped.")

    def startDiscovery(self) -> None:
        self.__discover()

    def _onGlobalContainerStackChanged(self) -> None:
        global_stack = Application.getInstance().getGlobalContainerStack()

        # Start timer when active machine is Snapmaker J1 only
        machine_name = global_stack.getProperty("machine_name", "value")
        if machine_name.startswith(MACHINE_NAME):
            self.start()
        else:
            self.stop()
