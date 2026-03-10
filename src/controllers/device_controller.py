# src/controllers/device_controller.py
from typing import List
from PySide6.QtCore import Signal, QObject
from src.services.device_service import DeviceService
from src.entities import Device
from src.controllers.base_controller import BaseController


class DeviceController(BaseController[Device]):
    device_state_changed = Signal(Device)
    def __init__(self, service: DeviceService):
        super().__init__(service)
        self.service = service
        self.service.signals.device_connected.connect(self.on_device_change_state)
        self.service.signals.device_disconnected.connect(self.on_device_change_state)
        
    def start_device_scan(self):
        self.service.start_scanning()
        
    def stop_device_scan(self):
        self.service.stop_scanning()

    def get_online_devices(self) -> List[Device]:
        return self.service.get_online_devices()
    
    def manually_update_status(self, device_uuid: str, status: str):
        return self.service.update_status(device_uuid, status)

    def on_device_change_state(self, device: Device):
        self.device_state_changed.emit(device)
    