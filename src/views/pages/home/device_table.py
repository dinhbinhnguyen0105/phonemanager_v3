# src/views/pages/home/device_table.py
from typing import List, TYPE_CHECKING
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QTableView, QAbstractItemView, QMenu

from src.entities import Device, Proxy
from src.constants import DeviceStatus, ProxyStatus
from src.models.table_model import DeviceTableModel
from src.database.connection import DatabaseManager
from src.views.pages.home.dialog_create_new_user import Dialog_CreateNewUser
from src.drivers.adb.adb_controller import ADBController
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager



class DeviceTable(QTableView):
    devices_selected = Signal(list) 
    row_double_clicked = Signal(Device)
    
    log_msg = Signal(str)

    def __init__(self, controllers: "ControllerManager", parent=None):
        super().__init__(parent)
        self.controllers = controllers

        self.controllers.device_controller.msg_signal.connect(self.log_msg.emit)
        
        self._model = DeviceTableModel(DatabaseManager())
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | 
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        self._hide_columns(["uuid", "created_at", "updated_at"])
        self.doubleClicked.connect(self._on_row_double_clicked)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, pos):
        selected_indexes = self.selectionModel().selectedRows()
        if not selected_indexes:
            return
        
        devices = []
        for idx in selected_indexes:
            if idx.isValid():
                record = self._model.record(idx.row())
                devices.append(self._parse_device_from_record(record))
        
        menu = QMenu(self)

        if len(devices) == 1:
            create_act = menu.addAction("Create New User")
            create_act.triggered.connect(lambda: self._handle_create_new_user(devices[0]))
            menu.addSeparator()

        menu.addAction("Launch (scrcpy)", lambda: self._launch_devices(devices))
        menu.addSeparator()

        menu.addAction("📸 Take Screenshot", lambda: self._take_screenshot(devices))
        menu.addSeparator()

        menu.addAction("Enable Internet", lambda : self._on_enable_internet_connection(devices))
        menu.addAction("Disable Internet", lambda : self._on_disable_internet_connection(devices))
        menu.addSeparator()

        menu.addAction("⚙️ Set Max Users (10)", lambda: self._set_max_users(devices))
        menu.addSeparator()

        enable_redsocks_act = menu.addAction("Enable Redsocks (Virtual Proxy)")

        enable_redsocks_act = menu.addAction("Enable Redsocks (Virtual Proxy)")
        enable_redsocks_act.triggered.connect(lambda: self._enable_redsocks(devices))

        disable_redsocks_act = menu.addAction("Disable Redsocks")
        disable_redsocks_act.triggered.connect(lambda: self._disable_redsocks(devices))

        enable_redsocks_act.setDisabled(False)
        disable_redsocks_act.setDisabled(False)
        menu.addSeparator()

        rotate_menu = menu.addMenu("Rotate & Apply Proxy")
        available_proxies = self.controllers.proxy_controller.service.repo.get_by_status(ProxyStatus.AVAILABLE)
        
        if not available_proxies:
            empty_act = rotate_menu.addAction("No proxies available")
            empty_act.setEnabled(False)
        else:
            for proxy in available_proxies:
                display_text = proxy.rotate_url if proxy.rotate_url else f"{proxy.host}:{proxy.port}"
                if len(display_text) > 40:
                    display_text = display_text[:37] + "..."
                
                proxy_act = rotate_menu.addAction(display_text)
                proxy_act.triggered.connect(
                    lambda checked=False, p=proxy, devs=devices: self._rotate_proxy(devs, p)
                )

        menu.exec(self.viewport().mapToGlobal(pos))

    # ==========================================
    # ACTION SLOTS
    # ==========================================
    def _handle_create_new_user(self, device: Device):
        if not device.device_root:
            self.log_msg.emit(f"🟠 Device must be rooted to create a user. ({device.device_id})")
            return
            
        dialog = Dialog_CreateNewUser(self)
        dialog.setWindowTitle(f"Create user for {device.device_name} ({device.device_id})")

        if dialog.exec() == Dialog_CreateNewUser.DialogCode.Accepted:
            username = dialog.get_username()
            if username:
                self.log_msg.emit(f"➕ Creating new user: {username}")
                logger.info(f"➕ Creating new user: {username}")
                self.controllers.user_controller.create_new_user(device, username)

    def _launch_devices(self, devices: list[Device]):
        self.controllers.device_controller.launch_scrcpy(devices)
        names = [d.device_name for d in devices]
        self.log_msg.emit(f"📱 Launching scrcpy for: {', '.join(names)}")
    
    def _take_screenshot(self, devices: list[Device]):
        self.controllers.device_controller.take_screenshot(devices)
        self.log_msg.emit(f"📸 Taked screenshot for {len(devices)} devices.")

    def _enable_redsocks(self, devices: list[Device]):
        dummy_ip = "0.0.0.0"
        dummy_port = 0
        self.log_msg.emit(f"🌐 Enabling Dummy Proxy ({dummy_ip}:{dummy_port}) for {len(devices)} devices.")
        self.controllers.device_controller.enable_redsocks(
            devices=devices, ip=dummy_ip, port=dummy_port, ptype="local"
        )

    def _disable_redsocks(self, devices: list[Device]):
        self.log_msg.emit(f"🚫 Disabling Redsocks for {len(devices)} devices.")
        self.controllers.device_controller.disable_redsocks(devices)

    def _rotate_proxy(self, devices: list[Device], proxy: Proxy):
        self.log_msg.emit(f"🔄 Rotating Proxy ({proxy.rotate_url[:30]}...)")
        self.controllers.proxy_controller.rotate_proxy_async(devices, proxy)
    
    def _on_enable_internet_connection(self, devices: List[Device]):
        for device in devices:
            adb_controller = ADBController(device.device_id)
            result = adb_controller.enable_internet()
            self.log_msg.emit(f"🌐 Enable internet connection for {device.device_id}: {result}")

    def _on_disable_internet_connection(self, devices: List[Device]):
        for device in devices:
            adb_controller = ADBController(device.device_id)
            result = adb_controller.disable_internet()
            self.log_msg.emit(f"🌐 Disable internet connection for {device.device_id}: {result}")


    def _hide_columns(self, column_names: list[str]):
        record = self._model.record()
        for i in range(record.count()):
            field_name = record.fieldName(i)
            self.setColumnHidden(i, field_name in column_names)

    def _parse_device_from_record(self, record) -> Device:
        status_str = record.value("device_status")
        try:
            status_enum = DeviceStatus(status_str)
        except ValueError:
            status_enum = DeviceStatus.OFFLINE
            
        return Device(
            uuid=record.value("uuid"),
            device_id=record.value("device_id"),
            device_name=record.value("device_name"),
            device_status=status_enum,
            device_root=bool(record.value("device_root")),
            created_at=record.value("created_at"),
            updated_at=record.value("updated_at")
        )

    def _on_selection_changed(self, selected, deselected):
        selected_devices = []
        for index in self.selectionModel().selectedRows():
            if index.isValid():
                record = self._model.record(index.row())
                device = self._parse_device_from_record(record)
                selected_devices.append(device)
        self.devices_selected.emit(selected_devices)

    def _on_row_double_clicked(self, index):
        if not index.isValid():
            return
        record = self._model.record(index.row())
        selected_device = self._parse_device_from_record(record)
        self.row_double_clicked.emit(selected_device)

    def _set_max_users(self, devices: List[Device]):
        """
        Triggers the ADBController to configure Multi-User limits for the selected devices.

        This method iterates through a list of device objects, checks for root 
        privileges, and attempts to set the 'fw.max_users' system property to 10. 
        It provides real-time feedback via log signals regarding the success or 
        failure of the operation for each device.

        Args:
            devices (List[Device]): A list of Device entities to be configured.
        """
        for device in devices:
            if not device.device_root:
                self.log_msg.emit(f"⚠️ Device {device.device_id} is not rooted; the command may be rejected.")
                
            adb_controller = ADBController(device.device_id)
            result = adb_controller.set_max_user(max_users=10)
            
            if result:
                self.log_msg.emit(f"⚙️ Successfully set fw.max_users = 10 for {device.device_id}")
            else:
                self.log_msg.emit(f"❌ Failed to configure Max Users for {device.device_id}. Check terminal logs.")
        
    def on_device_state_changed(self, device: Device):
        self._model.select()
    
    def refresh_data(self):
        self._model.select()