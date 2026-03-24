# src/services/base_service.py
from PySide6.QtCore import QObject
from typing import TypeVar, Generic, Union, List, Optional, Any, TYPE_CHECKING

from src.entities import BaseEntity
from src.repositories.base_repo import BaseRepository

if TYPE_CHECKING:
    from src.drivers.redis._manager_redis import RedisStateFacade


T = TypeVar("T", bound=BaseEntity)


class BaseService(Generic[T]):
    """
    Generic Service Layer

    - Wrap repository
    - Handle transaction
    - Handle validation hook
    """

    def __init__(self, repository: "BaseRepository[T]", redis_facade: "RedisStateFacade"):
        self.repo = repository
        self.redis_facade = redis_facade
        self.db = repository.db

    # =====================================================
    # Hooks (override nếu cần)
    # =====================================================

    def validate_create(self, entity: T):
        """Override để validate trước khi tạo"""
        pass

    def validate_update(self, entity: T):
        """Override để validate trước khi update"""
        pass

    def before_delete(self, entity: T):
        """Override nếu cần kiểm tra trước khi xóa"""
        pass

    # =====================================================
    # CRUD
    # =====================================================

    def get_all(self) -> List[T]:
        return self.repo.get_all()

    def get_by_id(self, pk: Any) -> Optional[T]:
        return self.repo.get_by_id(pk)

    def create(self, entity: T) -> Optional[T]:
        self.validate_create(entity)

        with self.db.atomic():
            if self.repo.insert(entity):
                return entity
            return None

    def update(self, entity: T) -> bool:
        self.validate_update(entity)

        with self.db.atomic():
            return self.repo.update(entity)

    def delete(self, pk: Any) -> bool:
        entity = self.repo.get_by_id(pk)
        if not entity:
            return False

        self.before_delete(entity)

        with self.db.atomic():
            return self.repo.delete(pk)

    def exists(self, pk: Any) -> bool:
        return self.repo.exists(pk)

    def bulk_create(self, entities: List[T]) -> bool:
        for entity in entities:
            self.validate_create(entity)

        with self.db.atomic():
            return self.repo.bulk_insert(entities)