# src/services/user_service.py
from typing import List, Dict, Any, TYPE_CHECKING
from src.services.base_service import BaseService
from src.entities import User, Device
from src.repositories.user_repo import UserRepository
# from src.drivers.adb.controller import ADBController
from src.utils.logger import logger
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
            
        user.device_uuid = ""
        return self.update(user)
    
    def sync_users_from_adb_data(self, device: Device, users_data: List[User]):
        existing_users = self.repo.get_by_device(device_uuid=device.uuid)
        existing_user_dict = {str(u.user_id): u for u in existing_users}
        adb_user_ids = set()
                
        for adb_user in users_data:
            adb_user_ids.add(adb_user.user_id)
            if str(adb_user.user_id) in existing_user_dict:
                db_user = existing_user_dict[str(adb_user.user_id)]
                db_user.user_name = adb_user.user_name
                db_user.user_status = adb_user.user_status
                self.update(db_user)
            else:
                adb_user.device_uuid = device.uuid
                self.create(adb_user)
                self.assign_to_device(adb_user.uuid, device.uuid)