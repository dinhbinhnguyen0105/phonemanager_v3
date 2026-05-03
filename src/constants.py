# core\constants.py
from enum import Enum

class Database__Table(str, Enum):
    """
    Mapping of database table names used within the application.
    """
    FACEBOOK_ACCOUNTS = "facebook_accounts"
    REAL_ESTATE_PRODUCTS = "real_estate_products"
    MISC_PRODUCTS = "misc_products"
    REAL_ESTATE_TEMPLATES = "real_estate_templates"
    SETTINGS = "settings"
    PROXY = "proxy"

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

class Product__Status(str, Enum):
    """
    Inventory and visibility status of listed products.
    """
    SELLING = "selling"
    SOLD = "sold"
    PAUSED = "paused"

class RealEstateProduct__TransactionType(str, Enum):
    """
    Types of real estate market transactions.
    """
    SALE = "sale"
    RENTAL = "rental"
    TRANSFER = "transfer"

class RealEstateProduct__Province(str, Enum):
    """
    Supported provinces for real estate listings.
    """
    LAM_DONG = "lam_dong"

class RealEstateProduct__District(str, Enum):
    """
    Supported districts for real estate listings.
    """
    DA_LAT = "da_lat"

class RealEstateProduct__Ward(str, Enum):
    """
    Specific wards and communes within the supported districts, primarily in Da Lat.
    """
    PHUONG_1 = "phuong_1_xuan_huong"
    PHUONG_2 = "phuong_2_xuan_huong"
    PHUONG_3 = "phuong_3_xuan_huong"
    PHUONG_4 = "phuong_4_xuan_huong"
    PHUONG_5 = "phuong_5_cam_ly"
    PHUONG_6 = "phuong_6_cam_ly"
    PHUONG_7 = "phuong_7_lang_biang"
    PHUONG_8 = "phuong_8_lam_vien"
    PHUONG_9 = "phuong_9_lam_vien"
    PHUONG_10 = "phuong_10_xuan_huong"
    PHUONG_11 = "phuong_11_xuan_truong"
    PHUONG_12 = "phuong_12_lam_vien"
    XUAN_TRUONG = "xa_xuan_truong"
    XUAN_THO = "xa_xuan_tho"
    TA_NUNG = "xa_ta_nung"
    TRAM_HANH = "xa_tram_hanh"
    LAC_DUONG = "thi_tran_lac_duong"

class RealEstateProduct__Category(str, Enum):
    """
    Classification of real estate property types.
    """
    TOWNHOUSE = "townhouse"
    STREET_FRONT_HOUSE = "street_front_house"
    APARTMENT_CONDO = "apartment_condo"
    VILLA = "villa"
    LAND_PLOT = "land_plot"
    WAREHOUSE_YARD = "warehouse_yard"
    BUSINESS_PREMISES = "business_premises"
    HOTEL = "hotel"
    HOMESTAY = "homestay"

class RealEstateProduct__Unit(str, Enum):
    """
    Pricing units for real estate listings.
    """
    BILLION = "billion"
    MILLION = "million"
    MILLION_PER_MONTH = "million_per_month"

class RealEstateProduct__Legal(str, Enum):
    """
    Legal documentation status and deed types for properties.
    """
    VI_BANG_PURCHASE = "vi_bang_purchase"
    SHARED_AGRICULTURAL_DEED = "shared_agriculture_deed"
    DECENTRALIZED_AGRICULTURAL_DEED = "decentralized_agriculture_deed"
    PRIVATE_AGRICULTURAL_DEED = "private_agriculture_deed"
    SHARED_CONSTRUCTION_DEED = "shared_construction_deed"
    DECENTRALIZED_CONSTRUCTION_DEED = "decentralized_construction_deed"
    PRIVATE_CONSTRUCTION_DEED = "private_construction_deed"

class RealEstateProduct__BuildingLine(str, Enum):
    """
    Accessibility and road access specifications for properties.
    """
    CAR_ACCESS_ROAD = "car_access_road"
    MOTORBIKE_ACCESS_ROAD = "motorbike_access_road"

class RealEstateProduct__Furniture(str, Enum):
    """
    Furniture status for residential property listings.
    """
    NO_FURNITURE = "no_furniture"
    BASIC_FURNITURE = "basic_furniture"
    FULL_FURNITURE = "full_furniture"

class RealEstateTemplate__Name(str, Enum):
    """
    Identifiable components for real estate content generation templates.
    """
    TITLE = "title"
    DESCRIPTION = "description"
