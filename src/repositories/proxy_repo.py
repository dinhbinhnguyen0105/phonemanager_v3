# src/repositories/proxy_repo.py
from typing import List
from src.repositories.base_repo import BaseRepository
from src.entities import Proxy
from src.constants import ProxyStatus, ProxyType

class ProxyRepository(BaseRepository[Proxy]):
    """Repository for managing proxy data."""
    
    def __init__(self, db_manager):
        super().__init__(
            db_manager=db_manager, 
            table_name="proxies", 
            entity_class=Proxy, 
            pk_name="proxy_id", # Proxy uses proxy_id instead of uuid
            soft_delete=False
        )
        
    def get_by_status(self, status: ProxyStatus) -> List[Proxy]:
        """Retrieves a list of proxies filtered by status."""
        return self.get_many_by_fields({"proxy_status": status.value})

    def get_by_type(self, proxy_type: ProxyType) -> List[Proxy]:
        """Retrieves a list of proxies filtered by type (STATIC, API, etc.)."""
        return self.get_many_by_fields({"proxy_type": proxy_type.value})