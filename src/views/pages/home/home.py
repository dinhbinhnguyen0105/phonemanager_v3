# src/views/pages/device/devices.py
from typing import List
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QTableView,
    QLineEdit,
    QListWidget,
)
from PySide6.QtGui import QStandardItemModel
from src.entities import Device
from src.constants import DeviceStatus
from src.controllers._manager_controllers import ControllerManager

from src.views.pages.home.device_table import DeviceTable
from src.views.pages.home.user_table import UserTable


class HomePage(QWidget):
    def __init__(self, controllers: ControllerManager, parent=None):
        super().__init__(parent)
        self.controllers = controllers
        self._setup_ui()
        self._setup_placeholders()
        self._connect_signals()

    def _setup_ui(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.devices_layout = QVBoxLayout()

        self.device__device_table = DeviceTable(self)
        self.devices_layout.addWidget(self.device__device_table)
        self.main_layout.addLayout(self.devices_layout, 0, 0, 1, 1)

        # --- Cột 1 & 2 (Span 2 cột): Bảng Users ---
        self.table_users = UserTable(self)
        self.main_layout.addWidget(self.table_users, 0, 1, 1, 2)

        # ==========================================
        # HÀNG 1 (ROW 1)
        # ==========================================

        # --- Cột 0: Bảng FB Accounts ---
        self.table_fb = QTableView()
        self.main_layout.addWidget(self.table_fb, 1, 0, 1, 1)

        # --- Cột 1: Bảng TikTok Accounts ---
        self.table_tt = QTableView()
        self.main_layout.addWidget(self.table_tt, 1, 1, 1, 1)

        self.adb_logs_layout = QVBoxLayout()

        self.input_adb = QLineEdit()
        self.input_adb.setPlaceholderText("ADB command")
        self.adb_logs_layout.addWidget(self.input_adb)

        self.list_logs = QListWidget()
        self.adb_logs_layout.addWidget(self.list_logs)

        self.main_layout.addLayout(self.adb_logs_layout, 1, 2, 1, 1)

    def _setup_placeholders(self):
        """Khởi tạo các Model rỗng cho các bảng chưa có data"""
        # 2. Bảng Facebook
        self.fb_model = QStandardItemModel()
        self.fb_model.setHorizontalHeaderLabels(
            ["FB UID", "Username", "Status", "Group"]
        )
        self.table_fb.setModel(self.fb_model)

        # 3. Bảng TikTok
        self.tt_model = QStandardItemModel()
        self.tt_model.setHorizontalHeaderLabels(["TikTok UID", "Username", "Status"])
        self.table_tt.setModel(self.tt_model)

    def _connect_signals(self):
        self.controllers.device_controller.device_state_changed.connect(
            self.on_device_state_changed
        )
        self.controllers.device_controller.device_state_changed.connect(
            self.device__device_table.on_device_state_changed
        )
        self.device__device_table.devices_selected.connect(self.handle_multiple_devices)
        self.device__device_table.row_double_clicked.connect(
            self.handle_single_device_action
        )
        self.controllers.user_controller.sync_completed.connect(
            self.on_user_sync_completed
        )
        self.controllers.user_controller.sync_failed.connect(self.on_user_sync_failed)

    # ==========================================
    # LOGIC XỬ LÝ
    # ==========================================

    def log_message(self, message: str):
        self.list_logs.addItem(message)
        self.list_logs.scrollToBottom()

    def handle_multiple_devices(self, devices: List[Device]):
        """Xử lý khi người dùng chọn/quét nhiều dòng trên bảng"""
        if not devices:
            self.input_adb.clear()
            return

        # Lấy danh sách tên hiển thị
        device_names = [d.device_name for d in devices]
        self.log_message(
            f"🛠 Đang chọn {len(devices)} thiết bị: {', '.join(device_names)}"
        )

        # Thông minh nhận diện chế độ
        if len(devices) == 1:
            self.input_adb.setText(f"adb -s {devices[0].device_id} shell ")
        else:
            self.input_adb.setText(
                f"# [Bulk Mode] Sẽ áp dụng lệnh cho {len(devices)} thiết bị..."
            )

    def handle_single_device_action(self, device: Device):
        """Xử lý khi người dùng click đúp vào 1 máy"""
        self.log_message(f"⚡ Thao tác nhanh trên: {device.device_name}")
        self.input_adb.setText(f"adb -s {device.device_id} shell ")
        self.input_adb.setFocus()

        self.table_users.setEnabled(False)
        self.controllers.user_controller.fetch_users_for_device(device)

    def on_refresh_clicked(self):
        self.log_message("Đang làm mới danh sách thiết bị...")
        self.device__device_table._model.select()

    def on_checkroot_clicked(self):
        self.log_message("Tính năng Check Root đang được phát triển.")

    def on_device_state_changed(self, device: Device):
        if device.device_status == DeviceStatus.ONLINE:
            self.log_message(f"🟢 Connected: {device.device_name} ({device.device_id})")
        else:
            self.log_message(
                f"🔴 Disconnected: {device.device_name} ({device.device_id})"
            )

    def on_user_sync_completed(self, device_uuid: str):
        """Được gọi khi Worker lấy data và Service lưu SQLite xong"""
        self.log_message(f"✅ Đồng bộ profiles thành công!")

        # 1. Mở khóa bảng User
        self.table_users.setEnabled(True)

        # 2. Yêu cầu UserTable load lại data từ SQLite
        # (Giả định UserTable của bạn lưu QSqlTableModel trong self._model)
        if hasattr(self.table_users, "_model"):
            self.table_users._model.select()

    def on_user_sync_failed(self, error_msg: str):
        """Được gọi nếu lỗi kết nối ADB hoặc lỗi DB"""
        self.log_message(f"❌ Lỗi đồng bộ: {error_msg}")

        # Vẫn phải mở khóa lại bảng để hệ thống không bị kẹt
        self.table_users.setEnabled(True)
