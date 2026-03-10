# src/repositories/base_repo.py

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from dataclasses import is_dataclass

from src.database.connection import DatabaseManager
from src.entities import BaseEntity


T = TypeVar("T", bound=BaseEntity)


class BaseRepository(Generic[T]):
    """
    Generic Repository – Compatible with new BaseEntity
    - Uses from_dict()
    - Auto handle timestamps
    - Optional soft delete
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        table_name: str,
        entity_class: Type[T],
        pk_name: str = "uuid",
        soft_delete: bool = False,
    ):
        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")

        if not is_dataclass(entity_class):
            raise TypeError("Entity must be a dataclass")

        if not issubclass(entity_class, BaseEntity):
            raise TypeError("Entity must inherit from BaseEntity")

        self.db = db_manager
        self.table_name = table_name
        self.entity_class = entity_class
        self.pk_name = pk_name
        self.soft_delete = soft_delete

    # =====================================================
    # Internal Helpers
    # =====================================================

    def _row_to_entity(self, row: Optional[Dict[str, Any]]) -> Optional[T]:
        if not row:
            return None
        return self.entity_class.from_dict(row)

    def _soft_delete_condition(self) -> str:
        return "AND is_deleted = 0" if self.soft_delete else ""

    # =====================================================
    # READ
    # =====================================================

    def get_all(self) -> List[T]:
        query = f"SELECT * FROM {self.table_name}"
        if self.soft_delete:
            query += " WHERE is_deleted = 0"

        rows = self.db.fetch_all(query)
        return [self._row_to_entity(r) for r in rows]

    def get_all_paginated(self, limit: int, offset: int = 0) -> List[T]:
        query = f"SELECT * FROM {self.table_name}"
        if self.soft_delete:
            query += " WHERE is_deleted = 0"

        query += " LIMIT ? OFFSET ?"

        rows = self.db.fetch_all(query, (limit, offset))
        return [self._row_to_entity(r) for r in rows]

    def get_by_id(self, pk_value: Any) -> Optional[T]:
        if pk_value is None:
            return None

        query = f"SELECT * FROM {self.table_name} WHERE {self.pk_name} = ?"
        if self.soft_delete:
            query += " AND is_deleted = 0"

        row = self.db.fetch_one(query, (pk_value,))
        return self._row_to_entity(row)

    def get_many_by_fields(self, filters: Dict[str, Any]) -> List[T]:
        """
        Retrieves a list of records matching multiple conditions (AND).
        Example: repo.get_many_by_fields({"device_status": "offline", "device_root": 1})
        """
        if not filters:
            return self.get_all()

        conditions = []
        values = []

        for field, value in filters.items():
            if not str(field).isidentifier():
                raise ValueError(f"Invalid field name: {field}")
            
            conditions.append(f"{field} = ?")
            values.append(value)

        if self.soft_delete:
            conditions.append("is_deleted = 0")

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"

        rows = self.db.fetch_all(query, tuple(values))
        return [self._row_to_entity(r) for r in rows]
        
    def get_one_by_fields(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        Retrieves the first record matching multiple conditions (AND).
        Example: repo.get_one_by_fields({"user_name": "profile_1", "user_status": "active"})
        """
        if not filters:
            return None

        conditions = []
        values = []

        for field, value in filters.items():
            if not str(field).isidentifier():
                raise ValueError(f"Invalid field name: {field}")
            
            conditions.append(f"{field} = ?")
            values.append(value)

        if self.soft_delete:
            conditions.append("is_deleted = 0")
            
        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause} LIMIT 1"

        row = self.db.fetch_one(query, tuple(values))
        
        if not row:
            return None
            
        return self._row_to_entity(row)

    def exists(self, pk_value: Any) -> bool:
        if pk_value is None:
            return False

        query = f"SELECT 1 FROM {self.table_name} WHERE {self.pk_name} = ? LIMIT 1"
        row = self.db.fetch_one(query, (pk_value,))
        return row is not None

    # =====================================================
    # WRITE
    # =====================================================

    def insert(self, entity: T) -> bool:
        if not isinstance(entity, BaseEntity):
            raise TypeError("Invalid entity type")

        entity.mark_created()

        data = entity.to_dict()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        success, _ = self.db.execute(query, values)
        return success

    def bulk_insert(self, entities: List[T]) -> bool:
        if not entities:
            return True

        try:
            with self.db.atomic():
                for entity in entities:
                    entity.mark_created()
                    data = entity.to_dict()

                    columns = ", ".join(data.keys())
                    placeholders = ", ".join(["?"] * len(data))
                    values = tuple(data.values())

                    query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                    success, error = self.db.execute(query, values)
                    if not success:
                        raise Exception(error)

            return True

        except Exception:
            return False

    def update(self, entity: T) -> bool:
        if not isinstance(entity, BaseEntity):
            raise TypeError("Invalid entity type")

        data = entity.to_dict()
        pk_value = data.pop(self.pk_name, None)

        if pk_value is None:
            return False

        entity.touch()
        data = entity.to_dict()
        data.pop(self.pk_name, None)

        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + (pk_value,)

        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_name} = ?"
        success, _ = self.db.execute(query, values)
        return success

    def delete(self, pk_value: Any) -> bool:
        if pk_value is None:
            return False

        if self.soft_delete:
            query = f"UPDATE {self.table_name} SET is_deleted = 1 WHERE {self.pk_name} = ?"
        else:
            query = f"DELETE FROM {self.table_name} WHERE {self.pk_name} = ?"

        success, _ = self.db.execute(query, (pk_value,))
        return success