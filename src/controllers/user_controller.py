from typing import List, Dict, Any
from PySide6.QtCore import QObject, QThreadPool, Signal
from src.services.user_service import UserService
from src.tasks.get_users_worker import GetUsersWorker
from src.utils.logger import logger
from src.entities import Device, User

class UserController(QObject):
    # Đổi dict thành (object, list) để tránh lỗi kẹt Queue
    sync_completed = Signal(object, list) 
    sync_failed = Signal(str)

    def __init__(self, service: UserService):
        super().__init__()
        self.user_service = service
        self.thread_pool = QThreadPool.globalInstance()
        self._active_workers: Dict[str, GetUsersWorker] = {}

    def fetch_users_for_device(self, device: Device):
        """Starts a background worker to fetch user profiles via ADB."""
        # Truyền thẳng đối tượng Device vào
        worker = GetUsersWorker(device=device)

        # KẾT NỐI TRỰC TIẾP (QUAN TRỌNG NHẤT)
        # Vì _on_fetch_success thuộc Main Thread, Qt sẽ đẩy luồng an toàn!
        worker.signals.success.connect(self._on_fetch_success)
        worker.signals.error.connect(self._on_fetch_error)

        self._active_workers[device.device_id] = worker
        self.thread_pool.start(worker)

    def _on_fetch_success(self, device: Device, users_data: List[User]):
        """Bây giờ hàm này ĐẢM BẢO 100% ĐANG CHẠY TRÊN MAIN THREAD"""
        if device.device_id in self._active_workers:
            del self._active_workers[device.device_id]
            
        logger.success(f"Successfully retrieved {len(users_data)} profiles from device: {device.device_id}")
        
        # Gọi xuống Database (sẽ không bao giờ bị kẹt nữa)
        self.user_service.sync_users_from_adb_data(device, users_data) 
    
        # Bắn 2 tham số ra UI
        self.sync_completed.emit(device, users_data)

    def _on_fetch_error(self, device: Device, error_msg: str):
        if device.device_id in self._active_workers:
            del self._active_workers[device.device_id]
            
        logger.error(f"Failed to fetch user list: {error_msg}")
        self.sync_failed.emit(error_msg)