# src/drivers/redis/base_state.py
import json
from enum import Enum
from redis import Redis
from typing import Any, Dict, List, Optional, Set

class BaseState:
    """
    Base class for managing state within Redis using a specific namespace.
    Provides utility methods for Hash, Set, and general Key operations.
    """
    def __init__(self, redis_client: Redis, namespace: str):
        """
        Initializes the BaseState with a Redis client and a prefix namespace.

        Args:
            redis_client (Redis): An active Redis connection instance.
            namespace (str): The prefix used for all keys (e.g., 'farm:device').
        """
        self.redis = redis_client
        self.namespace = namespace # 'farm:device'
    
    def _key(self, suffix: str) -> str:
        """
        Generates a full Redis key by joining the namespace and the suffix.
        """
        return f"{self.namespace}:{suffix}"
    
    # --- Hash Operations (Used for storing Object/Dict information) ---
    def hset_dict(self, key_suffix: str, data: Dict[str, Any]) -> None:
        """
        Stores a dictionary into a Redis hash, automatically serializing complex types to JSON.

        Args:
            key_suffix (str): The suffix for the Redis key.
            data (Dict[str, Any]): The dictionary data to store.
        """
        key = self._key(key_suffix)
        parsed_data = {}
        for k, v in data.items():
            if isinstance(v, (list, dict)):
                parsed_data[k] = json.dumps(v)
            elif isinstance(v, Enum):
                parsed_data[k] = v.value
            else:
                parsed_data[k] = v
        self.redis.hset(key, mapping=parsed_data)
    
    def hget_all(self, key_suffix: str) -> Dict[str, Any]:
        """
        Retrieves all fields and values from a Redis hash.
        """
        return self.redis.hgetall(self._key(key_suffix))
    
    def hdel(self, key_suffix: str, *field) -> None:
        """
        Deletes one or more fields from a Redis hash.
        """
        self.redis.hdel(self._key(key_suffix), *field)
    
    # --- Set Operations (Used for unique lists, e.g., online status) ---
    def sadd(self, key_suffix: str, *members: Any) -> None:
        """
        Adds one or more members to a Redis set.
        """
        self.redis.sadd(self._key(key_suffix), *members)
    
    def srem(self, key_suffix: str, *members: Any) -> None:
        """
        Removes one or more members from a Redis set.
        """
        self.redis.srem(self._key(key_suffix), *members)
    
    def smembers(self, key_suffix: str) -> Set[str]:
        """
        Retrieves all members of a Redis set.
        """
        return self.redis.smembers(self._key(key_suffix))
    
    # --- General Key Operations ---
    def delete(self, key_suffix: str) -> None:
        """
        Deletes a key from Redis regardless of its type.
        """
        self.redis.delete(self._key(key_suffix))
    
    def exists(self, key_suffix: str) -> bool:
        """
        Checks if a key exists in Redis.
        """
        return self.redis.exists(self._key(key_suffix))