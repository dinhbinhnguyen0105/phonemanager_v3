# core\entities.py
import json
import uuid
import time
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, Type, TypeVar

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Type, TypeVar, Optional
from src.constants import (
    DeviceStatus,
    UserStatus,
    ProxyType,
    ProxyStatus,
    JobStatus,
    JobAction,
    Platform,
    Product__Status,
    RealEstateProduct__TransactionType,
    RealEstateProduct__Province,
    RealEstateProduct__District,
    RealEstateProduct__Ward,
    RealEstateProduct__Category,
    RealEstateProduct__Unit,
    RealEstateProduct__Legal,
    RealEstateProduct__BuildingLine,
    RealEstateProduct__Furniture,
    RealEstateTemplate__Name,
)

T = TypeVar("T", bound="BaseEntity")


@dataclass
class BaseEntity:
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def mark_created(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

    def touch(self) -> None:
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


@dataclass
class RealEstateProduct(BaseEntity):
    """
    Represents a real estate listing with detailed technical specifications and status.
    """

    id: Optional[str] = None
    pid: str = ""
    status: Product__Status = Product__Status.PAUSED
    transaction_type: RealEstateProduct__TransactionType = (
        RealEstateProduct__TransactionType.SALE
    )
    province: RealEstateProduct__Province = RealEstateProduct__Province.LAM_DONG
    district: RealEstateProduct__District = RealEstateProduct__District.DA_LAT
    ward: RealEstateProduct__Ward = RealEstateProduct__Ward.PHUONG_1
    street: str = ""
    category: RealEstateProduct__Category = RealEstateProduct__Category.TOWNHOUSE
    area: float = 0.0
    price: float = 0.0
    unit: RealEstateProduct__Unit = RealEstateProduct__Unit.BILLION
    legal: RealEstateProduct__Legal = RealEstateProduct__Legal.PRIVATE_CONSTRUCTION_DEED
    structure: float = 0.0
    function: str = ""
    building_line: RealEstateProduct__BuildingLine = (
        RealEstateProduct__BuildingLine.MOTORBIKE_ACCESS_ROAD
    )
    furniture: RealEstateProduct__Furniture = RealEstateProduct__Furniture.NO_FURNITURE
    description: str = ""

    def __post_init__(self):
        def parse_enum(value, enum_cls, default):
            if isinstance(value, str):
                try:
                    return enum_cls(value.lower())
                except ValueError:
                    return default
            return value

        self.status = parse_enum(self.status, Product__Status, Product__Status.PAUSED)
        self.transaction_type = parse_enum(
            self.transaction_type,
            RealEstateProduct__TransactionType,
            RealEstateProduct__TransactionType.SALE,
        )
        self.province = parse_enum(
            self.province,
            RealEstateProduct__Province,
            RealEstateProduct__Province.LAM_DONG,
        )
        self.district = parse_enum(
            self.district,
            RealEstateProduct__District,
            RealEstateProduct__District.DA_LAT,
        )
        self.ward = parse_enum(
            self.ward, RealEstateProduct__Ward, RealEstateProduct__Ward.PHUONG_1
        )
        self.category = parse_enum(
            self.category,
            RealEstateProduct__Category,
            RealEstateProduct__Category.TOWNHOUSE,
        )
        self.unit = parse_enum(
            self.unit, RealEstateProduct__Unit, RealEstateProduct__Unit.BILLION
        )
        self.legal = parse_enum(
            self.legal,
            RealEstateProduct__Legal,
            RealEstateProduct__Legal.PRIVATE_CONSTRUCTION_DEED,
        )
        self.building_line = parse_enum(
            self.building_line,
            RealEstateProduct__BuildingLine,
            RealEstateProduct__BuildingLine.MOTORBIKE_ACCESS_ROAD,
        )
        self.furniture = parse_enum(
            self.furniture,
            RealEstateProduct__Furniture,
            RealEstateProduct__Furniture.NO_FURNITURE,
        )
@dataclass
class RealEstateTemplate(BaseEntity):
    """
    Template for generating real estate listing content like titles or descriptions.
    """

    id: Optional[str] = None
    transaction_type: RealEstateProduct__TransactionType = (
        RealEstateProduct__TransactionType.SALE
    )
    name: RealEstateTemplate__Name = RealEstateTemplate__Name.TITLE
    category: RealEstateProduct__Category = RealEstateProduct__Category.TOWNHOUSE
    value: str = ""
    is_default: bool = False

    def __post_init__(self):
        self.is_default = bool(self.is_default)
        if isinstance(self.transaction_type, str):
            try:
                # Handle case where it might be a digit string or the enum name
                self.transaction_type = RealEstateProduct__TransactionType(self.transaction_type.lower())
            except ValueError:
                self.transaction_type = RealEstateProduct__TransactionType.SALE

        if isinstance(self.name, str):
            try:
                self.name = RealEstateTemplate__Name(self.name.lower())
            except ValueError:
                self.name = RealEstateTemplate__Name.TITLE

        if isinstance(self.category, str):
            try:
                self.category = RealEstateProduct__Category(self.category.lower())
            except ValueError:
                self.category = RealEstateProduct__Category.TOWNHOUSE