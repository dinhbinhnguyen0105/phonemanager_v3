# src/views/pages/home/user_table.py
from typing import List
from PySide6.QtWidgets import QTableView, QAbstractItemView
from PySide6.QtCore import Signal
from src.entities import User, UserStatus
from src.models.table_model import UserTableModel
from src.database.connection import DatabaseManager


class UserTable(QTableView):
    users_selected = Signal(list) 
    row_double_clicked = Signal(User)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = UserTableModel(DatabaseManager())
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.hide_columns_by_name(["uuid", "created_at", "updated_at"])
        self.doubleClicked.connect(self._on_row_double_clicked)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def hide_columns_by_name(self, column_names: list[str]):
        record = self._model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setColumnHidden(i, field_name in column_names)

    def _parse_user_from_record(self, record) -> User:
        status_str = record.value("user_status")
        try:
            status_enum = UserStatus(status_str)
        except ValueError:
            status_enum = UserStatus.INACTIVE 
            
        return User(
            uuid=record.value("uuid"),
            user_id=record.value("user_id"),
            user_name=record.value("user_name"),
            user_status=status_enum,
            device_uuid=record.value("device_uuid"),
            social_uuid=record.value("social_uuid"),
            created_at=record.value("created_at"),
            updated_at=record.value("updated_at")
        )

    def _on_selection_changed(self, selected, deselected):
        selected_users = []
        for index in self.selectionModel().selectedRows():
            if index.isValid():
                record = self._model.record(index.row())
                user = self._parse_user_from_record(record)
                selected_users.append(user)
        self.users_selected.emit(selected_users)

    def _on_row_double_clicked(self, index):
        if not index.isValid():
            return
            
        record = self._model.record(index.row())
        selected_user = self._parse_user_from_record(record)
        self.row_double_clicked.emit(selected_user)
        
    def refresh_data(self):
        self._model.select()