# src/views/pages/home/social_table.py
from typing import List
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QTableView, QAbstractItemView, QMenu

from src.entities import Social
from src.models.table_model import SocialTableModel
from src.database.connection import DatabaseManager

class SocialTable(QTableView):
    socials_selected = Signal(list) 
    row_double_clicked = Signal(Social)
    log_msg = Signal(str)

    def __init__(self, controllers, parent=None):
        super().__init__(parent)
        self.controllers = controllers
        self._model = SocialTableModel(DatabaseManager())
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self._hide_columns(["uuid", "created_at", "updated_at", "social_password"])
        self.doubleClicked.connect(self._on_row_double_clicked)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        selected_indexes = self.selectionModel().selectedRows()
        if not selected_indexes:
            return
        
        socials = []
        for idx in selected_indexes:
            if idx.isValid():
                record = self._model.record(idx.row())
                socials.append(self._parse_social_from_record(record))
        
        menu = QMenu(self)
        if len(socials) == 1:
            delete_action = menu.addAction("Delete social account")
            delete_action.triggered.connect(lambda: self._delete_social(socials[0]))

        menu.exec(self.viewport().mapToGlobal(pos))

    # ==========================================
    # ACTION SLOTS
    # ==========================================
    def _delete_social(self, social: Social):
        self.log_msg.emit(f"🗑 Đang xóa tài khoản {social.social_name} ({social.social_platform})...")
        success = self.controllers.social_controller.delete(social.uuid)
        
        if success:
            self.log_msg.emit("✔️ Đã xóa tài khoản Social thành công.")
            self.refresh_data()
        else:
            self.log_msg.emit("❌ Lỗi: Không thể xóa tài khoản Social.")

    # Các hàm parse và refresh giữ nguyên
    def _hide_columns(self, column_names: list[str]):
        record = self._model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setColumnHidden(i, field_name in column_names)

    def _parse_social_from_record(self, record) -> Social:
        return Social(
            uuid=record.value("uuid"),
            user_uuid=record.value("user_uuid"),
            social_id=record.value("social_id"),
            social_name=record.value("social_name"),
            social_password=record.value("social_password"),
            social_status=int(record.value("social_status") or 0),
            social_group=int(record.value("social_group") or 0),
            social_platform=record.value("social_platform"),
            created_at=record.value("created_at"),
            updated_at=record.value("updated_at")
        )

    def _on_selection_changed(self, selected, deselected):
        selected_socials = []
        for index in self.selectionModel().selectedRows():
            if index.isValid():
                record = self._model.record(index.row())
                social = self._parse_social_from_record(record)
                selected_socials.append(social)
        self.socials_selected.emit(selected_socials)

    def _on_row_double_clicked(self, index):
        if not index.isValid():
            return
        record = self._model.record(index.row())
        selected_social = self._parse_social_from_record(record)
        self.row_double_clicked.emit(selected_social)
        
    def refresh_data(self):
        self._model.select()