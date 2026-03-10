# src/drivers/adb/controller.py
import re
from typing import List, Dict, Optional
from adbutils import adb
from adbutils.errors import AdbError
from src.entities import UserStatus
from src.drivers.adb.exceptions import ADBConnectionError, ADBCommandError, DeviceNotFoundError

DEFAULT_APP_PERMISSIONS = [
    "android.permission.CAMERA",
    "android.permission.RECORD_AUDIO",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.READ_CONTACTS",
    "android.permission.ACCESS_NETWORK_STATE"
]

class ADBController:
    def __init__(self, device_id: str):
        self.device_id = device_id
        try:
            self.device = adb.device(device_id)
        except AdbError as e:
            raise ADBConnectionError(f"Failed to connect to device: {e}")
    
    def _shell(self, command: str) -> str:
        try:
            return self.device.shell(command)
        except AdbError as e:
            raise ADBCommandError(f"Failed to execute command: {e}")
    
    def get_screen_size(self) -> Dict[str, int]:
        output = self._shell("wm size")
        match = re.search(r"(\d+)x(\d+)", output)
        if match:
            return {"width": int(match.group(1)), "height": int(match.group(2))}
        else:
            raise ADBCommandError("Failed to parse screen size output")
    
    def get_users(self) -> List[Dict[str, str]]:
        output = self._shell("pm list users")
        pattern = re.compile(r"UserInfo\{(\d+):([^:]+):")
        users = []
        for line in output.splitlines():
            match = pattern.search(line)
            if match:
                is_running = "running" in line
                users.append({
                    "user_id": int(match.group(1)),
                    "user_name": "root" if match.group(2).lower() == "owner" else match.group(2),
                    "user_status": UserStatus.ACTIVE if is_running else UserStatus.INACTIVE
                })
        return users
    
    def check_root(self) -> bool:
        try:
            su_check = self._shell("su -c 'echo is_rooted'").strip()
            if "is_rooted" in su_check:
                return True
            return False
        except ADBCommandError:
            return False
    
    def create_user(self, username: str) -> Optional[int]:
        output = self._shell(f"pm create-user {username}")
        match = re.search(r"id\s+(\d+)", output)
        if match:
            return int(match.group(1))
        return None
    
    def remove_user(self, user_id: int) -> bool:
        try:
            self._shell(f"pm remove-user {user_id}")
            return True
        except ADBCommandError:
            return False
    
    def switch_user(self, user_id: int) -> bool:
        output = self._shell(f"am switch-user {user_id}")
        return "error" not in output.lower()

    def is_apk_installed(self, user_id: int, package_name: str) -> bool:
        output = self._shell(f"pm list packages --user {user_id} {package_name}")
        return package_name in output
    
    def install_new_apk(self, user_id: int, apk_path: str) -> bool: 
        output = self._shell(f"pm install -r --user {user_id} {apk_path}")
        return "success" in output.lower()

    def install_existed_apk(self, user_id: int, package_name: str) -> bool: 
        output = self._shell(f"pm install-existing --user {user_id} {package_name}")
        return "installed" in output.lower()

    def uninstall_apk(self, user_id: int, package_name: str) -> bool: 
        output = self._shell(f"pm uninstall --user {user_id} {package_name}")
        return "success" in output.lower()

    def grand_apk_permission(self, user_id: int, package_name: str, permissions: List[str] = DEFAULT_APP_PERMISSIONS) -> bool:
        success = True
        for perm in permissions:
            output = self._shell(f"pm grant --user {user_id} {package_name} {perm}")
            if "error" in output.lower():
                success = False
        return success

    def get_public_ip(self) -> str:
        return self._shell("curl ifconfig.me")
