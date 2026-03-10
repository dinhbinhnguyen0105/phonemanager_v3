# src/repositories/device_repo.py
from typing import List, Optional
from src.repositories.base_repo import BaseRepository
from src.entities import Device
from src.constants import DeviceStatus

class DeviceRepository(BaseRepository[Device]):
    """Repository for managing device data."""
    
    def __init__(self, db_manager):
        super().__init__(
            db_manager=db_manager, 
            table_name="devices", 
            entity_class=Device, 
            pk_name="uuid",
            soft_delete=False
        )

    def get_by_status(self, status: DeviceStatus) -> List[Device]:
        """Retrieves a list of devices filtered by their status."""
        return self.get_many_by_fields({"device_status": status.value})
    
    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """Retrieves a single device by its unique device identifier."""
        return self.get_one_by_fields({"device_id": device_id})
    
    def save_or_update(self, device: Device):
        saved_device = self.get_by_device_id(device.device_id)
        if saved_device:
            self.update(Device(
                uuid=saved_device.uuid,
                device_id=saved_device.device_id,
                device_name=device.device_name,
                device_status=device.device_status,
                device_root=device.device_root,
                created_at=saved_device.created_at,
                updated_at=device.updated_at
            ))
        else:
            self.insert(device)