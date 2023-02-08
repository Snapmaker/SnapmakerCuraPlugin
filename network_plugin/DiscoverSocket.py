import socket

from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QUdpSocket, QAbstractSocket, QHostAddress, QNetworkAddressEntry

from UM.Platform import Platform
from UM.Signal import signalemitter, Signal


# Hard-coded discover port, all Snapmaker printer will be listen on 20054
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
            sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
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
            self._socket.writeDatagram(
                message, self._broadcast_address, DISCOVER_PORT)
        else:
            self._socket.sendto(
                message, (self._broadcast_address.toString(), DISCOVER_PORT))
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
