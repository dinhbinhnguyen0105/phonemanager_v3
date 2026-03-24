# src\controllers\social_controller.py
from typing import Any, Optional, List

from src.controllers.base_controller import BaseController
from src.services.social_service import SocialService
from src.entities import Social

class SocialController(BaseController[Social]):
    def __init__(self, service: SocialService):
        super().__init__(service)
        self.service = service

    def get_accounts_by_profile(self, user_uuid: str) -> List[Social]:
        return self.service.get_accounts_by_profile(user_uuid)

    def create(self, entity: Social) -> Optional[Social]:
        return self.service.create(entity)