# src/views/pages/home/home.py
from typing import List, Dict, Any, Optional
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QLineEdit,
)
from src.entities import Device, Proxy, User
from src.constants import DeviceStatus
from src.controllers._manager_controllers import ControllerManager

from src.views.pages.home.device_table import DeviceTable
from src.views.pages.home.user_table import UserTable
from src.views.pages.home.social_table import SocialTable

class HomePage(QWidget):
    message = Signal(str)

    def __init__(self, controllers: ControllerManager, parent=None):
        super().__init__(parent)
        self.controllers = controllers
        self._setup_ui()
        self._connect_signals()

        self.device_selected: Optional[Device] = None
        self.users_selected: List[User] = []

    def _setup_ui(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        
        self.devices_layout = QVBoxLayout()
        self.device_table = DeviceTable(self.controllers, self)
        
        self.adb_input = QLineEdit()
        self.adb_input.setPlaceholderText("ADB command")
        
        self.devices_layout.addWidget(self.device_table)
        self.devices_layout.addWidget(self.adb_input)
        
        self.main_layout.addLayout(self.devices_layout, 0, 0, 1, 2)

        self.user_table = UserTable(self.controllers, self)
        self.main_layout.addWidget(self.user_table, 1, 0)

        self.social_table = SocialTable(self.controllers, self)
        self.main_layout.addWidget(self.social_table, 1, 1)

    def _connect_signals(self):
        self.device_table.log_msg.connect(self.log_message)
        self.user_table.log_msg.connect(self.log_message)
        self.social_table.log_msg.connect(self.log_message)

        self.device_table.devices_selected.connect(self.handle_multiple_devices)
        self.device_table.row_double_clicked.connect(self.handle_single_device_action)
        self.user_table.users_selected.connect(self.handle_users_selected)
        
        self.user_table.social_data_changed.connect(self.social_table.refresh_data)

        self.controllers.device_controller.device_state_changed.connect(self.on_device_state_changed)
        self.controllers.device_controller.device_state_changed.connect(self.device_table.on_device_state_changed)
        
        self.controllers.device_controller.redsocks_enable_success.connect(self._on_redsocks_enable_success)
        self.controllers.device_controller.redsocks_enable_failed.connect(self._on_redsocks_enable_failed)
        self.controllers.device_controller.redsocks_disable_success.connect(self._on_redsocks_disable_success)
        
        self.controllers.proxy_controller.rotate_proxy_success.connect(self._on_proxy_rotate_success)
        self.controllers.proxy_controller.rotate_proxy_failed.connect(self._on_proxy_rotate_failed)
        
        self.controllers.user_controller.user_sync_completed.connect(self.on_user_sync_completed)
        self.controllers.user_controller.user_sync_failed.connect(self.on_user_sync_failed)

    def log_message(self, msg: str):
        self.message.emit(msg)

    def handle_multiple_devices(self, devices: List[Device]):
        if not devices:
            self.adb_input.clear()
            self.clear_sub_tables()
            self.device_selected = None
            self.user_table.current_device = None
            return

        device_names = [d.device_name for d in devices]
        self.log_message(f"🛠 Selecting {len(devices)} devices: {', '.join(device_names)}")
        
        if len(devices) == 1:
            self.adb_input.setText(f"adb -s {devices[0].device_id} shell ")
            self.device_selected = devices[0]
            self.user_table.current_device = devices[0]
            
            if hasattr(self.user_table, "_model"):
                self.user_table._model.setFilter(f"device_uuid = '{devices[0].uuid}'")
                self.user_table._model.select()
        else:
            self.device_selected = None
            self.user_table.current_device = None
            self.adb_input.setText(f"# [Bulk Mode] Command will be applied to {len(devices)} devices...")

    def handle_single_device_action(self, device: Device):
        self.log_message(f"⚡ Quick action on: {device.device_name}")
        self.adb_input.setText(f"adb -s {device.device_id} shell ")
        self.adb_input.setFocus()
        self.user_table.setEnabled(False)
        self.controllers.user_controller.fetch_users_for_device(device)
    
    def handle_users_selected(self, users: List[User]):
        self.users_selected = users
        if not users:
            self.social_table._model.setFilter("1=0")
        else:
            user_uuids = [u.uuid for u in users]
            if not user_uuids:
                self.social_table._model.setFilter("1=0")
            else:
                uuids_str = ", ".join([f"'{uid}'" for uid in user_uuids])
                self.social_table._model.setFilter(f"user_uuid IN ({uuids_str})")
        self.social_table._model.select()

    def clear_sub_tables(self):
        if hasattr(self.user_table, "_model"):
            self.user_table._model.setFilter("1=0")
            self.user_table._model.select()
        if hasattr(self.social_table, "_model"):
            self.social_table._model.setFilter("1=0")
            self.social_table._model.select()

    def on_device_state_changed(self, device: Device):
        if device.device_status == DeviceStatus.ONLINE:
            self.log_message(f"🟢 Connected: {device.device_name} ({device.device_id})")
        else:
            self.log_message(f"🔴 Disconnected: {device.device_name} ({device.device_id})")

    def on_user_sync_completed(self, device: Optional[Device], users_data: List[User]):
        self.log_message("✔️ Profile synchronization successful!")
        if not self.user_table.isEnabled():
            self.user_table.setEnabled(True)
        if hasattr(self.user_table, "_model"):
            self.user_table._model.select()
            if device:
                self.user_table._model.setFilter(f"device_uuid = '{device.uuid}'")

    def on_user_sync_failed(self, error_msg: str):
        self.log_message(f"❌ Sync Failed: {error_msg}")
        self.user_table.setEnabled(True)
        
    def _on_proxy_rotate_success(self, devices: List[Device], proxy: Proxy):
        self.log_message(f"✔️ Proxy rotated successfully! New IP: {proxy.host}:{proxy.port}")
        self.log_message(f"🌐 Applying active Proxy ({proxy.host}:{proxy.port}) to {len(devices)} devices...")
        self.controllers.device_controller.enable_redsocks(
            devices=devices, ip=proxy.host, port=proxy.port, username=proxy.username, password=proxy.password, ptype=proxy.proxy_type.value
        )

    def _on_proxy_rotate_failed(self, devices: List[Device], proxy: Proxy, error_msg: str):
        self.log_message(f"❌ Proxy rotation failed: {error_msg}")

    def _on_redsocks_enable_success(self, device: Device, result: str):
        self.log_message(f"✔️✔️✔️ Device {device.device_id} - {device.device_name}: Redsocks applied successfully!")
        
    def _on_redsocks_enable_failed(self, device: Device, result: str):
        self.log_message(f"❌ Device {device.device_id} - {device.device_name}: Redsocks application failed: {result}")

    def _on_redsocks_disable_success(self, device: Device):
        self.log_message(f"Device {device.device_id} - {device.device_name}: Redsocks disabled successfully!")
    
    def refresh_data(self):
        self.device_table.refresh_data()
        self.user_table.refresh_data()
        self.social_table.refresh_data()