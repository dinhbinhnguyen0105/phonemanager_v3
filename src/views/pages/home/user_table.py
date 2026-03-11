# src/views/pages/home/user_table.py
from typing import List
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import Signal

# Giả định import các class thực thể. Hãy điều chỉnh đường dẫn nếu cần thiết.
from src.entities import User, UserStatus
from src.models.table_model import UserTableModel
from src.database.connection import DatabaseManager


class UserTable(QTableView):
    # Phát ra danh sách User khi người dùng chọn nhiều dòng
    users_selected = Signal(list) 
    
    # Phát ra 1 User khi người dùng double click
    row_double_clicked = Signal(User)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Khởi tạo Sql Model và gắn vào Table
        self._model = UserTableModel(DatabaseManager())
        self.setModel(self._model)
        
        # Cấu hình UI: Chọn nguyên dòng, cho phép chọn nhiều, và không cho sửa text trực tiếp
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.ExtendedSelection) 
        self.setEditTriggers(QTableView.NoEditTriggers)

        # Ẩn các cột hệ thống không cần thiết cho user
        self.hide_columns_by_name(["uuid", "created_at", "updated_at"])
        
        # Kết nối sự kiện
        self.doubleClicked.connect(self._on_row_double_clicked)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def hide_columns_by_name(self, column_names: list[str]):
        """Duyệt qua các cột và ẩn đi những cột có tên trong danh sách."""
        record = self._model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setColumnHidden(i, field_name in column_names)

    def _parse_user_from_record(self, record) -> User:
        """Hàm phụ trợ: Chuyển đổi một dòng dữ liệu SQLite thành Object User."""
        status_str = record.value("user_status")
        try:
            status_enum = UserStatus(status_str)
        except ValueError:
            # Giá trị mặc định nếu database có lỗi sai format chuỗi
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
        """Kích hoạt mỗi khi vùng chọn (bôi đen) thay đổi."""
        selected_users = []
        
        # Duyệt qua các dòng đang được chọn
        for index in self.selectionModel().selectedRows():
            if index.isValid():
                record = self._model.record(index.row())
                user = self._parse_user_from_record(record)
                selected_users.append(user)
                
        # Phát tín hiệu mang theo danh sách User
        self.users_selected.emit(selected_users)

    def _on_row_double_clicked(self, index):
        """Kích hoạt khi double click vào một dòng."""
        if not index.isValid():
            return
            
        record = self._model.record(index.row())
        selected_user = self._parse_user_from_record(record)
        self.row_double_clicked.emit(selected_user)
        
    def refresh_data(self):
        """
        Tiện ích để Page gọi khi cần load lại dữ liệu (vd: sau khi sync từ ADB xong).
        """
        self._model.select()