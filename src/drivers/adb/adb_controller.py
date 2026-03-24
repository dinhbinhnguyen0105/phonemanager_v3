# src/drivers/adb/controller.py
import os
import re
from time import sleep
from datetime import datetime
from typing import List, Dict, Optional
from adbutils import adb
from adbutils.errors import AdbError
from src.constants import UserStatus
from src.entities import User
from src.drivers.adb.exceptions import ADBConnectionError, ADBCommandError, DeviceNotFoundError
from src.utils.yaml_handler import settings

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
    
    def create_user(self, username: str) -> Optional[User]:
        output = self._shell(f"pm create-user {username}")
        match = re.search(r"id\s+(\d+)", output)
        if match:
            return User(
                user_id=int(match.group(1)),
                user_name=username,
                user_status=UserStatus.INACTIVE
            )
        return None
    
    def get_current_user(self) -> int:
        """Gets the ID of the user currently displayed on the screen"""
        try:
            output = self._shell("am get-current-user").strip()
            return int(output)
        except (ADBCommandError, ValueError):
            return 0
    

    def switch_user(self, user_id: int) -> bool:
        """
        Switches the User, stops all other background users (except root 0), 
        and performs a deep RAM cleanup.
        """
        try:
            current_user = self.get_current_user()
            if current_user != user_id:                
                output = self._shell(f"am switch-user {user_id}")
                if "error" in output.lower():
                    return False
                success = False
                for _ in range(15):
                    sleep(1)
                    current_user = self.get_current_user()
                    if int(current_user) == int(user_id):
                        success = True
                        break
                if not success:
                    return False
            all_users = self.get_users()

            for u in all_users:
                uid = int(u["user_id"])
                if uid != 0 and uid != user_id:
                    self._shell(f"am stop-user -f {uid}")
            self._shell("am kill-all") 
            self._shell("su -c 'pm trim-caches 999G'") 
            self._shell("su -c 'echo 3 > /proc/sys/vm/drop_caches'")

            return True
        except ADBCommandError:
            return False
        
    def remove_user(self, user_id: int) -> bool:
        try:
            self.switch_user(0)
            sleep(3)
            self._shell(f"pm remove-user {user_id}")
            return True
        except ADBCommandError:
            return False
    
    
    def install_app_for_users(self, app_name: str, user_ids: List[int]) -> bool:
        apk_name = ""
        apk_path =""
        if "tiktok" in app_name.lower():
            apk_name = "com.zhiliaoapp.musically"
            apk_path = settings.repositories.tiktok_path # type: ignore
        elif "facebook" in app_name.lower():
            apk_name = "com.facebook.katana"
            apk_path = settings.repositories.facebook_path # type: ignore
        else:
            return False
        
            
        if not self.is_apk_installed(0, apk_name):
            self.install_new_apk(0, apk_path)
        for user_id in user_ids:
            self.install_existed_apk(user_id, apk_name)
        return True

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

    def disable_internet(self) -> bool:
        """
        Chặn toàn bộ mạng (IPv4). An toàn không dính lỗi dội rule.
        """
        try:
            # Gộp thành 1 chuỗi script, dùng 2>/dev/null để giấu đi các lỗi lặt vặt (như chain đã tồn tại)
            script = (
                "iptables -N FARM_BLOCK 2>/dev/null; "
                "iptables -F FARM_BLOCK; "
                "iptables -A FARM_BLOCK -p tcp --sport 5555 -j RETURN; "
                "iptables -A FARM_BLOCK -j DROP; "
                "iptables -D OUTPUT -j FARM_BLOCK 2>/dev/null; " # Xóa cũ
                "iptables -D OUTPUT -j FARM_BLOCK 2>/dev/null; " # Xóa dự phòng
                "iptables -I OUTPUT 1 -j FARM_BLOCK"            # Chèn mới vào Top 1
            )
            out = self._shell(f"su -c \"{script}\"")
            
            # Bắt lỗi thực tế từ chuỗi trả về
            if "error" in out.lower() or "denied" in out.lower():
                from src.utils.logger import logger
                logger.error(f"[{self.device_id}] Lỗi khi chặn mạng: {out}")
                return False
                
            return True
        except ADBCommandError:
            return False

    def enable_internet(self) -> bool:
        """
        Mở lại mạng. Đảm bảo thông mạng 100% bằng cách Flush Chain.
        """
        try:
            # Bước 1 (Quan trọng nhất): iptables -F FARM_BLOCK làm sạch các rule DROP.
            # Ngay khoảnh khắc dòng này chạy xong, mạng sẽ LẬP TỨC có lại!
            script = (
                "iptables -F FARM_BLOCK; "
                "iptables -D OUTPUT -j FARM_BLOCK 2>/dev/null; "
                "iptables -D OUTPUT -j FARM_BLOCK 2>/dev/null; "
                "iptables -D OUTPUT -j FARM_BLOCK 2>/dev/null; " # Xóa dọn dẹp thêm vài lần
                "iptables -X FARM_BLOCK 2>/dev/null"
            )
            out = self._shell(f"su -c \"{script}\"")
            
            if "error" in out.lower() or "denied" in out.lower():
                from src.utils.logger import logger
                logger.error(f"[{self.device_id}] Lỗi khi mở mạng: {out}")
                return False
                
            return True
        except ADBCommandError:
            return False

    def take_screenshot(self, output_dir: str) -> Optional[str]:
        """
        Captures a device screenshot and transfers it directly to the computer.
        
        This method bypasses temporary storage on the mobile device by using 
        adbutils to read the framebuffer directly, ensuring high performance.
        
        Args:
            output_dir (str): The local directory path where the image will be saved.
            
        Returns:
            Optional[str]: The absolute local file path of the saved screenshot, 
                          or None if the capture fails.
        """
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_device_id = self.device_id.replace(":", "_").replace(".", "_")
            file_name = f"{safe_device_id}_{timestamp}.png"
            local_path = os.path.join(output_dir, file_name)

            image = self.device.screenshot()
            
            image.save(local_path)

            return local_path
        except Exception as e:
            from src.utils.logger import logger
            logger.error(f"[{self.device_id}] Error capturing direct screenshot: {e}")
            return None