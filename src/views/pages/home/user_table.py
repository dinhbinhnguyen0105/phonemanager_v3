# src/views/pages/home/user_table.py
from typing import List, Optional, TYPE_CHECKING
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QTableView, QAbstractItemView, QMenu, QDialog, QMessageBox
from src.models.table_model import UserTableModel
from src.database.connection import DatabaseManager
from src.entities import User, UserStatus, Device, Social

from src.views.pages.home.dialog_create_tiktok_account import Dialog_CreateTikTokAccount
from src.views.pages.home.dialog_create_facebook_account import Dialog_CreateFacebookAccount

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager


class UserTable(QTableView):
    users_selected = Signal(list) 
    row_double_clicked = Signal(User)
    
    log_msg = Signal(str)
    social_data_changed = Signal() # Signal to notify HomePage to reload SocialTable

    def __init__(self, controllers: "ControllerManager", parent=None):
        super().__init__(parent)
        self.controllers = controllers
        self.current_device: Optional[Device] = None # Stores the device currently being operated
        self.controllers.user_controller.user_switched.connect(self._on_user_switched)
        self._model = UserTableModel(DatabaseManager())
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
        
        users = []
        for idx in selected_indexes:
            if idx.isValid():
                record = self._model.record(idx.row())
                users.append(self._parse_user_from_record(record))
        
        menu = QMenu(self)
        install_menu = menu.addMenu("Install app")
        install_fb = install_menu.addAction("Facebook")
        install_tt = install_menu.addAction("TikTok")
        
        install_fb.triggered.connect(lambda: self._install_app(users, "Facebook"))
        install_tt.triggered.connect(lambda: self._install_app(users, "TikTok"))

        if len(users) == 1:
            menu.addSeparator()
            
            link_menu = menu.addMenu("Link social accounts")
            link_fb = link_menu.addAction("Facebook")
            link_tt = link_menu.addAction("TikTok")
            link_fb.triggered.connect(lambda: self._handle_link_social(users[0], "Facebook"))
            link_tt.triggered.connect(lambda: self._handle_link_social(users[0], "TikTok"))

            menu.addSeparator()
            switch_action = menu.addAction("Switch user")
            switch_action.triggered.connect(lambda: self._switch_user(users[0]))

            delete_action = menu.addAction("Delete this user")
            delete_action.triggered.connect(lambda: self._delete_user(users[0]))

        menu.exec(self.viewport().mapToGlobal(pos))

    # ==========================================
    # ACTION SLOTS
    # ==========================================
    def _install_app(self, users: list[User], app_name: str):
        self.log_msg.emit(f"📦 Installing {app_name} for {len(users)} profiles.")
        if not self.current_device:
            return
        self.controllers.user_controller.install_app(self.current_device, users, app_name)
        self.controllers.user_controller.app_installed.connect(self._on_installed_app)

    def _switch_user(self, user: User):
        self.log_msg.emit(f"🔄 Switching to user: {user.user_name} (ID: {user.user_id})")
        if not self.current_device:
            return
        self.controllers.user_controller.switch_user(self.current_device, user)

    def _delete_user(self, user: User):
        if int(user.user_id) == 0:
            self.log_msg.emit(f"🟠 Cannot delete root user.")
            return
        
        device = self.controllers.device_controller.get_by_id(user.device_uuid)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Deletion")
        msg_box.setText(f"Are you sure you want to delete profile '{user.user_name}'?")
        msg_box.setInformativeText(
            "• Select 'Delete' to only remove the profile from the phone.\n"
            "• Select 'Delete all' to remove the profile AND all associated Social accounts from the Database."
        )
        msg_box.setIcon(QMessageBox.Icon.Warning)

        btn_delete_all = msg_box.addButton("Delete all", QMessageBox.ButtonRole.DestructiveRole)
        btn_delete = msg_box.addButton("Delete", QMessageBox.ButtonRole.AcceptRole)
        btn_cancel = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == btn_cancel:
            return

        if clicked_button == btn_delete_all:
            self.log_msg.emit(f"🗑 Cleaning up social accounts for user {user.user_name}...")
            
            social_accounts = self.controllers.social_controller.get_accounts_by_profile(user.uuid)
            for account in social_accounts:
                self.controllers.social_controller.delete(account.uuid)
            self.log_msg.emit(f"✔️ Deleted {len(social_accounts)} associated social accounts.")
            self.social_data_changed.emit()
            
        self.controllers.user_controller.delete_user(device, user)

    def _handle_link_social(self, user: User, platform: str):
        if platform == "Facebook":
            dialog = Dialog_CreateFacebookAccount(self)
        elif platform == "TikTok":
            dialog = Dialog_CreateTikTokAccount(self)
        else:
            return
            
        if dialog.exec() == QDialog.DialogCode.Accepted:
            social_data = dialog.get_data()
            self.log_msg.emit(f"🔗 Linking {platform} account for profile: {user.user_name}")
            
            social_data.user_uuid = user.uuid 
            social_new_data = self.controllers.social_controller.create(social_data)
            
            if not social_new_data:
                self.log_msg.emit(f"❌ Failed to link Social account.")
            else:
                self.log_msg.emit(f"✔️ Successfully added {platform} account to Database.")
                self.social_data_changed.emit()

    def _hide_columns(self, column_names: list[str]):
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
    
    def _on_installed_app(self, device: Device, apk_name: str, is_success: bool):
        if is_success:
            self.log_msg.emit(f"✔️ Installed {apk_name}")
        else:
            self.log_msg.emit(f"❌ Failed to install {apk_name}")
    
    def _on_user_switched(self, device: Device, user: User):
        self.current_device = device
        self.log_msg.emit(f"✔️ Switched to user {user.user_name} on device {device.device_name}")
        # self.controllers.device_controller.state

    def refresh_data(self):
        self._model.select()