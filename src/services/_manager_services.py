# src/services/_manager_services.py
from src.services.device_service import DeviceService
from src.services.user_service import UserService
from src.services.social_service import SocialService
from src.services.proxy_service import ProxyService
from src.services.job_service import JobService

from src.utils.logger import logger
from src.repositories._manager_repositories import RepositoryManager
from src.drivers.redis._manager_redis import RedisStateFacade


class ServiceManager:
    """
    Centralized hub for the entire Service Layer.
    Manages repository initialization and dependency injection for services.
    """
    def __init__(self, repo_manager: "RepositoryManager", redis_facade: "RedisStateFacade"):
        self.repos = repo_manager
        self.redis = redis_facade
        self.devices = DeviceService(self.repos.devices, self.redis)
        self.users = UserService(self.repos.users, self.redis)
        self.socials = SocialService(self.repos.socials, self.redis)
        self.proxies = ProxyService(self.repos.proxies, self.redis)
        self.jobs = JobService(self.redis)

    def init_system(self):
        """Initializes the database and creates tables if they do not exist."""
        self.repos.init_database()
        if self.redis.ping():
            logger.success("Connected to Redis successfully.")
        else:
            logger.error("Failed to connect to Redis.")

    def shutdown(self):
        """Safely closes all database connections."""
        self.repos.close()