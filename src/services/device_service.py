# src/services/device_service.py
from typing import List, TYPE_CHECKING
from PySide6.QtCore import QThread, Signal, QObject
from src.services.base_service import BaseService
from src.entities import Device
from src.constants import DeviceStatus
from src.repositories.device_repo import DeviceRepository
from src.tasks.scan_device_info import ScanDeviceInfo
if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade

class DeviceSignals(QObject):
    data_changed__devices = Signal()
    device_connected = Signal(Device)
    device_disconnected = Signal(Device)

class DeviceService(BaseService[Device]):
    """
    Service layer for managing Device-related business logic.
    Handles validation, status management, and integration with the repository.
    """
    
    def __init__(self, repository: "DeviceRepository", redis_facade: "RedisStateFacade"):
        BaseService.__init__(self, repository, redis_facade)
        self.signals = DeviceSignals()
        self.scan_thread = QThread()
        self.repo = repository
        self.redis_facade = redis_facade
        self.scan_worker = ScanDeviceInfo()
        self._setup_background_task()
        

    def validate_create(self, entity: Device) -> None:
        """
        Validates that no other device exists with the same device_id (ADB ID).
        
        :param entity: The Device entity to validate.
        :raises ValueError: If a device with the same ID already exists.
        """
        existing = self.repo.get_by_device_id(entity.device_id)
        if existing:
            raise ValueError(f"Device with ID '{entity.device_id}' already exists.")

    def get_online_devices(self) -> List[Device]:
        """
        Retrieves a list of all devices that are currently in the ONLINE state.
        
        :return: A list of online Device entities.
        """
        return self.repo.get_by_status(DeviceStatus.ONLINE)

    def update_status(self, device_uuid: str, new_status: DeviceStatus) -> bool:
        """
        Updates the status of a specific device by its UUID.
        
        :param device_uuid: The unique identifier of the device.
        :param new_status: The new status to be assigned.
        :return: True if the update was successful, False otherwise.
        """
        device = self.get_by_id(device_uuid)
        if not device:
            return False
            
        device.device_status = new_status
        return self.update(device)
    
    def reset_all_devices_status(self):
        online_devices = self.get_online_devices()
        for device in online_devices:
            device.device_status = DeviceStatus.OFFLINE
            self.update(device)
            self.redis_facade.devices.set_offline(device.device_id)
    
    def _setup_background_task(self):
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.finished.connect(self.scan_worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_worker.device_info.connect(self.handle_device_connected)
        # self.scan_worker.device_disconnected.connect(self.handle_device_disconnected)
    
    def start_scanning(self):
        self.reset_all_devices_status()
        if not self.scan_thread.isRunning():
            self.scan_thread.start()

    def stop_scanning(self):
        self.reset_all_devices_status()
        self.scan_worker.stop()
        if self.scan_thread.isRunning():
            self.scan_thread.terminate()
            self.scan_thread.wait()

    def handle_device_connected(self, device: Device):
        # Device(uuid='4450471c-58f0-400c-bf2d-d84623db2ff1', created_at=None, updated_at=None, device_id='521088a9eab064f9', device_name='SAMSUNG Samsung Galaxy J7 Prime', device_status=<DeviceStatus.ONLINE: 'online'>, device_root=True)
        self.repo.save_or_update(device)
        if device.device_status == DeviceStatus.ONLINE:
            self.redis_facade.devices.set_online(device.device_id)
            self.signals.device_connected.emit(device)
        elif device.device_status == DeviceStatus.OFFLINE:
            self.redis_facade.devices.set_offline(device.device_id)
            self.signals.device_disconnected.emit(device)