# core\entities.py
import json
import uuid
import time
from enum import Enum
from typing import Optional, Any, Dict, Type, TypeVar

from dataclasses import dataclass, asdict, field
from .constants import DeviceStatus, UserStatus, ProxyType, ProxyStatus, JobStatus, JobAction, Platform

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


@dataclass
class Social(BaseEntity):
    user_uuid: str = ""
    social_id: str = ""
    social_name: str = "New social"
    social_password: str = field(default="")
    social_status: int = 0
    social_group: int = 0
    social_platform: str = "facebook"


@dataclass
class Proxy(BaseEntity):
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    rotate_url: str = ""
    proxy_type: ProxyType = ProxyType.STATIC
    proxy_status: ProxyStatus = ProxyStatus.AVAILABLE

    def __post_init__(self):
        if isinstance(self.proxy_type, str):
            try:
                self.proxy_type = ProxyType(self.proxy_type.lower()) 
            except ValueError:
                self.proxy_type = ProxyType.STATIC
        if isinstance(self.proxy_status, str):
            try:
                self.proxy_status = ProxyStatus(self.proxy_status.lower())
            except ValueError:
                self.proxy_status = ProxyStatus.AVAILABLE
        if isinstance(self.rotate_url, str):
            self.rotate_url = self.rotate_url.strip()

@dataclass
class Job(BaseEntity):
    name: str = "Unnamed Job"
    social_uuid: str = ""
    device_uuid: str = ""
    user_uuid: str = ""
    
    platform: Platform = Platform.FACEBOOK
    action: JobAction = JobAction.FB__SCROLL_FEED
    status: JobStatus = JobStatus.PENDING
    
    parameters: Dict[str, Any] = field(default_factory=dict)
    log_message: str = ""

    def __post_init__(self):
        if isinstance(self.platform, str):
            try:
                self.platform = Platform(self.platform.lower())
            except ValueError:
                self.platform = Platform.FACEBOOK
                
        if isinstance(self.action, str):
            try:
                self.action = JobAction(self.action.lower())
            except ValueError:
                self.action = JobAction.FB__SCROLL_FEED
                
        if isinstance(self.status, str):
            try:
                self.status = JobStatus(self.status.lower())
            except ValueError:
                self.status = JobStatus.PENDING

    # @property
    # def params_dict(self) -> dict:
    #     try:
    #         return json.loads(self.parameters)
    #     except Exception:
    #         return {}

    # def set_params(self, params_dict: dict):
    #     self.parameters = json.dumps(params_dict, ensure_ascii=False)

@dataclass
class RealEstateProduct:
    id: Optional[str]
    pid: Optional[str]
    status: bool
    transaction_type: int
    province: int
    district: int
    ward: int
    street: str
    category: int
    area: float
    price: float
    legal: int
    structure: float
    function: str
    building_line: int
    furniture: int
    description: str
    created_at: Optional[str]
    updated_at: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data

@dataclass
class RealEstateTemplateType:
    id: Optional[str]
    transaction_type: int
    part: int # 0: title, 1: description
    category: int
    value: str
    is_default: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data