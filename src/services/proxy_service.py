# src/services/proxy_service.py
from typing import Optional, TYPE_CHECKING, List

from src.entities import Proxy
from src.constants import ProxyType, ProxyStatus
from src.services.base_service import BaseService
from src.repositories.proxy_repo import ProxyRepository
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade

class ProxyService(BaseService[Proxy]):
    """
    Service layer for managing Proxy business logic and Redis synchronization.
    """
    def __init__(self, repository: ProxyRepository, redis_facade: "RedisStateFacade"):
        super().__init__(repository, redis_facade=redis_facade)
        self.repo = repository
        self.sync_db_to_redis()

    def sync_db_to_redis(self):
        """Synchronizes all proxies from the SQLite database to the Redis pool on startup."""
        logger.info("🔄 Starting proxy synchronization from Database to Redis...")
        for p_type in ProxyType:
            self.redis_facade.proxies.redis.delete(f"farm:proxy:pool:available:{p_type.value}")
        proxies = self.repo.get_many_by_fields({"proxy_status": ProxyStatus.AVAILABLE.value})
        for proxy in proxies:
            self.redis_facade.proxies.init_proxy(proxy)
            if proxy.proxy_status == ProxyStatus.AVAILABLE:
                self.redis_facade.proxies.add_to_pool(proxy.uuid, proxy.proxy_type.value)
        logger.success(f"✔️ Synchronized {len(proxies)} proxies. Ready for service.")

    def validate_create(self, entity: Proxy) -> None:
        """
        Validates proxy data before creation.
        
        :raises ValueError: If required fields are missing or if the address already exists.
        """
        if entity.proxy_type in (ProxyType.API, ProxyType.LOCAL):
            if not entity.rotate_url:
                raise ValueError("Rotate URL is required for API proxies.")
            return
        if not entity.host or type(entity.port) is not int or entity.port is None or entity.port < 0 or entity.port > 65535:
            raise ValueError("Proxy host and port are required for STATIC proxies.")
        
        existing = self.repo.get_by_address(entity.host, entity.port)
        if existing:
            raise ValueError(f"Proxy {entity.host}:{entity.port} already exists.")

    def create(self, entity: Proxy) -> Optional[Proxy]:
        """Persists a new proxy to DB and initializes it in Redis pools."""
        success = super().create(entity)
        if success:
            self.redis_facade.proxies.init_proxy(entity)
            if entity.proxy_status == ProxyStatus.AVAILABLE:
                self.redis_facade.proxies.add_to_pool(entity.uuid, entity.proxy_type.value)
        return success

    def update(self, entity: Proxy) -> bool:
        """Updates proxy data in DB and refreshes metadata/pools in Redis."""
        success = super().update(entity)
        if success:
            self.redis_facade.proxies.init_proxy(entity)
            if entity.proxy_status == ProxyStatus.UNAVAILABLE:
                self.redis_facade.proxies.remove_from_pool(entity.uuid, entity.proxy_type.value)
                logger.info(f"Removed Proxy {entity.uuid[:8]} from the idle pool.")
            elif entity.proxy_status == ProxyStatus.AVAILABLE:
                self.redis_facade.proxies.remove_from_pool(entity.uuid, entity.proxy_type.value)
                self.redis_facade.proxies.add_to_pool(entity.uuid, entity.proxy_type.value)
                
        return success

    def delete(self, pk: str) -> bool:
        """Deletes a proxy from DB and cleans up its real-time data in Redis."""
        success = super().delete(pk)
        if success:
            try:
                # Direct Redis deletion for cleanup
                self.redis_facade.proxies.redis.delete(f"farm:proxy:info:{pk}")
            except Exception as e:
                logger.warning(f"Minor error cleaning up Redis for proxy {pk}: {e}")
        return success

    def acquire_proxy(self, device_id: str, p_type: Optional[ProxyType] = None) -> Optional[Proxy]:
        """
        Retrieves an available proxy from the Redis Pool.
        """
        proxy_uuid = self.redis_facade.proxies.acquire_proxy(device_id, p_type)
        if not proxy_uuid:
            p_type_name = p_type.value if p_type else "ANY"
            logger.warning(f"[{device_id}] No '{p_type_name}' proxies available in the Redis Pool.")
            return None

        proxy = self.get_by_id(proxy_uuid)
        if not proxy:
            logger.error(f"[{device_id}] Proxy {proxy_uuid} exists in Redis but is missing from the Database!")
            self.redis_facade.proxies.release_proxy(proxy_uuid)
            return None

        logger.info(f"[{device_id}] Acquired Proxy: {proxy.host}:{proxy.port}")
        return proxy

    def release_proxy(self, uuid: str) -> None:
        """Returns the proxy to the Redis Pool so other devices can utilize it."""
        proxy = self.get_by_id(uuid)
        if not proxy:
            return
        if proxy.proxy_status == ProxyStatus.WORKING:
            proxy.proxy_status = ProxyStatus.AVAILABLE
            self.update(proxy)
            
        self.redis_facade.proxies.release_proxy(uuid)
        logger.info(f"Proxy '{uuid[:8]}...' has been returned to the Pool.")