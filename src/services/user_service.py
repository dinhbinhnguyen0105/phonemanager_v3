# src/services/user_service.py
from typing import List, Dict, Any, TYPE_CHECKING
from src.services.base_service import BaseService
from src.entities import User, Device
from src.repositories.user_repo import UserRepository
from src.drivers.adb.controller import ADBController
if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade

class UserService(BaseService[User]):
    """Service layer for managing User profile business logic."""
    
    def __init__(self, repository: "UserRepository", redis_facade: "RedisStateFacade"):
        super().__init__(repository, redis_facade)
        self.repo: UserRepository

    def validate_create(self, entity: User) -> None:
        """
        Validates user data before creation.
        
        :raises ValueError: If the user name is empty.
        """
        if not entity.user_name or entity.user_name.strip() == "":
            raise ValueError("User name cannot be empty.")

    def get_profiles_by_device(self, device_uuid: str) -> List[User]:
        """Retrieves all user profiles assigned to a specific device."""
        return self.repo.get_by_device(device_uuid)

    def assign_to_device(self, user_uuid: str, device_uuid: str) -> bool:
        """Assigns a profile to a device for task execution."""
        user = self.get_by_id(user_uuid)
        if not user:
            raise ValueError("User profile not found.")
            
        user.device_uuid = device_uuid
        return self.update(user)

    def unassign_device(self, user_uuid: str) -> bool:
        """Removes the profile from its current device."""
        user = self.get_by_id(user_uuid)
        if not user:
            return False
            
        user.device_uuid = None
        return self.update(user)
    
    def sync_users_from_adb_data(self, device: Device, adb_users_data: List[Dict[str, Any]]):
        users = self.repo.get_by_device(device_uuid=device.uuid)
        print(users)
        print(adb_users_data) #[{'user_id': 0, 'user_name': 'root', 'user_status': 'active'}]
        pass