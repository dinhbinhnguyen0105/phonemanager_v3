# src/services/social_service.py
from typing import List,TYPE_CHECKING, Optional
from src.services.base_service import BaseService
from src.entities import Social
from src.repositories.social_repo import SocialRepository
if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade

class SocialService(BaseService[Social]):
    """Service layer for managing Social account business logic."""
    
    def __init__(self, repository: SocialRepository, redis_facade: "RedisStateFacade"):
        super().__init__(repository, redis_facade)
        self.repo = repository
        self.redis_facade = redis_facade
    def validate_create(self, entity: Social) -> None:
        """Hook for validating social account data before creation."""
        pass
        
    def get_accounts_by_group(self, group_id: int) -> List[Social]:
        """Retrieves a list of accounts belonging to a specific group."""
        return self.repo.get_by_group(group_id)
    
    def get_accounts_by_profile(self, user_uuid: str) -> List[Social]:
        return self.repo.get_accounts_by_profile(user_uuid)