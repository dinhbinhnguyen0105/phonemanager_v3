# src/services/proxy_service.py
from typing import Optional, TYPE_CHECKING
from src.entities import Proxy
from src.constants import ProxyStatus, ProxyType
from src.services.base_service import BaseService
from src.repositories.proxy_repo import ProxyRepository
if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade

class ProxyService(BaseService[Proxy]):
    """Service layer for managing Proxy business logic."""
    
    def __init__(self, repository: ProxyRepository, redis_facade: "RedisStateFacade"):
        super().__init__(repository, redis_facade=redis_facade)

    def validate_create(self, entity: Proxy) -> None:
        """
        Validates proxy data before creation.
        
        :raises ValueError: If the proxy value is empty or already exists.
        """
        if not entity.value:
            raise ValueError("Proxy value cannot be empty.")
        
        # Check if proxy (ip:port string) already exists
        existing = self.repo.get_one_by_fields({"value": entity.value})
        if existing:
            raise ValueError(f"Proxy '{entity.value}' already exists.")

    def get_available_proxy(self, p_type: ProxyType = ProxyType.STATIC) -> Optional[Proxy]:
        """Retrieves an available proxy by type."""
        proxies = self.repo.get_many_by_fields({
            "proxy_status": ProxyStatus.AVAILABLE.value,
            "proxy_type": p_type.value
        })
        return proxies[0] if proxies else None

    def mark_proxy_working(self, proxy_id: int) -> bool:
        """Sets the proxy status to WORKING."""
        proxy = self.get_by_id(proxy_id)
        if proxy:
            proxy.proxy_status = ProxyStatus.WORKING
            return self.update(proxy)
        return False
        
    def release_proxy(self, proxy_id: int) -> bool:
        """Sets the proxy status back to AVAILABLE."""
        proxy = self.get_by_id(proxy_id)
        if proxy:
            proxy.proxy_status = ProxyStatus.AVAILABLE
            return self.update(proxy)
        return False