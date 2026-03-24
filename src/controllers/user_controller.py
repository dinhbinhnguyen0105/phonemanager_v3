# src/controllers/user_controller.py
from typing import List, Dict, Any, Optional
from PySide6.QtCore import Signal

from src.controllers.base_controller import BaseController
from src.services.user_service import UserService
from src.utils.logger import logger
from src.entities import Device, User, Social
from src.constants import UserStatus
from src.drivers.adb.adb_controller import ADBController
from src.worker.generic_worker import GenericWorker 


class UserController(BaseController[User]):
    user_sync_completed = Signal(object, list) 
    user_sync_failed = Signal(str)

    user_switched = Signal(object, object) # Device, User
    app_installed = Signal(object, str, bool) # Device, apk name, is_success
    social_linked = Signal(object, object, str) # Device, User, platform_name

    def __init__(self, service: UserService):
        super().__init__(service)
        self.service = service
        self._active_workers: Dict[str, dict] = {}

    def fetch_users_for_device(self, device: Device):
        task_name = f"fetch_users_{device.device_id}"
        if task_name in self._active_workers:
            logger.warning(f"{device.device_name} is already being scanned. Skipping...")
            return

        adb_controller = ADBController(device.device_id)
        worker = GenericWorker(
            task_name=task_name,
            target_func=adb_controller.get_users
        )
        worker.success.connect(self._on_fetch_success)
        worker.error.connect(self._on_fetch_error)
        worker.finished.connect(worker.deleteLater)
        self._active_workers[task_name] = {
            "worker": worker,
            "device": device
        }
        worker.start()
    
    def create_new_user(self, device: Device, username: str):
        task_name = f"create_new_user_{device.device_id}"
        if task_name in self._active_workers:
            logger.warning(f"{device.device_name} is already create new user. Skipping...")
            return
        
        adb_controller = ADBController(device.device_id)
        worker = GenericWorker(
            task_name=task_name,
            target_func=adb_controller.create_user,
            username=username
        )
        worker.success.connect(self._on_create_user_success)
        worker.error.connect(self._on_create_user_error)
        worker.finished.connect(worker.deleteLater)
        self._active_workers[task_name] = {
            "worker": worker,
            "device": device
        }
        worker.start()
    
    def delete_user(self, device: Optional[Device], user: User):
        task_name = f"delete_user_{user.device_uuid}"
        if task_name in self._active_workers:
            logger.warning(f"{user.user_name} is already being deleted. Skipping...")
            return
        
        if not device:
            self.service.delete(user.uuid)
            logger.success(f"Successfully deleted user: {user.user_name} (ID: {user.user_id})")
            self.user_sync_completed.emit(None, [])
            return
        
        adb_controller = ADBController(device.device_id)
        worker = GenericWorker(
            task_name=task_name,
            target_func=adb_controller.remove_user,
            user_id=user.user_id
        )
        worker.success.connect(lambda task_name, result: self._on_delete_user_success(task_name, result, user))
        worker.error.connect(self._on_delete_user_error)
        worker.finished.connect(worker.deleteLater)
        self._active_workers[task_name] = {
            "worker": worker,
            "device": device
        }
        worker.start()

    def _on_fetch_success(self, task_name: str, result: Any):
        if task_name not in self._active_workers:
            return
        device = self._active_workers[task_name]["device"]
        del self._active_workers[task_name]
        users_data: List[User] = []
        for user_data in result:
            user = User(
                user_id=int(user_data.get("user_id", 0)),
                user_name=user_data.get("user_name", "Unknown User"),
                user_status=UserStatus(user_data.get("user_status", UserStatus.INACTIVE.value)),
            )
            users_data.append(user)

        logger.success(f"Successfully retrieved {len(users_data)} profiles from device: {device.device_id}")
        self.service.sync_users_from_adb_data(device, users_data) 
        self.user_sync_completed.emit(device, users_data)

    def _on_fetch_error(self, task_name: str, error_msg: str):
        if task_name not in self._active_workers:
            return
            
        del self._active_workers[task_name]
            
        logger.error(f"Failed to fetch user list: {error_msg}")
        self.user_sync_failed.emit(error_msg)
    
    def _on_create_user_success(self, task_name: str, new_user: User):
        if task_name not in self._active_workers:
            return
        device = self._active_workers[task_name]["device"]
        del self._active_workers[task_name]

        if new_user:
            new_user.device_uuid = device.uuid
            logger.success(f"Successfully created new user: {new_user.user_name} (ID: {new_user.user_id})")
            self.service.create(new_user)
            self.user_sync_completed.emit(device, [new_user]) 
        else:
            _msg = "Failed to create new user"
            logger.warning(_msg)
            self.user_sync_failed.emit(_msg)

        
    def _on_create_user_error(self, task_name: str, error_msg: str=""):
        if task_name not in self._active_workers:
            return
        del self._active_workers[task_name]
        _msg = f"Failed to create new user: {error_msg}" if error_msg else "Failed to create new user"
        logger.error(_msg)
        self.user_sync_failed.emit(_msg)
    
    def _on_delete_user_success(self, task_name: str, result: Any, user: User):
        if task_name not in self._active_workers:
            return
        device = self._active_workers[task_name]["device"]
        del self._active_workers[task_name]
        
        if result:
            self.service.delete(user.uuid)
        logger.success(f"Successfully deleted user from device: {device.device_id}")
        self.user_sync_completed.emit(device, [])
    
    def _on_delete_user_error(self, task_name: str, error_msg: str):
        if task_name not in self._active_workers:
            return
        del self._active_workers[task_name]
        _msg = f"Failed to create new user: {error_msg}" if error_msg else "Failed to create new user"
        logger.error(_msg)
        self.user_sync_failed.emit(_msg)

    def switch_user(self, device: Device, user: User):
        task_name = f"switch_user_{device.device_id}_{user.user_id}"
        if task_name in self._active_workers:
            logger.warning(f"Device {device.device_name} is already switching user. Skipping...")
            return
            
        adb_controller = ADBController(device.device_id)
    
        worker = GenericWorker(
            task_name=task_name,
            target_func=adb_controller.switch_user, 
            user_id=user.user_id
        )
        worker.success.connect(lambda t_name, result: self._on_switch_success(t_name, result, device, user))
        worker.error.connect(lambda t_name, err: self._on_switch_error(t_name, err, device))
        worker.finished.connect(worker.deleteLater)
        
        self._active_workers[task_name] = {"worker": worker, "device": device}
        worker.start()

    def install_app(self, device: Device, users: List[User], app_name: str):
        task_name = f"install_app_{device.device_id}_{app_name}"
        if task_name in self._active_workers:
            logger.warning(f"Device {device.device_name} is already installing {app_name}. Skipping...")
            return
            
        adb_controller = ADBController(device.device_id)
        user_ids = [u.user_id for u in users]
        
        worker = GenericWorker(
            task_name=task_name,
            target_func=adb_controller.install_app_for_users, 
            app_name=app_name, 
            user_ids=user_ids
        )
        
        worker.success.connect(lambda t_name, result: self._on_install_success(t_name, result, device, app_name))
        worker.error.connect(lambda t_name, err: self._on_install_error(t_name, err, device, app_name))
        worker.finished.connect(worker.deleteLater)
        
        self._active_workers[task_name] = {"worker": worker, "device": device}
        worker.start()
        
    
    # --- Callbacks for Switch User ---
    def _on_switch_success(self, task_name: str, result: Any, device: Device, user: User):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        msg = f"✔️ Switched to user {user.user_name} on device {device.device_name}"
        logger.success(msg)
        # self.msg_signal.emit(msg)
        self.user_switched.emit(device, user)

    def _on_switch_error(self, task_name: str, error_msg: str, device: Device):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        logger.error(f"Failed to switch user on {device.device_name}: {error_msg}")

    # --- Callbacks for Install App ---
    def _on_install_success(self, task_name: str, result: Any, device: Device, app_name: str):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        logger.success(f"Installed {app_name} successfully on {device.device_name}")
        self.app_installed.emit(device, app_name, True)

    def _on_install_error(self, task_name: str, error_msg: str, device: Device, app_name: str):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        logger.error(f"Failed to install {app_name} on {device.device_name}: {error_msg}")
        self.app_installed.emit(device, app_name, False)

    # --- Callbacks for Link Social ---
    def _on_social_success(self, task_name: str, result: Any, device: Device, user: User, platform: str):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        logger.success(f"Opened {platform} for user {user.user_name} on {device.device_name}")
        self.social_linked.emit(device, user, platform)

    def _on_social_error(self, task_name: str, error_msg: str, device: Device, platform: str):
        if task_name in self._active_workers:
            del self._active_workers[task_name]
        logger.error(f"Failed to open {platform} on {device.device_name}: {error_msg}")