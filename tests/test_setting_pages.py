# run_settings_test.py
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from PySide6.QtWidgets import QApplication


# Import các thành phần của hệ thống
from src.database.connection import DatabaseManager
from src.repositories._manager_repositories import RepositoryManager
from src.services._manager_services import ServiceManager
from src.drivers.redis._manager_redis import RedisStateFacade
from src.controllers._manager_controllers import ControllerManager
from src.views.pages.settings.settings import SettingsPage
from src.utils.logger import logger

def main():
    # 1. Khởi tạo ứng dụng Qt
    app = QApplication(sys.argv)

    try:
        # 2. Khởi tạo Database Manager
        # (Lưu ý: Nếu lớp DatabaseManager của bạn có hàm tạo bảng như create_tables() 
        # hay initialize(), hãy gọi nó ở đây để đảm bảo SQLite đã sẵn sàng)
        db_manager = DatabaseManager()
        db_manager.init_tables()
        logger.info("Database initialized successfully.")

        repo_manager = RepositoryManager(db_manager=db_manager)
        logger.info("Repositories initialized successfully.")

        redis_facade = RedisStateFacade()
        logger.info("Redis State Facade initialized successfully.")

        # 2. Khởi tạo Service Manager
        service_manager = ServiceManager(repo_manager=repo_manager, redis_facade=redis_facade)
        logger.info("Services initialized successfully.")
        # 3. Khởi tạo Controller Manager
        # (Lưu ý: Nếu ControllerManager của bạn yêu cầu truyền các Service vào __init__, 
        # bạn hãy khởi tạo các Service tương ứng ở đây trước)
        controllers = ControllerManager(service_manager=service_manager)
        logger.info("Controllers initialized successfully.")

        # 4. Khởi tạo giao diện SettingsPage
        settings_page = SettingsPage(controllers=controllers)
        
        # Bạn có thể gọi hàm setup_data() nếu muốn load dữ liệu ngay khi mở form
        # settings_page.setup_data()
        
        # Thiết lập kích thước cửa sổ và hiển thị
        settings_page.resize(910, 640) 
        settings_page.show()

        logger.info("SettingsPage is running...")

        # 5. Chạy vòng lặp sự kiện chính của PySide6
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Error starting application: {e}")

if __name__ == "__main__":
    main()