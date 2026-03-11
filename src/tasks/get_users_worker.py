# src/tasks/get_users_worker.py
from typing import List
from PySide6.QtCore import QObject, Signal, QRunnable
from src.drivers.adb.controller import ADBController
from src.utils.logger import logger
from src.entities import User, Device # Thêm import Device
from src.constants import UserStatus

class GetUsersSignals(QObject):
    # Thay vì truyền list, giờ truyền cả Device (object) và list
    success = Signal(object, list) 
    error = Signal(object, str)

class GetUsersWorker(QRunnable):
    # Đổi tham số nhận vào thành Device
    def __init__(self, device: Device): 
        super().__init__()
        self.device = device
        self.signals = GetUsersSignals()

    def run(self):
        try:
            adb_controller = ADBController(self.device.device_id)
            users_data = adb_controller.get_users()
            results: List[User] = []
            for user_data in users_data:
                user = User(
                    user_id=int(user_data.get("user_id", 0)),
                    user_name=user_data.get("user_name", "Unknown User"),
                    user_status=UserStatus(user_data.get("user_status", UserStatus.INACTIVE.value)),
                )
                results.append(user)

            # Phóng tín hiệu mang theo Device và mảng User
            self.signals.success.emit(self.device, results)
        except Exception as e:
            logger.error(f"[GetUsersWorker] Lỗi khi lấy danh sách user từ {self.device.device_id}: {e}")
            self.signals.error.emit(self.device, str(e))