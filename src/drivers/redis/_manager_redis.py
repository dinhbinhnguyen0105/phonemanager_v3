# src/drivers/redis/_manager_redis.py
from typing import Awaitable
from src.drivers.redis.redis_manager import RedisStateManager
from src.drivers.redis.device_state import DeviceState
from src.drivers.redis.proxy_state import ProxyState
from src.drivers.redis.job_state import JobState

class RedisStateFacade:
    """
    A centralized access point (Facade) for all Redis-based state management.
    This class orchestrates the initialization of specific state modules
    such as devices, proxies, and jobs.
    """
    
    def __init__(self):
        # Retrieve the shared Redis client from the connection pool
        self.client = RedisStateManager.get_client()
        
        # Initialize specific state management modules
        self.devices = DeviceState(self.client)
        self.proxies = ProxyState(self.client)
        self.jobs = JobState(self.client)
        
    def ping(self) -> Awaitable[bool] | bool:
        """
        Verifies the connection to the Redis server.
        
        :return: True if the connection is active, False otherwise.
        """
        try:
            return self.client.ping()
        except Exception:
            return False