import math
import time
from typing import List, Dict, Any, Optional
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Signal, Qt, QThreadPool
from src.entities import Device
from src.constants import DeviceStatus
from src.utils.logger import logger
from src.utils.yaml_handler import settings
from src.services.device_service import DeviceService
from src.drivers.scrcpy.scrcpy_client import ScrcpyClient
from src.controllers.base_controller import BaseController
from src.worker.generic_worker import GenericWorker
from src.drivers.redsocks.redsocks_driver import RedsocksDriver
from src.worker.screen_shot import ScreenshotTask


class DeviceController(BaseController[Device]):
    """
    Controller responsible for managing physical mobile devices.

    Handles device lifecycle signals, UI mirroring via Scrcpy, grid-based window
    positioning, and network proxy configuration via Redsocks.
    """

    device_state_changed = Signal(Device)
    redsocks_enable_success = Signal(Device, str)
    redsocks_enable_failed = Signal(Device, str)
    redsocks_disable_success = Signal(Device)

    def __init__(self, service: DeviceService):
        super().__init__(service)
        self.service = service

        self.service.signals.device_connected.connect(self.on_device_state_change)
        self.service.signals.device_disconnected.connect(self.on_device_state_change)

        self._active_scrcpy_clients: Dict[str, ScrcpyClient] = {}
        self._active_workers: Dict[str, dict] = {}
        self._scrcpy_slots: Dict[str, int] = {}
        self.thread_pool = QThreadPool.globalInstance()

    def start_device_scan(self):
        """Starts the background service to discover ADB devices."""
        self.service.start_scanning()

    def stop_device_scan(self):
        """Stops the ADB device discovery service."""
        self.service.stop_scanning()

    def get_online_devices(self) -> List[Device]:
        """Returns a list of all currently connected devices."""
        return self.service.get_online_devices()

    def manually_update_status(self, device_uuid: str, status: DeviceStatus):
        """Manually overrides the status of a specific device."""
        return self.service.update_status(device_uuid, status)

    def on_device_state_change(self, device: Device):
        """Relays device connection/disconnection events to the UI."""
        self.device_state_changed.emit(device)

    def launch_scrcpy(self, devices: List[Device]):
        """
        Calculates a static grid layout and launches mirroring for a list of devices.

        Args:
            devices (List[Device]): The list of devices to mirror.
        """
        if not devices:
            return

        total_devices = len(devices)
        logger.info(f"📱 Calculating Grid Layout for {total_devices} devices...")

        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_w = screen_geometry.width()
        screen_h = screen_geometry.height()

        cols = math.ceil(math.sqrt(total_devices))
        rows = math.ceil(total_devices / cols) if cols > 0 else 1

        cell_w = screen_w // cols
        cell_h = screen_h // rows

        window_width = cell_w + 10
        window_height = cell_h + 30

        for index, device in enumerate(devices):
            if device.device_id in self._active_scrcpy_clients:
                logger.warning(
                    f"Scrcpy for device {device.device_id} is already running. Skipping..."
                )
                continue

            row = index // cols
            col = index % cols

            pos_x = screen_geometry.x() + (col * cell_w)
            pos_y = screen_geometry.y() + (row * cell_h)

            client = ScrcpyClient(device_id=device.device_id, user_id=0, parent=self)
            client.finished.connect(
                self._on_scrcpy_finished, Qt.ConnectionType.QueuedConnection
            )

            self._active_scrcpy_clients[device.device_id] = client

            client.start_mirroring(
                x=pos_x, y=pos_y, width=window_width, height=window_height
            )
            time.sleep(0.5)

    def launch_scrcpy_for_job(self, device: Device, max_concurrent_jobs: int):
        """
        Launches a single Scrcpy window into an available grid slot.

        Used by background workers to dynamically place windows based on the
        maximum worker capacity.

        Args:
            device (Device): The device to mirror.
            max_concurrent_jobs (int): The total capacity used to calculate grid dimensions.
        """
        if device.device_id in self._active_scrcpy_clients:
            logger.warning(f"Scrcpy for {device.device_id} is already running.")
            return

        occupied_slots = set(self._scrcpy_slots.values())
        slot_index = 0
        for i in range(max_concurrent_jobs):
            if i not in occupied_slots:
                slot_index = i
                break
        else:
            slot_index = len(occupied_slots)

        self._scrcpy_slots[device.device_id] = slot_index

        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_w = screen_geometry.width()
        screen_h = screen_geometry.height()

        cols = math.ceil(math.sqrt(max_concurrent_jobs))
        rows = math.ceil(max_concurrent_jobs / cols) if cols > 0 else 1

        cell_w = screen_w // cols
        cell_h = screen_h // rows
        window_width = cell_w + 10
        window_height = cell_h + 30

        row = slot_index // cols
        col = slot_index % cols
        pos_x = screen_geometry.x() + (col * cell_w)
        pos_y = screen_geometry.y() + (row * cell_h)

        client = ScrcpyClient(device_id=device.device_id, user_id=0, parent=self)
        client.finished.connect(
            self._on_scrcpy_finished, Qt.ConnectionType.QueuedConnection
        )

        self._active_scrcpy_clients[device.device_id] = client
        client.start_mirroring(
            x=pos_x, y=pos_y, width=window_width, height=window_height
        )
        time.sleep(0.5)

    def take_screenshot(self, devices: List[Device]) -> bool:
        """
        Dispatches parallel screenshot requests for multiple devices to the QThreadPool.

        This method iterates through a list of devices, instantiates a ScreenshotTask
        for each, and manages thread-safe signal connections to handle results
        asynchronously.

        Args:
            devices (List[Device]): A list of device entities to capture.

        Returns:
            bool: True if tasks were successfully dispatched, False if the device list was empty.
        """
        if not devices:
            return False

        output_dir = settings.repositories.screen_shot_dir  # type: ignore
        logger.info(f"📸 Dispatching screenshot requests for {len(devices)} devices...")

        for device in devices:
            task = ScreenshotTask(device.device_id, output_dir)

            task.signals.success.connect(self._on_screenshot_success)
            task.signals.error.connect(self._on_screenshot_error)

            self.thread_pool.start(task)

        return True

    def is_scrcpy_running(self, device_id: str) -> bool:
        """Checks if a Scrcpy window is currently active for the given device."""
        return device_id in self._active_scrcpy_clients

    def _on_scrcpy_finished(self, device_id: str, exit_code: int):
        """Handles resource cleanup and slot release when a mirroring window closes."""
        if device_id in self._active_scrcpy_clients:
            client = self._active_scrcpy_clients.pop(device_id)
            client.deleteLater()

            if device_id in self._scrcpy_slots:
                self._scrcpy_slots.pop(device_id)

            msg = f"⭕ Closed Scrcpy for device {device_id} (Exit Code: {exit_code})"
            logger.info(msg)

    def enable_redsocks(
        self,
        devices: List[Device],
        ip: str,
        port: int,
        username: str = "",
        password: str = "",
        ptype: str = "http-connect",
    ):
        """
        Spawns background workers to enable Redsocks proxy on multiple devices.
        """
        for device in devices:
            task_name = f"enable_redsocks_{device.device_id}"
            if task_name in self._active_workers:
                logger.warning(
                    f"Redsocks for device {device.device_id} is already running. Skipping..."
                )
                continue
            driver = RedsocksDriver(device.device_id)
            worker = GenericWorker(
                task_name=task_name,
                target_func=driver.enable,
                ip=ip,
                port=port,
                username=username,
                password=password,
                ptype=ptype,
            )
            worker.success.connect(self._on_redsocks_enable_success)
            worker.error.connect(self._on_proxy_error)
            worker.finished.connect(worker.deleteLater)

            worker.finished.connect(
                lambda t=task_name: self._active_workers.pop(t, None)
            )

            self._active_workers[task_name] = {
                "worker": worker,
                "device": device,
                "action": "enable",
            }
            worker.start()

    def disable_redsocks(self, devices: List[Device]):
        """
        Spawns background workers to disable Redsocks proxy and restore direct network.
        """
        for device in devices:
            task_name = f"disable_proxy_{device.device_id}"
            if task_name in self._active_workers:
                continue

            driver = RedsocksDriver(device.device_id)
            worker = GenericWorker(task_name=task_name, target_func=driver.disable)

            worker.success.connect(self._on_redsocks_disable_success)
            worker.error.connect(self._on_proxy_error)
            worker.finished.connect(worker.deleteLater)
            
            self._active_workers[task_name] = {"worker": worker, "device": device, "action": "disable"}
            worker.start()

    def _on_redsocks_enable_success(self, task_name: str, result: str):
        """
        Processes the successful completion of a proxy activation task.

        This callback validates the result of the Redsocks activation. If the
        result indicates a specific failure state (e.g., lack of Root, connection
        failure), it emits a failure signal. Otherwise, it updates the system
        with the new proxy IP address and emits a success signal.

        Args:
            task_name (str): The unique identifier of the worker task.
            result (str): The outcome message or the new public IP address.
        """
        if task_name not in self._active_workers:
            return

        device = self._active_workers[task_name]["device"]

        if result in ["NO_ROOT", "START_FAILED", "NO_INTERNET"]:
            logger.error(f"[{device.device_name}] Failed to enable proxy: {result}")
            self.redsocks_enable_failed.emit(device, result)
        else:
            logger.success(f"[{device.device_name}] Proxy connected! IP: {result}")
            self.redsocks_enable_success.emit(device, result)

    def _on_redsocks_disable_success(self, task_name: str, result: Any):
        """
        Processes the successful completion of a proxy deactivation task.

        Confirms that Redsocks has been stopped and the device routing has
        returned to its normal state.

        Args:
            task_name (str): The unique identifier of the worker task.
            result (Any): The result returned by the worker (typically ignored on success).
        """
        if task_name not in self._active_workers:
            return

        device = self._active_workers[task_name]["device"]

        logger.info(f"[{device.device_name}] Proxy disabled successfully.")
        self.redsocks_disable_success.emit(device)

    def _on_proxy_error(self, task_name: str, error_msg: str):
        """
        Handles unexpected exceptions encountered during proxy configuration tasks.

        This method catches high-level execution errors (like worker crashes or
        process timeouts) and routes the error signal based on whether the
        original action was to 'enable' or 'disable' the proxy.

        Args:
            task_name (str): The unique identifier of the worker task.
            error_msg (str): The detailed error message or traceback.
        """
        if task_name not in self._active_workers:
            return

        device = self._active_workers[task_name]["device"]
        action = self._active_workers[task_name]["action"]

        logger.error(
            f"[{device.device_name}] Error running proxy {action} task: {error_msg}"
        )

        if action == "enable":
            self.redsocks_enable_failed.emit(device, error_msg)

    def _on_screenshot_success(self, device_id: str, path: str):
        """
        Handles successful screenshot capture for a specific device.

        This callback is triggered when a ScreenshotTask completes without errors.
        It logs the file location and notifies the UI via a signal.

        Args:
            device_id (str): The unique identifier of the Android device.
            path (str): The absolute local path where the screenshot was saved.
        """
        msg = f"📸 [{device_id}] Screenshot saved at: {path}"
        logger.info(msg)
        self.msg_signal.emit

    def _on_screenshot_error(self, device_id: str, error: str):
        """
        Handles failures encountered during the screenshot capture process.

        Logs the error details for debugging and notifies the UI to update
        the device status or alert the user.

        Args:
            device_id (str): The unique identifier of the Android device.
            error (str): The error message or exception details.
        """
        msg = f"❌ [{device_id}] Screenshot failed: {error}"
        logger.error(msg)
        self.msg_signal.emit(msg)
