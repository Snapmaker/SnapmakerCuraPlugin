from typing import List

from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import QNetworkInterface, QAbstractSocket

from UM.Application import Application
from UM.Logger import Logger
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin

from .DiscoverSocket import DiscoverSocket
from .SnapmakerJ1OutputDevice import SnapmakerJ1OutputDevice
from .SnapmakerArtisanOutputDevice import SnapmakerArtisanOutputDevice
from .Snapamker2OutputDevice import Snapmaker2OutputDevice
from ..config import (
    is_machine_discover_supported,
    SNAPMAKER_J1,
    SNAPMAKER_ARTISAN,
    SNAPMAKER_2_A150_DUAL_EXTRUDER,
    SNAPMAKER_2_A250_DUAL_EXTRUDER,
    SNAPMAKER_2_A350_DUAL_EXTRUDER,
    SNAPMAKER_DISCOVER_MACHINES,
)


class SnapmakerOutputDevicePlugin(OutputDevicePlugin):
    """Output device plugin that detects networked Snapmaker printers.

    Start discovering only when active machine is a Snapmaker machine.
    """

    def __init__(self) -> None:
        super().__init__()

        self._discover_timer = QTimer()
        self._discover_timer.setInterval(16000)  # 16 seconds
        self._discover_timer.setSingleShot(False)
        self._discover_timer.timeout.connect(self.__discover)

        self._discover_sockets = []  # type: List[DiscoverSocket]

        self._active_machine_name = ""
        self._active_machine = None

        Application.getInstance().globalContainerStackChanged.connect(
            self._onGlobalContainerStackChanged)
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
                    Logger.info(
                        "Discovering printers on network interface: %s", address.toString())
                    sock.dataReady.connect(self.__onData)
                    self._discover_sockets.append(sock)

    def __discover(self) -> None:
        if not self._discover_sockets:
            self.__prepare()

        for sock in self._discover_sockets:
            Logger.info(
                "Discovering networked printer... (interface: %s)", sock.address.toString())
            sock.discover(b"discover")

        # TODO: remove output devices that not reply message for a period of time

    def __onData(self, msg: str) -> None:
        """Parse message.

        e.g. Snapmaker J1@172.18.0.2|model:Snapmaker J1|status:IDLE
        """
        # Logger.debug("Discovered printer: %s", msg)

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

        # only accept current active machine
        model = properties.get("model", "")
        if self._active_machine and model != self._active_machine['model']:
            return

        device = self.getOutputDeviceManager().getOutputDevice(device_id)
        if not device:
            Logger.info("Discovered %s printer: %s@%s",
                        self._active_machine_name, name, address)

            if model == SNAPMAKER_J1['name']:
                # J1
                device = SnapmakerJ1OutputDevice(device_id, address, properties)
                self.getOutputDeviceManager().addOutputDevice(device)
            elif model == SNAPMAKER_ARTISAN['name']:
                # Artisan
                device = SnapmakerArtisanOutputDevice(device_id, address, properties)
                self.getOutputDeviceManager().addOutputDevice(device)
            elif model in [SNAPMAKER_2_A150_DUAL_EXTRUDER['model'],
                           SNAPMAKER_2_A250_DUAL_EXTRUDER['model'],
                           SNAPMAKER_2_A350_DUAL_EXTRUDER['model'], ]:
                # Snapmaker 2.0 Dual Extruder
                device = Snapmaker2OutputDevice(device_id, address, properties)
                self.getOutputDeviceManager().addOutputDevice(device)

    def start(self) -> None:
        if not is_machine_discover_supported(self._active_machine_name):
            return

        if not self._discover_timer.isActive():
            self._discover_timer.start()
            Logger.info("Snapmaker printer discovering started.")

    def stop(self) -> None:
        if self._discover_timer.isActive():
            self._discover_timer.stop()

        for sock in self._discover_sockets:
            sock.abort()

        # clear all discover sockets
        self._discover_sockets.clear()

        Logger.info("Snapmaker printer discovering stopped.")

    def startDiscovery(self) -> None:
        self.__discover()

    def _updateActiveMachine(self) -> None:
        # check for current global container
        global_stack = Application.getInstance().getGlobalContainerStack()
        if global_stack is None:
            # First time launch, global stack could be None
            return

        machine_name = global_stack.getProperty("machine_name", "value")
        self._active_machine_name = machine_name

        for machine in SNAPMAKER_DISCOVER_MACHINES:
            if machine['name'] == machine_name:
                self._active_machine = machine
                break

    def _onGlobalContainerStackChanged(self) -> None:
        self._updateActiveMachine()

        # Start timer when active machine is supported
        if is_machine_discover_supported(self._active_machine_name):
            self.start()
        else:
            self.stop()
