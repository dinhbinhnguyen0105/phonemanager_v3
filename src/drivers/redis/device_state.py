# src/drivers/redis/device_state.py
from typing import List
from src.entities import DeviceStatus
from src.constants import DeviceStatus
from src.drivers.redis.base_state import BaseState


class DeviceState(BaseState):
    def __init__(self, redis_client, ):
        super().__init__(redis_client, namespace='farm:device')
    
    def get_all_online(self) -> List[str]:
        return list(self.smembers(DeviceStatus.ONLINE))

    def set_online(self, device_id: str, status: DeviceStatus = DeviceStatus.ONLINE) -> None:
        self.sadd(DeviceStatus.ONLINE, device_id)
        self.hset_dict(f"info:{device_id}", {
            "status": status,
            "current_job": "none", 
        })
    
    def set_offline(self, device_id: str) -> None:
        self.srem(DeviceStatus.ONLINE, device_id)
        self.delete(f"info:{device_id}")
    
    def update_working_status(self, device_id: str, job_uuid: str) -> None:
        self.hset_dict(f"info:{device_id}", {
            "status": DeviceStatus.WORKING,
            "current_job": job_uuid, 
        })
    
    def update_error_status(self, device_id: str, error_msg: str) -> None:
        self.hset_dict(f"info:{device_id}", {
            "status": DeviceStatus.ERROR,
            "error_msg": error_msg, 
        })