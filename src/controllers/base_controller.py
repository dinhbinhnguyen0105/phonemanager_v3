# src/controllers/base_controller.py
from PySide6.QtCore import QObject, Signal
from typing import TypeVar, Generic, List, Optional, Any, Union

from src.services.base_service import BaseService
from src.entities import BaseEntity
from src.utils.logger import logger

T = TypeVar("T", bound=BaseEntity)


class BaseController(QObject, Generic[T]):
    data_changed = Signal()
    error_occurred = Signal(str)
    msg_signal = Signal(str)

    def __init__(self, service: BaseService[T]):
        super().__init__()
        self.service = service

    def get_all(self) -> List[T]:
        return self.service.get_all()

    def get_by_id(self, pk: Any) -> Optional[T]:
        return self.service.get_by_id(pk)

    def create(self, entity: T) -> Optional[T]:
        try:
            return self.service.create(entity)
        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            self.error_occurred.emit(str(e))
            return None

    def update(self, entity: T) -> bool:
        try:
            success = self.service.update(entity)
            if success:
                self.data_changed.emit()
            return success
        except Exception as e:
            self.error_occurred.emit(str(e))
            logger.error(f"Error updating entity: {e}")
            return False

    def delete(self, pk: Any) -> bool:
        try:
            success = self.service.delete(pk)
            if success:
                self.data_changed.emit()
            return success
        except Exception as e:
            self.error_occurred.emit(str(e))
            logger.error(f"Error deleting entity: {e}")
            return False
