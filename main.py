# main.py
import sys
from PySide6.QtWidgets import QApplication

from src.repositories._manager_repositories import RepositoryManager
from src.drivers.redis._manager_redis import RedisStateFacade
from src.services._manager_services import ServiceManager
from src.controllers._manager_controllers import ControllerManager
from src.views.mainwindown import MainWindow

def main():
    app = QApplication(sys.argv)
    redis_facade = RedisStateFacade()
    repo_manager = RepositoryManager()
    service_manager = ServiceManager(repo_manager, redis_facade)
    service_manager.init_system()
    controller_manager = ControllerManager(service_manager)
    window = MainWindow(controller_manager)
    window.show()
    controller_manager.start_background_tasks()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()