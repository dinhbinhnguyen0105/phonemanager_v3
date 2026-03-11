from typing import List, Dict, Any
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

        # --- Device Table ---
        self.device_table = DeviceTable(self)
        self.devices_layout.addWidget(self.device_table)
        self.main_layout.addLayout(self.devices_layout, 0, 0, 1, 1)

        # --- User Table (Span 2 columns) ---
        self.user_table = UserTable(self)
        self.main_layout.addWidget(self.user_table, 0, 1, 1, 2)

        # ==========================================
        # ROW 1
        # ==========================================

        # --- Column 0: Facebook Accounts Table ---
        self.fb_table = QTableView()
        self.main_layout.addWidget(self.fb_table, 1, 0, 1, 1)

        # --- Column 1: TikTok Accounts Table ---
        self.tt_table = QTableView()
        self.main_layout.addWidget(self.tt_table, 1, 1, 1, 1)

        # --- Column 2: ADB Logs & Input ---
        self.adb_logs_layout = QVBoxLayout()

        self.adb_input = QLineEdit()
        self.adb_input.setPlaceholderText("ADB command")
        self.adb_logs_layout.addWidget(self.adb_input)

        self.log_list = QListWidget()
        self.adb_logs_layout.addWidget(self.log_list)

        self.main_layout.addLayout(self.adb_logs_layout, 1, 2, 1, 1)

    def _setup_placeholders(self):
        """Initialize empty models for tables without data yet"""
        # 1. Facebook Table
        self.fb_model = QStandardItemModel()
        self.fb_model.setHorizontalHeaderLabels(
            ["FB UID", "Username", "Status", "Group"]
        )
        self.fb_table.setModel(self.fb_model)

        # 2. TikTok Table
        self.tt_model = QStandardItemModel()
        self.tt_model.setHorizontalHeaderLabels(["TikTok UID", "Username", "Status"])
        self.tt_table.setModel(self.tt_model)

    def _connect_signals(self):
        # Device status updates
        self.controllers.device_controller.device_state_changed.connect(
            self.on_device_state_changed
        )
        self.controllers.device_controller.device_state_changed.connect(
            self.device_table.on_device_state_changed
        )
        
        # Table interactions
        self.device_table.devices_selected.connect(self.handle_multiple_devices)
        self.device_table.row_double_clicked.connect(
            self.handle_single_device_action
        )
        
        # User synchronization
        self.controllers.user_controller.sync_completed.connect(
            self.on_user_sync_completed
        )
        self.controllers.user_controller.sync_failed.connect(self.on_user_sync_failed)

    # ==========================================
    # LOGIC HANDLERS
    # ==========================================

    def log_message(self, message: str):
        self.log_list.addItem(message)
        self.log_list.scrollToBottom()

    def handle_multiple_devices(self, devices: List[Device]):
        """Handles selection/highlighting of multiple rows in the table"""
        if not devices:
            self.adb_input.clear()
            return

        device_names = [d.device_name for d in devices]
        self.log_message(
            f"🛠 Selecting {len(devices)} devices: {', '.join(device_names)}"
        )

        # Intelligent mode detection
        if len(devices) == 1:
            self.adb_input.setText(f"adb -s {devices[0].device_id} shell ")
        else:
            self.adb_input.setText(
                f"# [Bulk Mode] Command will be applied to {len(devices)} devices..."
            )

    def handle_single_device_action(self, device: Device):
        """Handles double-click actions on a single device"""
        self.log_message(f"⚡ Quick action on: {device.device_name}")
        self.adb_input.setText(f"adb -s {device.device_id} shell ")
        self.adb_input.setFocus()

        self.user_table.setEnabled(False)
        self.controllers.user_controller.fetch_users_for_device(device)

    def on_refresh_clicked(self):
        self.log_message("Refreshing device list...")
        self.device_table._model.select()

    def on_checkroot_clicked(self):
        self.log_message("Check Root feature is currently under development.")

    def on_device_state_changed(self, device: Device):
        if device.device_status == DeviceStatus.ONLINE:
            self.log_message(f"🟢 Connected: {device.device_name} ({device.device_id})")
        else:
            self.log_message(
                f"🔴 Disconnected: {device.device_name} ({device.device_id})"
            )

    def on_user_sync_completed(self, payload: Dict[str, Any]):
        """Triggered after Worker fetches data and Service saves to SQLite"""
        self.log_message("✅ Profile synchronization successful!")

        # 1. Unlock User Table
        self.user_table.setEnabled(True)

        # 2. Reload data from SQLite
        if hasattr(self.user_table, "_model"):
            self.user_table._model.select()

    def on_user_sync_failed(self, error_msg: str):
        """Triggered on ADB connection issues or DB errors"""
        self.log_message(f"❌ Sync Failed: {error_msg}")
        self.user_table.setEnabled(True)