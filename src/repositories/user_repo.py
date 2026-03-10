# src/repositories/user_repo.py

from typing import List
from src.repositories.base_repo import BaseRepository
from src.entities import User
from src.constants import UserStatus

class UserRepository(BaseRepository[User]):
    """Repository for managing user profile data."""
    
    def __init__(self, db_manager):
        super().__init__(
            db_manager=db_manager, 
            table_name="users", 
            entity_class=User, 
            pk_name="uuid",
            soft_delete=False
        )
        
    def get_by_device(self, device_uuid: str) -> List[User]:
        """Retrieves a list of user profiles assigned to a specific device."""
        return self.get_many_by_fields({"device_uuid": device_uuid})
        
    def get_by_status(self, status: UserStatus) -> List[User]:
        """Retrieves a list of user profiles filtered by status (ACTIVE, INACTIVE, etc.)."""
        return self.get_many_by_fields({"user_status": status.value})
    