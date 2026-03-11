# core\entities.py
import uuid
import time
from enum import Enum
from typing import Optional, Any, Dict, Type, TypeVar

from dataclasses import dataclass, asdict, field
from .constants import DeviceStatus, UserStatus, ProxyType, ProxyStatus

T = TypeVar("T", bound="BaseEntity")


@dataclass
class BaseEntity:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    def mark_created(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        now = int(time.time())
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

    def touch(self) -> None:
        self.updated_at = int(time.time())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> Optional[T]:
        if not data:
            return None
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)


@dataclass
class Device(BaseEntity):
    device_id: str = ""
    device_name: str = "New device"
    device_status: DeviceStatus = DeviceStatus.OFFLINE
    device_root: int = 0


@dataclass
class User(BaseEntity):
    user_id: int = 0
    user_name: str = "New profile"
    user_status: UserStatus = UserStatus.INACTIVE
    device_uuid: str = field(default="")
    social_uuid: str = field(default="")


@dataclass
class Social(BaseEntity):
    social_id: int = 0
    social_name: str = "New social"
    social_password: str = field(default="")
    social_status: int = 0
    social_group: int = 0


@dataclass
class Proxy(BaseEntity):
    proxy_id: int = 0
    value: str = ""
    proxy_type: ProxyType = ProxyType.STATIC
    proxy_status: ProxyStatus = ProxyStatus.AVAILABLE
