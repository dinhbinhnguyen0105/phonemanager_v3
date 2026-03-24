# src/repositories/proxy_repo.py
from typing import List, Optional
from src.repositories.base_repo import BaseRepository
from src.entities import Proxy
from src.constants import ProxyStatus, ProxyType

class ProxyRepository(BaseRepository[Proxy]):
    """Repository for managing proxy data using UUID as primary key."""
    
    def __init__(self, db_manager):
        super().__init__(
            db_manager=db_manager, 
            table_name="proxies", 
            entity_class=Proxy, 
            pk_name="uuid", # Updated from proxy_id to uuid based on schema.py
            soft_delete=False
        )
        
    def get_by_status(self, status: ProxyStatus) -> List[Proxy]:
        """Retrieves a list of proxies filtered by status enum."""
        return self.get_many_by_fields({"proxy_status": status.value})

    def get_by_type(self, proxy_type: ProxyType) -> List[Proxy]:
        """Retrieves a list of proxies filtered by type (STATIC, API, LOCAL)."""
        return self.get_many_by_fields({"proxy_type": proxy_type.value})

    def get_by_address(self, host: str, port: int) -> Optional[Proxy]:
        """Finds a proxy by its host and port combination."""
        return self.get_one_by_fields({"host": host, "port": port})