# src\views\pages\settings\settings.py
from PySide6.QtWidgets import QWidget, QMenu, QFileDialog, QAbstractItemView
from PySide6.QtCore import (
    Qt, Slot, QPoint, QItemSelection, QItemSelectionModel, Signal
)
from PySide6.QtGui import (
    QAction, QShortcut, QKeySequence, QMouseEvent
)

from src.controllers._manager_controllers import ControllerManager
from src.entities import Proxy
from src.constants import ProxyStatus, ProxyType
from src.models.table_model import ProxyTableModel
from src.database.connection import DatabaseManager
from src.utils.logger import logger
from src.constants import SettingType
from src.ui.page_settings_ui import Ui_PageSettings


class SettingsPage(QWidget, Ui_PageSettings):
    def __init__(self, controllers: ControllerManager, parent=None):
        super(SettingsPage, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("setting page".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.controllers = controllers

        self.setup_data()
        self.setup_connections()

        self.proxy_model = ProxyTableModel(DatabaseManager())

    def setup_data(self):
        self.setting_input.setTitle("")
        self.setting_value.setDisabled(True)
        self.setting_value.setPlaceholderText("")
        self.setting_save_btn.setDisabled(True)
        self.setting_is_selected.setDisabled(True)
        self.setting_option.clear()
        self.setting_option.addItem("--- Select setting ---")

        for item in SettingType:
            self.setting_option.addItem(item.name, item.value)
    
    def setup_connections(self):
        self.setting_option.currentIndexChanged.connect(self.on_setting_option_changed)
        self.setting_value.textChanged.connect(self.on_setting_value_changed) 
        self.setting_save_btn.clicked.connect(self.on_setting_save_btn_clicked)
        
        self.setting_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setting_table.customContextMenuRequested.connect(self.on_table_context_menu)

    def on_setting_option_changed(self, index: int):
        if index == 0:
            self.setting_value.setDisabled(True)
            self.setting_save_btn.setDisabled(True)
            self.setting_is_selected.setDisabled(True)
            self.setting_value.setPlaceholderText("")
            self.setting_table.setModel(None)
            return
        else:
            self.setting_value.setDisabled(False)
            self.setting_is_selected.setDisabled(False)
        
        current_setting: str = self.setting_option.currentData(Qt.ItemDataRole.UserRole)
        
        if current_setting:
            self.setting_input.setTitle(f"Add new {current_setting}")
            
            if current_setting == SettingType.PROXY.value:
                self.setting_value.setPlaceholderText("Add new rotate url")
                self.setting_is_selected.setChecked(True)
                self.setting_is_selected.setText("Available")

                self.setting_table.setModel(self.proxy_model)
                self.setting_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                self.setting_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
                
                self.proxy_model.select()
                self._hide_columns(["uuid", "created_at", "updated_at"])
            else:
                self.setting_table.setModel(None)
    
    def on_setting_save_btn_clicked(self):
        current_setting: str = self.setting_option.currentData(Qt.ItemDataRole.UserRole)
        
        if current_setting == SettingType.PROXY.value:
            input_value = self.setting_value.text().strip()
            proxy_status = ProxyStatus.AVAILABLE if self.setting_is_selected.isChecked() else ProxyStatus.UNAVAILABLE
            host = ""
            port = 0
            username = ""
            password = ""
            rotate_url = ""
            proxy_type = ProxyType.STATIC
            if input_value.upper() == "DIRECT:0":
                host = "DIRECT"
                port = 0
            elif input_value.startswith(("http://", "https://")):
                rotate_url = input_value
                proxy_type = self.controllers.proxy_controller.classify_proxy_type(input_value)
            else:
                parts = input_value.split(":")
                host = parts[0]
                port = int(parts[1])
                if len(parts) == 4:
                    username = parts[2]
                    password = parts[3]
            proxy = Proxy(
                host=host,
                port=port,
                username=username,
                password=password,
                rotate_url=rotate_url,
                proxy_status=proxy_status,
                proxy_type=proxy_type
            )
            
            self.controllers.proxy_controller.create(proxy)
            
            self.setting_value.clear() 
            self.proxy_model.select()

    def on_setting_value_changed(self, value: str):
        value = value.strip()
        if not value:
            self.setting_save_btn.setDisabled(True)
            return

        current_setting: str = self.setting_option.currentData(Qt.ItemDataRole.UserRole)
        
        if current_setting == SettingType.PROXY.value:
            if value.startswith(("http://", "https://")):
                self.setting_save_btn.setDisabled(False)
                return
            if value.upper() == "DIRECT:0":
                self.setting_save_btn.setDisabled(False)
                return
            parts = value.split(":")
            if len(parts) in [2, 4]:
                host = parts[0]
                port_str = parts[1]
                if port_str.isdigit() and host:
                    self.setting_save_btn.setDisabled(False)
                    return
            self.setting_save_btn.setDisabled(True)
            
    
    def _hide_columns(self, column_names: list[str]):
        if not self.setting_table.model():
            return
        record = self.proxy_model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setting_table.setColumnHidden(i, field_name in column_names)
    
    def on_table_context_menu(self, pos: QPoint):
        current_setting: str = self.setting_option.currentData(Qt.ItemDataRole.UserRole)
        
        if current_setting == SettingType.PROXY.value:
            self.show_proxy_context_menu(pos)

    def show_proxy_context_menu(self, pos: QPoint):
        selected_indexes = self.setting_table.selectionModel().selectedRows()
        if not selected_indexes:
            return

        selected_uuids = []
        uuid_col_index = self.proxy_model.fieldIndex("uuid")
        for index in selected_indexes:
            uuid = self.proxy_model.data(self.proxy_model.index(index.row(), uuid_col_index))
            selected_uuids.append(uuid)

        menu = QMenu(self)
        
        action_check = QAction("Check", self)
        action_set_available = QAction("Set available", self)
        action_set_unavailable = QAction("Set unavailable", self)
        action_delete = QAction("Delete", self)

        action_check.triggered.connect(lambda: self.handle_proxy_actions("check", selected_uuids))
        action_set_available.triggered.connect(lambda: self.handle_proxy_actions("set_available", selected_uuids))
        action_set_unavailable.triggered.connect(lambda: self.handle_proxy_actions("set_unavailable", selected_uuids))
        action_delete.triggered.connect(lambda: self.handle_proxy_actions("delete", selected_uuids))

        menu.addAction(action_check)
        menu.addSeparator()
        menu.addAction(action_set_available)
        menu.addAction(action_set_unavailable)
        menu.addSeparator()
        menu.addAction(action_delete)

        menu.exec(self.setting_table.viewport().mapToGlobal(pos))

    def handle_proxy_actions(self, action: str, uuids: list[str]):
        logger.info(f"Executing '{action}' for {len(uuids)} proxies...")
        
        for uuid in uuids:
            if action == "delete":
                self.controllers.proxy_controller.delete(uuid)
            elif action == "set_available":
                proxy = self.controllers.proxy_controller.get_by_id(uuid)
                if proxy:
                    proxy.proxy_status = ProxyStatus.AVAILABLE
                    self.controllers.proxy_controller.update(proxy)
            elif action == "set_unavailable":
                proxy = self.controllers.proxy_controller.get_by_id(uuid)
                if proxy:
                    proxy.proxy_status = ProxyStatus.UNAVAILABLE
                    self.controllers.proxy_controller.update(proxy)
            elif action == "check":
                pass # TODO: Chèn logic test URL (dùng GenericWorker) như đã làm ở trên
                
        self.proxy_model.select()
    
    def refresh_data(self):
        self.proxy_model.select()