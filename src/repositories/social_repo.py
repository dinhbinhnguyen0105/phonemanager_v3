# src/repositories/social_repo.py
from typing import List
from src.repositories.base_repo import BaseRepository
from src.entities import Social

class SocialRepository(BaseRepository[Social]):
    """Repository for managing social account data."""
    
    def __init__(self, db_manager):
        super().__init__(
            db_manager=db_manager, 
            table_name="socials", 
            entity_class=Social, 
            pk_name="uuid",
            soft_delete=False
        )
        
    def get_by_group(self, group_id: int) -> List[Social]:
        """Retrieves a list of social accounts belonging to a specific group."""
        return self.get_many_by_fields({"social_group": group_id})