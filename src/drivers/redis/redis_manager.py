# src/drivers/redis/redis_manager.py
import redis
from src.utils.yaml_handler import settings

class RedisStateManager:
    _pool = None

    @staticmethod
    def get_client() -> redis.Redis:
        if RedisStateManager._pool is None:
            RedisStateManager._pool = redis.ConnectionPool(
                host=settings.redis.host or 'localhost', # type: ignore
                port=settings.redis.port or 6379, # type: ignore
                db=settings.redis.db or 1, # type: ignore
                # password=settings.redis.password or None,
                decode_responses=True
            )
        return redis.Redis(connection_pool=RedisStateManager._pool)