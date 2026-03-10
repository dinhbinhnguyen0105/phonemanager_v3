# src/repositories/_manager_repositories.py
from typing import Optional
from src.database.connection import DatabaseManager
from src.repositories.device_repo import DeviceRepository
from src.repositories.user_repo import UserRepository
from src.repositories.social_repo import SocialRepository
from src.repositories.proxy_repo import ProxyRepository

class RepositoryManager:
    """
    Centralized access point (Facade/Unit of Work) for all repositories.
    """
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        
        # Initialize repositories sharing the same DatabaseManager
        self.devices = DeviceRepository(self.db)
        self.users = UserRepository(self.db)
        self.socials = SocialRepository(self.db)
        self.proxies = ProxyRepository(self.db)

    def init_database(self) -> bool:
        """Runs the schema initialization to create tables if they do not exist."""
        return self.db.init_tables()

    def close(self):
        """Closes the database connection for the current thread."""
        self.db.close()
        