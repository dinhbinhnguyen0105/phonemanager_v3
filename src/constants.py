# core\constants.py
from enum import Enum

class RedisQueue(str, Enum):
    DEVICE_EVENTS = "farm:device_events:queue"

    JOB_PENDING = "farm:job_pending:queue"
    JOB_RESULTS = "farm:job_results:queue"
    PROXY_EVENTS = "farm:proxy_events:queue"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DeviceStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    WORKING = "working"
    ERROR = "error"
    AUTHORIZING = "authorizing"


class DeviceAction(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

class UserStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    BANNED = "banned"

class SocialAccountStatus(str, Enum):
    LIVE = "live"
    CHECKPOINT = "checkpoint"


class ProxyStatus(str, Enum):
    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"
    WORKING = "working"


class ProxyType(str, Enum):
    STATIC = "static"
    API = "api"