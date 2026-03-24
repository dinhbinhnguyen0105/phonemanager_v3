# src/drivers/proxy/redsocks_driver.py
import os
import sys
import time
import base64
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.logger import logger
from src.drivers.adb.adb_controller import ADBController
from src.drivers.redsocks.base64config import BIN_V7, BIN_V8

class RedsocksDriver:
    """
    Manages Android proxy settings using Redsocks2 and IPTables.
    Redirects device TCP traffic through a specified proxy server.
    Requires Root access.
    """

    def __init__(self, driver_id:str):
        self.adb = ADBController(driver_id)
        self.driver_id = driver_id
        self.remote_bin = "/data/local/tmp/redsocks2"
        self.remote_cfg = "/data/local/tmp/redsocks2.conf"

    def _get_architecture(self) -> str:
        """Detects device CPU architecture to deploy the correct binary."""
        abi = self.adb._shell("getprop ro.product.cpu.abi").strip()
        return "v8" if "arm64" in abi else "v7"

    def _deploy(self):
        """Decodes and pushes the Redsocks2 binary to the device."""
        arch = self._get_architecture()
        bin_data = BIN_V8 if arch == "v8" else BIN_V7

        local_temp = f"rs_temp_{self.driver_id}"
        try:
            with open(local_temp, "wb") as f:
                f.write(base64.b64decode(bin_data.strip()))
            
            # Sử dụng api sync.push của adbutils để truyền file
            self.adb.device.sync.push(local_temp, self.remote_bin)
            self.adb._shell(f"su -c 'chmod 755 {self.remote_bin}'")
        finally:
            if os.path.exists(local_temp):
                os.remove(local_temp)

    def _setup_iptables(self, proxy_ip: str):
        """Configures firewall rules to transparently redirect TCP traffic."""
        cmds = [
            "iptables -t nat -F OUTPUT",
            "iptables -t nat -A OUTPUT -d 127.0.0.0/8 -j RETURN",
            f"iptables -t nat -A OUTPUT -d {proxy_ip} -j RETURN",
            "iptables -t nat -A OUTPUT -p udp --dport 53 -j RETURN",  # Allow DNS bypass
            "iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-ports 12345",
        ]
        for c in cmds:
            self.adb._shell(f"su -c '{c}'")

    def set_proxy(
        self,
        ip: str,
        port: int,
        username: str = "",
        password: str = "",
        ptype="http-connect",
    ):
        """Creates config, starts Redsocks2, and enables traffic redirection."""
        self._deploy()
        
        # Sanitize IP: remove protocol prefixes and paths
        clean_ip = ip.replace("http://", "").replace("https://", "").split("/")[0]

        valid_protocols = ["http-connect", "http-relay", "socks4", "socks5"]
        if ptype not in valid_protocols:
            ptype = "http-connect"

        # Prepare Authentication Config
        auth_config = ""
        if username and password:
            auth_config = f'login = "{username}";\npassword = "{password}";\n'

        config_content = (
            "base {\n"
            "log_debug = off;\n"
            "log_info = on;\n"
            "daemon = on;\n"
            "redirector = iptables;\n"
            "}\n"
            "redsocks {\n"
            "local_ip = 127.0.0.1;\n"
            "local_port = 12345;\n"
            f"ip = {clean_ip};\n"
            f"port = {port};\n"
            f"type = {ptype};\n"
            f"{auth_config}"
            "}\n"
        )

        local_cfg = f"temp_{self.driver_id}.conf"
        try:
            with open(local_cfg, "w", newline="\n") as f:
                f.write(config_content)
                
            self.adb.device.sync.push(local_cfg, self.remote_cfg)
            
            try:
                self.adb._shell("su -c 'killall -9 redsocks2'")
            except Exception:
                pass
                
            time.sleep(0.5)
            self.adb._shell(f"su -c '{self.remote_bin} -c {self.remote_cfg}'")
            self._setup_iptables(clean_ip)
        finally:
            if os.path.exists(local_cfg):
                os.remove(local_cfg)

    def is_running(self) -> bool:
        """Checks if the Redsocks2 process is currently running on the device."""
        pid = self.adb._shell("su -c 'pidof redsocks2'").strip()
        return pid.isdigit()

    def verify_proxy(self) -> str:
        """Verifies the public IP address via proxy using IPv4."""
        try:
            res = self.adb._shell("su -c 'curl -4 -s -m 60 https://api.ipify.org'").strip()
            logger.debug(res)
            return res
        except Exception:
            return ""

    def disable(self):
        """Flushes IPTables and terminates the proxy process."""
        try:
            self.adb._shell("su -c 'iptables -t nat -F'")
            self.adb._shell("su -c 'killall -9 redsocks2'")
        except Exception:
            pass

    def enable(
        self,
        ip: str,
        port: int,
        username: str = "",
        password: str = "",
        ptype="http-connect",
    ) -> str:
        """
        Main execution flow to establish a proxy connection.
        Disables IPv6 to prevent IP leakage.
        """
        auth_info = f" (Auth: {username})" if username else ""
    
        if not self.adb.check_root():
            logger.warning(f"❌ [{self.driver_id}] ROOT access is required!")
            return "NO_ROOT"
        self.disable()
        self.adb._shell("su -c 'echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6'")
        self.adb._shell("su -c 'echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6'")

        self.set_proxy(ip, port, username, password, ptype)

        success = False
        for _ in range(10):
            if self.is_running():
                success = True
                break
            time.sleep(1)

        if not success:
            logger.error(f"❌ [{self.driver_id}] Redsocks2 failed to start!")
            return "START_FAILED"
        for _ in range(3):
            final_ip = self.verify_proxy()
            if final_ip and len(final_ip.split(".")) == 4:
                return final_ip
            time.sleep(3)

        logger.warning(
            f"⚠️ [{self.driver_id}] Proxy established but no internet access detected."
        )
        return "NO_INTERNET"
