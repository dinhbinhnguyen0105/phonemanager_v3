# src/tasks/scan_device_info.py
import time
from PySide6.QtCore import QObject, Signal
from adbutils import adb
from src.utils.logger import logger
from src.constants import DeviceStatus
from src.entities import Device

class ScanDeviceInfo(QObject):
    finished = Signal()
    device_info = Signal(object)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        logger.info("Starting device scanning thread (Polling mode)...")
        try:
            adb.server_version()
            known_devices = {}

            while self._is_running:
                current_devices = adb.list()
                current_state = {d.serial: d.state for d in current_devices}
                for serial, state in current_state.items():
                    if serial not in known_devices:
                        # logger.debug(f"[Scanner] 🟢 NEW device detected: {serial} | State: {state}")
                        self._emit_device_event(serial, state, is_connected=True)
                    elif known_devices[serial] != state:
                        logger.debug(f"[Scanner] 🟡 Device {serial} STATE CHANGED: {known_devices[serial]} -> {state}")
                        self._emit_device_event(serial, state, is_connected=True)
                for serial in list(known_devices.keys()):
                    if serial not in current_state:
                        # logger.debug(f"[Scanner] 🔴 Device UNPLUGGED or disconnected: {serial}")
                        self._emit_device_event(serial, known_devices[serial], is_connected=False)
                        
                known_devices = current_state
                time.sleep(1)

        except Exception as e:
            logger.error(f"Device scanning error: {e}")
        finally:
            logger.info("Device scanning thread closed safely.")
            self.finished.emit()

    def _emit_device_event(self, serial: str, state: str, is_connected: bool):
        device_status = DeviceStatus.OFFLINE
        device_root = 0
        device_name = "Unknown Device"

        if is_connected:
            if state == "device":
                device_status = DeviceStatus.ONLINE
                device_root = self.check_root(serial)
                device_name = self.get_device_model_info(serial)
            elif state == "unauthorized":
                device_status = DeviceStatus.AUTHORIZING
            
        device = Device(
            device_id=serial,
            device_name=device_name,
            device_status=device_status if is_connected else DeviceStatus.OFFLINE,
            device_root=device_root,
        )
        
        self.device_info.emit(device)

    def check_root(self, device_id: str) -> bool:
        try:
            su_check = adb.device(device_id).shell("su -c 'echo is_rooted'").strip()
            if "is_rooted" in su_check:
                return True
            return False
        except Exception as e:
            logger.error(str(e))
            return False

    def get_device_model_info(self, device_id: str) -> str:
        try:
            brand = adb.device(device_id).shell("getprop ro.product.brand").strip()
            model = adb.device(device_id).shell("getprop ro.product.model").strip()
            return f"{brand.upper()} {model}"
        except Exception as e:
            logger.error(str(e))
            return "Unknown Device"

    def stop(self):
        logger.info("Receiving command to stop device scanning thread...")
        self._is_running = False