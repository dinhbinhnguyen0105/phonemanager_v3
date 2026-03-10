# src/controllers/user_controller.py
from typing import List, Dict, Any
from PySide6.QtCore import QObject, QThreadPool, Signal
from src.services.user_service import UserService
from src.tasks.get_users_worker import GetUsersWorker
from src.utils.logger import logger
from src.entities import Device

class UserController(QObject):
    sync_completed = Signal(str)
    sync_failed = Signal(str)

    def __init__(self, service: UserService):
        super().__init__()
        self.user_service = service
        self.thread_pool = QThreadPool.globalInstance()

    def fetch_users_for_device(self, device: Device):
        worker = GetUsersWorker(device_id=device.device_id)
        
        worker.signals.success.connect(
            lambda users_data: self._on_fetch_success(device, users_data)
        )
        worker.signals.error.connect(self._on_fetch_error)
        
        self.thread_pool.start(worker)

    def _on_fetch_success(self, device: Device, users_data: List[Dict[str, Any]]):
        logger.success(f"Đã lấy thành công {len(users_data)} profiles từ thiết bị.")
        self.user_service.sync_users_from_adb_data(device, users_data)
        # self.sync_completed.emit(device_uuid)

    def _on_fetch_error(self, error_msg: str):
        logger.error(f"Lấy danh sách user thất bại: {error_msg}")
        self.sync_failed.emit(error_msg)