# src/models/table_model.py
from typing import Any
from PySide6.QtSql import QSqlTableModel, QSqlQuery
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QColor, QBrush
from src.constants import DeviceStatus, UserStatus


# ==========================================
# BASE TABLE MODEL
# ==========================================
class BaseTableModel(QSqlTableModel):
    def __init__(self, db_manager, table_name, column_header=None):
        super().__init__(db=db_manager.db)
        self.table_name = table_name
        self.setTable(table_name)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        self.column_headers = column_header or {}
        self.setup_headers()
        self.select()

    def setup_headers(self):
        for i in range(self.columnCount()):
            col_name = self.record().fieldName(i)
            if col_name in self.column_headers:
                self.setHeaderData(
                    i, Qt.Orientation.Horizontal, self.column_headers[col_name]
                )
                
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        flags = super().flags(index)
        col_name = self.record().fieldName(index.column())
        
        editable_columns = [
            "device_name", 
            "user_name", 
            "social_name", 
            "social_group", 
            "social_password"
        ]
        
        if col_name in editable_columns:
            flags |= Qt.ItemFlag.ItemIsEditable
        else:
            flags &= ~Qt.ItemFlag.ItemIsEditable
            
        return flags

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any: # type: ignore
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ForegroundRole:
            col_name = self.record().fieldName(index.column())
            if "status" in col_name:
                status_val = str(super().data(index, Qt.ItemDataRole.DisplayRole)).lower()
                if status_val in ["0", "stopped", "die", "inactive", "offline"]:
                    return QBrush(QColor("#e74c3c"))
                elif status_val in ["1", "running", "live", "active", "online"]:
                    return QBrush(QColor("#2ecc71"))
        if role == Qt.ItemDataRole.DisplayRole:
            col_name = self.record().fieldName(index.column())
            val = super().data(index, Qt.ItemDataRole.EditRole)
            if col_name in ["created_at", "updated_at"] and val:
                return str(val).replace("T", " ").split(".")[0]
            if val is None or val == "":
                return "---"

            return val

        return super().data(index, role)


# ==========================================
# DEVICES TABLE MODEL
# ==========================================
class DeviceTableModel(BaseTableModel):
    """
    Model for the 'devices' table.
    """

    def __init__(self, db_manager):
        headers = {
            "uuid": "System ID",
            "device_id": "Serial/UDID",
            "device_name": "Device Name",
            "device_status": "Status",
            "device_root": "Rooted",
        }
        super().__init__(db_manager, "devices", headers)
        self.setFilter(f"device_status != '{DeviceStatus.OFFLINE.value}'")

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
            
        if role == Qt.ItemDataRole.BackgroundRole:
            return QBrush(QColor("#e8f8f5"))
            
        if role == Qt.ItemDataRole.DisplayRole:
            col_name = self.record().fieldName(index.column())
            val = super().data(index, Qt.ItemDataRole.EditRole)

            if col_name == "device_status":
                return "Online" if str(val).lower() == "online" else "Offline"
            if col_name == "device_root":
                return "Yes" if val in [1, True, "1"] else "No"

        return super().data(index, role)


# ==========================================
# SOCIAL ACCOUNT MODEL
# ==========================================
class SocialTableModel(BaseTableModel):
    def __init__(self, db_manager):
        headers = {
            "social_id": "Social UID",
            "user_uuid": "Profile UUID",
            "social_name": "Account Name",
            "social_status": "Status",
            "social_group": "Group",
            "social_platform": "Platform",
            "social_password": "Password",
        }
        super().__init__(db_manager, "socials", headers)
        self.device_status_map = {}
        self.refresh_caches()

    def refresh_caches(self):
        """Map uuid của Social với device_status của Device tương ứng"""
        self.device_status_map = {}
        query = QSqlQuery("""
            SELECT s.uuid, d.device_status 
            FROM socials s
            LEFT JOIN users u ON s.user_uuid = u.uuid
            LEFT JOIN devices d ON u.device_uuid = d.uuid
        """, self.database())
        while query.next():
            self.device_status_map[query.value(0)] = query.value(1)

    def select(self):
        self.refresh_caches()
        return super().select()
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
            
        if role == Qt.ItemDataRole.BackgroundRole:
            social_uuid = self.record(index.row()).value("uuid")
            dev_status = self.device_status_map.get(social_uuid)
            
            if not dev_status or str(dev_status).lower() != "online":
                return QBrush(QColor("#e2e5e9"))
            return QBrush(QColor("#e8f8f5"))
            
        if role == Qt.ItemDataRole.DisplayRole:
            col_name = self.record().fieldName(index.column())
            val = super().data(index, Qt.ItemDataRole.EditRole)

            if col_name == "social_status":
                return "Live" if int(val or 0) == 1 else "Dead"

        return super().data(index, role)



# ==========================================
# PROXY MODEL
# ==========================================
class ProxyTableModel(BaseTableModel):
    """
    Model for the 'proxies' table.
    """

    def __init__(self, db_manager):
        headers = {
            "proxy_id": "Proxy ID",
            "value": "IP:Port",
            "proxy_type": "Type",
            "proxy_status": "Status",
        }
        super().__init__(db_manager, "proxies", headers)


# ==========================================
# USER (PROFILE) TABLE MODEL
# ==========================================
class UserTableModel(BaseTableModel):
    def __init__(self, db_manager):
        headers = {
            "user_id": "Profile ID",
            "user_name": "Profile Name",
            "user_status": "Status",
            "device_uuid": "Device",
        }

        super().__init__(db_manager, "users", headers)
        self.device_map = {}
        self.social_map = {}
        self.refresh_caches()

    def refresh_caches(self):
        self.device_map = {}
        query = QSqlQuery("SELECT uuid, device_name FROM devices", self.database())
        while query.next():
            self.device_map[query.value(0)] = query.value(1)
        self.social_map = {}
        query = QSqlQuery("SELECT uuid, social_name FROM socials", self.database())
        while query.next():
            self.social_map[query.value(0)] = query.value(1)

    def select(self):
        self.refresh_caches()
        return super().select()

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            col_name = self.record().fieldName(index.column())
            raw_value = super().data(index, Qt.ItemDataRole.EditRole)

            if col_name == "user_status":
                return UserStatus(raw_value).value.capitalize()

            if col_name == "device_uuid":
                return self.device_map.get(raw_value, "---")

            if col_name == "social_uuid":
                return self.social_map.get(raw_value, "---")
        if role == Qt.ItemDataRole.ForegroundRole:
            col_name = self.record().fieldName(index.column())
            # if col_name == "user_status":
            #     return UserStatus.ACTIVE.value.capitalize() if 
            if col_name in ["device_uuid", "social_uuid"]:
                raw_value = super().data(index, Qt.ItemDataRole.EditRole)
                if not raw_value:
                    return QBrush(QColor("#bdc3c7"))
        return super().data(index, role)