# src/worker/job_env.py
import time
from typing import TYPE_CHECKING, Tuple, Optional

from src.drivers.adb.adb_controller import ADBController
from src.drivers.redsocks.redsocks_driver import RedsocksDriver
from src.constants import ProxyType
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager
    from src.entities import Device, User, Proxy


def setup_device_environment(
    controllers: "ControllerManager", 
    device: "Device", 
    user: "User", 
    proxy_type: Optional[ProxyType] = None
) -> Tuple[bool, Optional["Proxy"], str]:
    """
    Sets up a secure environment: Fetch Proxy -> Rotate Proxy -> Attach Proxy -> Switch User -> Unlock.
    Returns a Tuple: (Success status, Current Proxy object, Log message)
    """
    
    proxy = None
    try:

        adb = ADBController(device.device_id)
        switch_success = adb.switch_user(user.user_id)
        if not switch_success:
            teardown_device_environment(controllers, device, proxy)
            return False, None, f"Could not switch to user {user.user_id}."
        
        adb.enable_internet()
        adb.grand_apk_permission(user_id=user.user_id, package_name="com.facebook.katana")
        # tt


        # 1. RETRIEVE PROXY FROM REDIS POOL
        # Update: Utilizing acquire_proxy to comply with the distributed architecture
        proxy = controllers.proxy_controller.acquire_proxy(device.device_id, proxy_type)
        if not proxy:
            return False, None, "No available proxies in the Pool."
        
        # logger.debug(proxy)
            
        # 2. ROTATE PROXY (If Proxy type is API or LOCAL)
        if proxy.proxy_type in [ProxyType.API, ProxyType.LOCAL]:
            is_success, msg = controllers.proxy_controller._rotate_proxy(proxy.uuid)
            if not is_success:
                # If rotation fails, immediately release the proxy back to the Pool
                controllers.proxy_controller.release_proxy(proxy.uuid)
                return False, None, f"Proxy rotation error: {msg}"
            
            # Refresh proxy data after rotation
            proxy = controllers.proxy_controller.get_by_id(proxy.uuid) 

        if not proxy:
            return False, None, "Proxy data synchronization failed after rotation."

        # 3. APPLY PROXY TO DEVICE VIA REDSOCKS
        rs_driver = RedsocksDriver(device.device_id)
        # Run enable function synchronously (blocks until network is ready or an error occurs)
        rs_result = rs_driver.enable(
            ip=proxy.host,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
            ptype=proxy.proxy_type.value
        )
        
        if rs_result in ["START_FAILED", "NO_INTERNET"]: #"NO_ROOT", 
            # If network connection fails, call teardown to clean up the environment
            teardown_device_environment(controllers, device, proxy)
            return False, None, f"Failed to apply proxy to device: {rs_result}"

        # 4. UNLOCK SCREEN (Wake up -> Unlock -> Return to Home)
        adb._shell("input keyevent 224") # WAKEUP
        time.sleep(0.5)
        adb._shell("input keyevent 82")  # UNLOCK (Swipe/Menu)
        time.sleep(0.5)
        adb._shell("input keyevent 3")   # HOME

        return True, proxy, "Environment setup successful."

    except Exception as e:
        logger.error(f"Unknown error during setup for device {device.device_id}: {e}")
        if proxy:
            teardown_device_environment(controllers, device, proxy)
        return False, None, f"System error during setup: {str(e)}"


def teardown_device_environment(
    controllers: "ControllerManager", 
    device: "Device", 
    proxy: Optional["Proxy"]
) -> bool:
    """
    Cleans up the environment: Disable Internet -> Clear background RAM -> Release Proxy to Redis.
    """
    try:
        rs_driver = RedsocksDriver(device.device_id)
        rs_driver.disable()

        adb = ADBController(device.device_id)
        adb.disable_internet()
        adb._shell("am kill-all")
        if proxy:
            controllers.proxy_controller.release_proxy(proxy.uuid)
        return True
    except Exception as e:
        logger.error(f"Error during teardown for device {device.device_id}: {e}")
        return False