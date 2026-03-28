# src/drivers/redis/proxy_state.py
from typing import Optional, Dict, Any, List

from src.utils.logger import logger
from src.constants import ProxyStatus
from src.entities import Proxy, ProxyType
from src.drivers.redis.base_state import BaseState

class ProxyState(BaseState):
    """
    Manages the real-time state of proxies in Redis.
    Handles proxy pooling, acquisition, and status tracking.
    """
    
    def __init__(self, redis_client):
        super().__init__(redis_client, namespace='farm:proxy')
    
    def get_all_available(self) -> List[Proxy]:
        """
        Retrieves all available proxies from all proxy type pools 
        and reconstructs them into Proxy objects.
        """
        available_proxies = []
    
        for p_type in ProxyType:
            list_key = self._key(f"pool:available:{p_type.value}")
            
            items: list = self.redis.lrange(list_key, 0, -1) # type: ignore
            if items:
                for item in items:
                    proxy_uuid = item.decode('utf-8') if isinstance(item, bytes) else item
                    
                    info = self.get_proxy_info(proxy_uuid)
                    
                    if info:
                        proxy = Proxy(
                            uuid=proxy_uuid,
                            host=info.get("host", ""),
                            port=int(info.get("port", 0)),
                            rotate_url=info.get("rotate_url", ""),
                            proxy_type=info.get("type", ProxyType.STATIC.value),
                            proxy_status=info.get("status", ProxyStatus.AVAILABLE.value)
                        )
                        available_proxies.append(proxy)
                    
        return available_proxies
    
    def init_proxy(self, proxy: Proxy) -> None:
        """
        Initializes metadata for a new proxy on Redis.
        
        :param proxy: The Proxy entity containing configuration details.
        """
        self.hset_dict(f"info:{proxy.uuid}", {
            "host": proxy.host,
            "port": proxy.port,
            "rotate_url": proxy.rotate_url,
            "type": proxy.proxy_type.value,
            "status": proxy.proxy_status.value,
            "current_ip": "",
        })
    
    def add_to_pool(self, proxy_uuid: str, p_type: str = ProxyType.STATIC.value) -> None:
        """
        Adds a proxy to the available resource pool based on its classification.

        This method ensures the proxy is unique within the Redis list by performing 
        an 'LREM' (remove all existing occurrences) before pushing it to the 
        head of the queue. It also synchronizes the proxy's metadata status 
        to 'AVAILABLE'.

        Args:
            proxy_uuid (str): The unique identifier of the proxy.
            p_type (str): The type of proxy (e.g., STATIC, API, LOCAL). 
                          Defaults to ProxyType.STATIC.
        """
        queue_key = self._key(f"pool:available:{p_type}")
        
        self.redis.lrem(queue_key, 0, proxy_uuid) 
        
        self.redis.lpush(queue_key, proxy_uuid)
        
        self.hset_dict(f"info:{proxy_uuid}", {
            "status": ProxyStatus.AVAILABLE.value,
        })
    
    def acquire_proxy(self, serial: str, p_type: Optional[ProxyType] = None) -> Optional[str]:
        """
        Acquires an available proxy. If p_type is None, it takes from ANY available pool.
        """
        # Determine the queues to scan
        if p_type:
            keys = [self._key(f"pool:available:{p_type.value}")]
        else:
            # If no specific type is requested, scan through all available pools
            keys = [self._key(f"pool:available:{pt.value}") for pt in ProxyType]
            
        # BRPOP supports passing a list of keys. It pops the first element found in any of them.
        result = self.redis.brpop(keys, timeout=2) # type: ignore
        if result:
            queue_name, proxy_uuid = result # type: ignore
            proxy_uuid_str = proxy_uuid.decode('utf-8') if isinstance(proxy_uuid, bytes) else proxy_uuid
            
            # Associate the proxy with the device serial and mark it as working
            self.hset_dict(self._key("working"), {proxy_uuid_str: serial}) 
            self.hset_dict(f"info:{proxy_uuid_str}", {
                "status": ProxyStatus.WORKING.value,
            })
            return proxy_uuid_str
        return None

    def release_proxy(self, proxy_uuid: str) -> None:
        """
        Releases the proxy and returns it to its original pool.
        
        :param proxy_uuid: Unique identifier for the proxy to be released.
        """
        self.hdel(self._key("working"), proxy_uuid)
        
        info = self.get_proxy_info(proxy_uuid)
        p_type = info.get("type", ProxyType.STATIC.value)
        if isinstance(p_type, bytes):
            p_type = p_type.decode('utf-8')
            
        self.add_to_pool(proxy_uuid, p_type)
    
    def get_proxy_info(self, proxy_uuid: str) -> Dict[str, Any]:
        """Retrieves metadata for a specific proxy."""
        return self.hget_all(f"info:{proxy_uuid}")
    
    def update_current_ip(self, proxy_uuid: str, new_ip: str) -> None:
        """Updates the detected public IP for a proxy."""
        self.hset_dict(f"info:{proxy_uuid}", {
            "current_ip": new_ip,
        })
    
    def remove_from_pool(self, proxy_uuid: str, p_type: str) -> None:
        """
        Removes a proxy from the idle pool (available queue).
        Uses the lrem command to remove the specific UUID from the List.
        
        :param proxy_uuid: The unique identifier of the proxy to remove.
        :param p_type: The proxy classification (e.g., STATIC, API, LOCAL).
        """
        self.redis.lrem(self._key(f"pool:available:{p_type}"), 0, proxy_uuid)