# src/controllers/user_controller.py
from typing import List, Dict

from PySide6.QtCore import QThreadPool, Signal, Qt
from src.controllers.base_controller import BaseController
from src.services.user_service import UserService
from src.tasks.get_users_worker import GetUsersWorker
from src.utils.logger import logger
from src.entities import Device, User

class UserController(BaseController[User]):
    user_sync_completed = Signal(object, list) 
    user_sync_failed = Signal(str)

    def __init__(self, service: UserService):
        super().__init__(service)
        self.service = service
        self.thread_pool = QThreadPool.globalInstance()
        self._active_workers: Dict[str, GetUsersWorker] = {}

    def fetch_users_for_device(self, device: Device):
        worker = GetUsersWorker(device=device)
        worker.signals.success.connect(self._on_fetch_success, Qt.ConnectionType.QueuedConnection)
        worker.signals.error.connect(self._on_fetch_error, Qt.ConnectionType.QueuedConnection)

        self._active_workers[device.device_id] = worker
        self.thread_pool.start(worker)

    def _on_fetch_success(self, device: Device, users_data: List[User]):
        if device.device_id in self._active_workers:
            del self._active_workers[device.device_id]
        logger.success(f"Successfully retrieved {len(users_data)} profiles from device: {device.device_id}")
        self.service.sync_users_from_adb_data(device, users_data) 
        self.user_sync_completed.emit(device, users_data)

    def _on_fetch_error(self, device: Device, error_msg: str):
        if device.device_id in self._active_workers:
            del self._active_workers[device.device_id]
            
        logger.error(f"Failed to fetch user list: {error_msg}")
        self.user_sync_failed.emit(error_msg)
        