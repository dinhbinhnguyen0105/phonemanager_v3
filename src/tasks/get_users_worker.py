# src/tasks/get_users_worker.py
from PySide6.QtCore import QObject, Signal, QRunnable
from src.drivers.adb.controller import ADBController
from src.utils.logger import logger

class GetUsersSignals(QObject):
    success = Signal(list)
    error = Signal(str)

class GetUsersWorker(QRunnable):
    """
    Luồng nền độc lập dùng để lấy danh sách User từ thiết bị qua ADB.
    """
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
        self.signals = GetUsersSignals()

    def run(self):
        try:
            adb_controller = ADBController(self.device_id)
            users_data = adb_controller.get_users()
            self.signals.success.emit(users_data)
        except Exception as e:
            logger.error(f"[GetUsersWorker] Lỗi khi lấy danh sách user từ {self.device_id}: {e}")
            self.signals.error.emit(str(e))