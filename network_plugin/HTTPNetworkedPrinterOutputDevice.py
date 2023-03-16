import json
import time
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtNetwork import (
    QHttpPart,
    QNetworkReply,
    QNetworkRequest,
    QNetworkAccessManager,
)
from UM.Application import Application
from UM.Logger import Logger
from UM.Message import Message

from cura.PrinterOutput.NetworkedPrinterOutputDevice import \
    NetworkedPrinterOutputDevice, AuthState
from cura.PrinterOutput.PrinterOutputDevice import ConnectionState

if TYPE_CHECKING:
    from UM.FileHandler.FileHandler import FileHandler
    from UM.Scene.SceneNode import SceneNode


class HTTPNetworkedPrinterOutputDevice(NetworkedPrinterOutputDevice):
    """Snapmaker 2.0 printer control over HTTP.

    1. Connect
    2. Authenticate
    3. Send G-code file
    4. Disconnect
    """

    def __init__(self, device_id: str, address: str, properties: Dict[str, str]) -> None:
        super().__init__(device_id, address, properties)

        self._setInterfaceElements()

        self._api_prefix = ":8080/api/v1"

        self._token = ""  # API token
        self._stream = StringIO()  # data stream of file

        self.authenticationStateChanged.connect(self._onAuthenticationStateChanged)
        self.connectionStateChanged.connect(self._onConnectionStateChanged)

        # write done, cleanup
        self.writeFinished.connect(self.__onWriteFinished)

        self._progress = PrintJobUploadProgressMessage(self)
        self._need_auth = PrintJobNeedAuthMessage(self)

    def _setInterfaceElements(self) -> None:
        self.setPriority(2)
        self.setShortDescription("Send to {}".format(self._address))
        self.setDescription("Send to {}".format(self.getId()))
        self.setConnectionText("Connected to {}".format(self.getId()))

    def _onConnectionStateChanged(self, id) -> None:
        if self.connectionState == ConnectionState.Connected:
            if self.authenticationState != AuthState.Authenticated:
                return

            # once connected, we send file right away
            if not self._progress.visible:
                self._progress.show()

                self._upload()

    def _onAuthenticationStateChanged(self) -> None:
        if self.authenticationState == AuthState.Authenticated:
            self._need_auth.hide()
        elif self.authenticationState == AuthState.AuthenticationRequested:
            self._need_auth.show()
        elif self.authenticationState == AuthState.AuthenticationDenied:
            self._token = ""
            self._need_auth.hide()

    def setDeviceStatus(self, status: str):
        """Set Device Status

        IDLE, RUNNING, PAUSED, STOPPED
        """
        if status == "IDLE":
            if self.connectionState != ConnectionState.Connected:
                self.setConnectionState(ConnectionState.Connected)
        elif status in ("RUNNING", "PAUSED", "STOPPED"):
            if self.connectionState != ConnectionState.Busy:
                self.setConnectionState(ConnectionState.Connected)

    def requestWrite(self, nodes: List["SceneNode"], file_name: Optional[str] = None,
                     limit_mimetypes: bool = False, file_handler: Optional["FileHandler"] = None,
                     filter_by_machine: bool = False, **kwargs) -> None:
        """Custom request in subclass."""
        raise NotImplementedError

    def _writeFileJobFinished(self, job) -> None:
        # connect to remote
        self.connect()

    def __onWriteFinished(self):
        # disconnect from remote
        self.disconnect()

    def _queryParams(self) -> List[QHttpPart]:
        return [
            self._createFormPart("name=token", self._token.encode()),
            self._createFormPart("name=_", "{}".format(time.time()).encode()),
        ]

    def connect(self) -> None:
        # reset state
        self.setConnectionState(ConnectionState.Closed)
        self.setAuthenticationState(AuthState.NotAuthenticated)

        self.postFormWithParts("/connect", self._queryParams(), self._onRequestFinished)

    def disconnect(self) -> None:
        if self._token:
            self.postFormWithParts("/disconnect", self._queryParams(), self._onRequestFinished)

    def checkStatus(self):
        url = "/status?token={}&_={}".format(self._token, time.time())
        self.get(url, self._onRequestFinished)

    def _upload(self):
        Logger.info("Start to upload G-code file to device {}".format(self.getId()))
        if not self._token:
            return

        print_info = Application.getInstance().getPrintInformation()
        job_name = print_info.jobName.strip()
        print_time = print_info.currentPrintTime
        material_name = "-".join(print_info.materialNames)

        self._filename = "{}_{}_{}.gcode".format(
            job_name, material_name,
            "{}h{}m{}s".format(print_time.days * 24 + print_time.hours, print_time.minutes, print_time.seconds))

        parts = self._queryParams()
        parts.append(
            self._createFormPart(
                'name=file; filename="{}"'.format(self._filename),
                self._stream.getvalue().encode()))
        self._stream.close()
        self.postFormWithParts("/upload",
                               parts,
                               on_finished=self._onRequestFinished,
                               on_progress=self._onUploadProgress)

    def _jsonReply(self, reply: QNetworkReply):
        try:
            return json.loads(bytes(reply.readAll()).decode("utf-8"))
        except json.decoder.JSONDecodeError:
            Logger.warning("Received invalid JSON from snapmaker.")
            return {}

    def _onRequestFinished(self, reply: QNetworkReply) -> None:
        http_url = reply.url().toString()

        if reply.error() not in (
                QNetworkReply.NetworkError.NoError,
                QNetworkReply.NetworkError.AuthenticationRequiredError,  # 204 is No Content, not an error
        ):
            Logger.warning("Error %s from %s", reply.error(), http_url)
            self.setConnectionState(ConnectionState.Closed)
            Message(title="Error",
                    text=reply.errorString(),
                    lifetime=0,
                    dismissable=True).show()
            return

        http_code = reply.attribute(
            QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        Logger.info("Request: %s - %d", http_url, http_code)
        if not http_code:
            return

        http_method = reply.operation()
        if http_method == QNetworkAccessManager.Operation.GetOperation:
            # /api/v1/status
            if self._api_prefix + "/status" in http_url:
                if http_code == 200:  # approved
                    self.setAuthenticationState(AuthState.Authenticated)
                    resp = self._jsonReply(reply)
                    device_status = resp.get("status", "UNKNOWN")
                    self.setDeviceStatus(device_status)
                elif http_code == 401:  # denied
                    self.setAuthenticationState(AuthState.AuthenticationDenied)
                elif http_code == 204:  # wait for authentication on HMI
                    self.setAuthenticationState(AuthState.AuthenticationRequested)
                else:
                    self.setAuthenticationState(AuthState.NotAuthenticated)
        elif http_method == QNetworkAccessManager.Operation.PostOperation:
            # /api/v1/connect
            if self._api_prefix + "/connect" in http_url:
                if http_code == 200:
                    # success, got a token to start heartbeat
                    resp = self._jsonReply(reply)
                    token = resp.get("token")
                    if self._token != token:
                        self._token = token

                    # check status
                    self.checkStatus()

                elif http_code == 403 and self._token:
                    # expired, retry connect
                    self._token = ""
                    self.connect()
                else:
                    # failed
                    self.setConnectionState(ConnectionState.Closed)
                    Message(
                        title="Error",
                        text=
                        "Please check the touchscreen and try again (Err: {}).".format(http_code),
                        lifetime=10,
                        dismissable=True).show()

            # /api/v1/disconnect
            elif self._api_prefix + "/disconnect" in http_url:
                self._token = ""
                self.setConnectionState(ConnectionState.Closed)

            # /api/v1/upload
            elif self._api_prefix + "/upload" in http_url:
                self._progress.hide()
                self.writeFinished.emit()

                Message(title="Sent to {}".format(self.getId()),
                        text="Start print on the touchscreen: {}".format(self._filename),
                        lifetime=60).show()

    def _onUploadProgress(self, bytes_sent: int, bytes_total: int) -> None:
        if bytes_total > 0:
            percentage = (bytes_sent / bytes_total) if bytes_total else 0
            self._progress.setProgress(percentage * 100)
            self.writeProgress.emit()


class PrintJobNeedAuthMessage(Message):

    def __init__(self, device: HTTPNetworkedPrinterOutputDevice):
        super().__init__(
            title="Screen authorization needed",
            text="Please tap Yes on Snapmaker touchscreen to continue.",
            lifetime=0,
            dismissable=True,
            use_inactivity_timer=False)
        self._device = device
        self.setProgress(-1)
        self._gTimer = QTimer()
        self._gTimer.setInterval(1500)
        self._gTimer.timeout.connect(lambda: self._onCheck(None, None))
        self.inactivityTimerStart.connect(self._startTimer)
        self.inactivityTimerStop.connect(self._stopTimer)

    def _startTimer(self):
        if self._gTimer and not self._gTimer.isActive():
            self._gTimer.start()

    def _stopTimer(self):
        if self._gTimer and self._gTimer.isActive():
            self._gTimer.stop()

    def _onCheck(self, *args, **kwargs):
        self._device.checkStatus()


class PrintJobUploadProgressMessage(Message):

    def __init__(self, device: HTTPNetworkedPrinterOutputDevice):
        super().__init__(title="Sending to {}".format(device.getId()),
                         progress=-1,
                         lifetime=0,
                         dismissable=False,
                         use_inactivity_timer=False)
        self._device = device
        self._gTimer = QTimer()
        self._gTimer.setInterval(3 * 1000)
        self._gTimer.timeout.connect(lambda: self._heartbeat())
        self.inactivityTimerStart.connect(self._startTimer)
        self.inactivityTimerStop.connect(self._stopTimer)

    def show(self):
        self.setProgress(0)
        super().show()

    def update(self, percentage: int):
        if not self._visible:
            super().show()
        self.setProgress(percentage)

    def _heartbeat(self):
        self._device.checkStatus()

    def _startTimer(self):
        if self._gTimer and not self._gTimer.isActive():
            self._gTimer.start()

    def _stopTimer(self):
        if self._gTimer and self._gTimer.isActive():
            self._gTimer.stop()
