# src/drivers/redis/proxy_state.py

from typing import Optional, Dict, Any
from src.entities import ProxyStatus, ProxyType
from src.drivers.redis.base_state import BaseState


class ProxyState(BaseState):
    """
    Manages the real-time state of proxies in Redis.
    Handles proxy pooling, acquisition, and status tracking.
    """
    
    def __init__(self, redis_client):
        super().__init__(redis_client, namespace='farm:proxy')
    
    def init_proxy(self, proxy_uuid: str, p_type: ProxyType, value: str) -> None:
        """
        Initializes the metadata for a new proxy.
        
        :param proxy_uuid: Unique identifier for the proxy.
        :param p_type: Type of the proxy (e.g., STATIC, API).
        :param value: The actual proxy connection string (ip:port).
        """
        self.hset_dict(f"info:{proxy_uuid}", {
            "type": p_type.value,
            "value": value,
            "status": ProxyStatus.AVAILABLE.value,
            "current_ip": "",
        })
    
    def add_to_pool(self, proxy_uuid: str) -> None:
        """
        Adds a proxy to the available pool for devices to acquire.
        
        :param proxy_uuid: Unique identifier for the proxy.
        """
        self.redis.lpush(self._key("pool:available"), proxy_uuid)
        self.hset_dict(f"info:{proxy_uuid}", {
            "status": ProxyStatus.AVAILABLE.value,
        })
    
    def acquire_proxy(self, serial: str) -> Optional[str]:
        """
        Blocks and waits to acquire an available proxy from the pool.
        
        :param serial: The device serial number acquiring the proxy.
        :return: The proxy UUID if acquired, or None if the request timed out.
        """
        # Block until a proxy is available in the list
        result = self.redis.brpop(self._key("pool:available"), timeout=2)
        if result:
            _, proxy_uuid = result
            # Register the proxy as currently working with this device
            self.hset_dict(self._key("working"), {proxy_uuid: serial}) 
            self.hset_dict(f"info:{proxy_uuid}", {
                "status": ProxyStatus.WORKING.value,
            })
            return proxy_uuid.decode('utf-8') if isinstance(proxy_uuid, bytes) else proxy_uuid
        return None
    
    def release_proxy(self, proxy_uuid: str) -> None:
        """
        Releases a proxy back into the available pool for other devices.
        
        :param proxy_uuid: Unique identifier for the proxy.
        """
        self.hdel(self._key("working"), proxy_uuid)
        self.add_to_pool(proxy_uuid)
    
    def get_proxy_info(self, proxy_uuid: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific proxy.
        
        :param proxy_uuid: Unique identifier for the proxy.
        :return: A dictionary containing proxy metadata.
        """
        return self.hget_all(f"info:{proxy_uuid}")
    
    def update_current_ip(self, proxy_uuid: str, new_ip: str) -> None:
        """
        Updates the detected current IP address for a proxy.
        
        :param proxy_uuid: Unique identifier for the proxy.
        :param new_ip: The new IP address to set.
        """
        self.hset_dict(f"info:{proxy_uuid}", {
            "current_ip": new_ip,
        })