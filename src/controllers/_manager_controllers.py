# src/controllers/_manager_controllers.py
from typing import TYPE_CHECKING
from src.controllers.device_controller import DeviceController
from src.controllers.user_controller import UserController
from src.controllers.proxy_controller import ProxyController
from src.controllers.social_controller import SocialController
from src.controllers.external_data_controller import ExternalDataController

if TYPE_CHECKING:
    from src.services._manager_services import ServiceManager

class ControllerManager:
    def __init__(self, service_manager: "ServiceManager"):
        self.service_manager = service_manager
        self.device_controller = DeviceController(service_manager.devices)
        self.user_controller = UserController(service_manager.users)
        self.proxy_controller = ProxyController(service_manager.proxies)
        self.social_controller = SocialController(service_manager.socials)
        self.external_db_controller = ExternalDataController(service_manager.external_db)
    
    def start_background_tasks(self):
        self.device_controller.start_device_scan()
    
    def stop_all(self):
        self.device_controller.stop_device_scan()