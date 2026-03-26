# src/controllers/proxy_controller.py
import requests
import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse

from PySide6.QtCore import Signal


from src.entities import Proxy
from src.constants import ProxyType, ProxyStatus
from src.utils.logger import logger
from src.worker.generic_worker import GenericWorker
from src.services.proxy_service import ProxyService
from src.controllers.base_controller import BaseController


class ProxyController(BaseController[Proxy]):
    """
    Controller handling Proxy-related business operations.
    Inherits data_changed and error_occurred signals from BaseController.
    Inherits methods: get_all(), get_by_id(), update(), delete().
    """

    rotate_proxy_success = Signal(list, object)  # List[Device], Proxy
    rotate_proxy_failed = Signal(list, object, str)  # List[Device], Proxy, error_msg

    def __init__(self, service: ProxyService):
        super().__init__(service)
        self.service = service
        self._rotate_queue = {}
        self._active_worker = {}

    def create(self, entity: Proxy) -> Optional[Proxy]:
        """Overrides the create method to validate data before persisting to the database."""
        try:
            self.service.validate_create(entity)
            success = self.service.create(entity)
            if success:
                self.data_changed.emit()
                logger.success(f"Proxy added successfully: {entity.host}:{entity.port}")
            return success
        except ValueError as ve:
            logger.error(f"Proxy data error: {ve}")
            self.error_occurred.emit(str(ve))
            return None
        except Exception as e:
            logger.error(f"System error while adding Proxy: {e}")
            self.error_occurred.emit(str(e))
            return None

    # ==========================================
    # WORKER RESOURCE LOGIC (VIA REDIS)
    # ==========================================

    def acquire_proxy(
        self, device_id: str, p_type: Optional[ProxyType] = None
    ) -> Optional[Proxy]:
        """
        Retrieves an idle Proxy from Redis. Pass p_type=None to acquire any available proxy type.
        """
        try:
            return self.service.acquire_proxy(device_id, p_type)
        except Exception as e:
            logger.error(f"Error acquiring proxy for {device_id}: {e}")
            self.error_occurred.emit(str(e))
            return None

    def release_proxy(self, uuid: str) -> None:
        """
        Returns the Proxy back to the Redis Pool.
        """
        try:
            self.service.release_proxy(uuid)
        except Exception as e:
            logger.error(f"Error releasing proxy {uuid}: {e}")
            self.error_occurred.emit(str(e))

    # ==========================================
    # ASYNC ROTATION LOGIC (UI)
    # ==========================================
    def rotate_proxy_async(self, devices: list, proxy: Proxy):
        """
        Triggers an asynchronous proxy rotation task via GenericWorker.

        This method initializes a background thread to handle the network request
        for rotating a proxy IP. It ensures the UI remains responsive and avoids
        database conflicts by only passing primitive data to the worker.

        Args:
            devices (list): List of device objects affected by this proxy.
            proxy (Proxy): The proxy entity to be rotated.
        """
        task_name = f"rotate_{proxy.uuid}_{id(devices)}"
        self._rotate_queue[task_name] = (devices, proxy)

        worker = GenericWorker(
            task_name=task_name,
            target_func=self._fetch_new_proxy_ip,
            rotate_url=proxy.rotate_url,
            proxy_type=proxy.proxy_type,
        )
        self._active_worker[task_name] = worker

        worker.success.connect(self._on_rotate_worker_success)
        worker.error.connect(self._on_rotate_worker_error)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(lambda t=task_name: self._active_worker.pop(t, None))

        worker.start()

    def _on_rotate_worker_success(self, task_name: str, result: Tuple[bool, str]):
        """
        Handles successful worker completion for proxy rotation in the MAIN THREAD.

        Updates the database and emits success signals once the background thread
        retrieves a valid new proxy configuration.

        Args:
            task_name (str): Unique identifier for the completed task.
            result (Tuple[bool, str]): A tuple containing success status and the result message.
        """
        is_success, message = result
        devices, proxy = self._rotate_queue.pop(task_name, ([], None))

        if is_success and proxy:
            try:
                parts = message.split(":")
                proxy.host = parts[0]
                proxy.port = int(parts[1])
                self.update(proxy)

                logger.debug(
                    f"Proxy updated successfully to: {proxy.host}:{proxy.port}"
                )
                self.rotate_proxy_success.emit(devices, proxy)
            except Exception as e:
                self.rotate_proxy_failed.emit(devices, proxy, f"DB Update failed: {e}")
        else:
            self.rotate_proxy_failed.emit(devices, proxy, message)

    def _on_rotate_worker_error(self, task_name: str, error_msg: str):
        """
        Handles unexpected worker errors during the rotation process.

        Args:
            task_name (str): Unique identifier for the failed task.
            error_msg (str): Description of the error encountered.
        """
        devices, proxy = self._rotate_queue.pop(task_name, ([], None))
        self.rotate_proxy_failed.emit(devices, proxy, error_msg)

    # ==========================================
    # ROTATION & UTILITY LOGIC
    # ==========================================

    def _fetch_new_proxy_ip(
        self, rotate_url: str, proxy_type: ProxyType
    ) -> Tuple[bool, str]:
        """
        Pure Network Function: Executes the API request to retrieve a new IP address.

        This function is designed to be thread-safe by avoiding direct access to
        the database or class instance variables (ORM/Self). It supports multiple
        proxy types including API and Local Box.

        Args:
            rotate_url (str): The endpoint used to trigger the IP rotation.
            proxy_type (ProxyType): The classification of the proxy (API, LOCAL, etc.).

        Returns:
            Tuple[bool, str]: (Success status, Result message or proxy string).
        """
        try:
            if not rotate_url:
                return False, "Proxy does not have a Rotation URL."
            if proxy_type == ProxyType.STATIC:
                return False, "Static proxies do not support rotation."

            headers = {}
            bypass_proxies = {"http": "", "https": ""}

            if proxy_type == ProxyType.LOCAL:
                headers["x-api-key"] = "NDB_SECRET_KEY_2026"
                response = requests.post(
                    rotate_url, headers=headers, timeout=300, proxies=bypass_proxies
                )
            else:
                response = requests.get(
                    rotate_url, headers=headers, timeout=300, proxies=bypass_proxies
                )

            response.raise_for_status()
            data = response.json()

            if proxy_type in [ProxyType.API, ProxyType.LOCAL]:
                if data.get("status") in [100, "success", 1]:
                    proxy_http = data.get("proxyhttp", "")
                    if proxy_http and isinstance(proxy_http, str) and ":" in proxy_http:
                        return True, proxy_http

                error_msg = data.get(
                    "message", "Unknown error from provider or Local Box."
                )
                return False, f"Rotation denied: {error_msg}"

            return (
                False,
                f"Rotation is not supported for proxy type '{proxy_type.value}'.",
            )

        except requests.exceptions.RequestException as e:
            return False, f"Network connection error: {str(e)}"
        except ValueError:
            return False, "Invalid JSON response from rotation API."
        except Exception as e:
            return False, f"Data processing error: {str(e)}"

    def _rotate_proxy(
        self, proxy_uuid: str, set_working: bool = True
    ) -> Tuple[bool, str]:
        """
        Synchronous proxy rotation.

        Used by Job Workers or synchronous logic to rotate a proxy and update its
        status in the database immediately.

        Args:
            proxy_uuid (str): UUID of the proxy to rotate.
            set_working (bool): If True, sets the proxy status to WORKING upon success.

        Returns:
            Tuple[bool, str]: (Success status, Resulting proxy address or error message).
        """
        try:
            proxy = (
                self.get_by_id(proxy_uuid)
                if isinstance(proxy_uuid, str)
                else proxy_uuid
            )
            if not proxy:
                return False, "Proxy not found in the system."

            is_success, result_msg = self._fetch_new_proxy_ip(
                proxy.rotate_url, proxy.proxy_type
            )

            if is_success:
                parts = result_msg.split(":")
                proxy.host = parts[0]
                proxy.port = int(parts[1])
                if set_working:
                    proxy.proxy_status = ProxyStatus.WORKING
                self.update(proxy)

                proxy_type_str = "API" if proxy.proxy_type == ProxyType.API else "Local"
                logger.success(
                    f"{proxy_type_str} Proxy rotated successfully: {proxy.host}:{proxy.port}"
                )
                return True, f"{proxy.host}:{proxy.port}"
            else:
                return False, result_msg

        except Exception as e:
            logger.error(f"System error during proxy rotation: {e}")
            return False, f"Database/System error: {str(e)}"

    @staticmethod
    def classify_proxy_type(rotate_url: str) -> ProxyType:
        """
        Determines the ProxyType based on the rotation URL structure.
        """
        if not rotate_url or not rotate_url.strip():
            return ProxyType.STATIC

        url = rotate_url.strip()

        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not hostname:
                return ProxyType.API

            if hostname.lower() == "localhost":
                return ProxyType.LOCAL

            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback:
                    return ProxyType.LOCAL
                else:
                    return ProxyType.API

            except ValueError:
                return ProxyType.API

        except Exception:
            return ProxyType.API
