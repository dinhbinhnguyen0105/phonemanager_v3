# core\constants.py
from enum import Enum

class RedisQueue(str, Enum):
    DEVICE_EVENTS = "farm:device_events:queue"

    JOB_PENDING = "farm:job_pending:queue"
    JOB_RESULTS = "farm:job_results:queue"
    PROXY_EVENTS = "farm:proxy_events:queue"

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
    LOCAL = "local"

class SettingType(str, Enum):
    PROXY = "proxy"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Platform(str, Enum):
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tikok"

class JobAction(str, Enum):
    LAUNCH = "launch"                              

    FB__LAUNCH_APP = "fb_launch_app"               # Chạy app"
    FB__SCROLL_FEED = "fb_scroll_feed"             # Chỉ lướt new feed
    FB__INTERACT_FEED = "fb_interact_feed"         # Lướt và tự động like/comment ngẫu nhiên
    FB__POST_GROUP = "fb_post_group"               # Đăng bài vào nhóm
    FB__INTERACT_TARGET = "fb_interact_target"     # Vào thẳng 1 bài viết/page chỉ định để tương tác
    FB__LIST_MARKETPLACE_AND_SHARE = "fb_list_marketplace_and_share"
    
    TT__LAUNCH_APP = "tt_launch_app"               # Chạy app"
    TT__WATCH_FEED = "tt_watch_feed"               # Lướt For You page
    TT__INTERACT_TARGET = "tt_interact_target"     # Mở video chỉ định (qua link/ID) để like, share


class FacebookReaction(str, Enum):
    LIKE = "like"
    LOVE = "love"
    CARE = "care"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"