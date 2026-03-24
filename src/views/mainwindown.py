# src/views/mainwindow.py
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QLabel, QListView, QListWidgetItem, QListWidget

from src.controllers._manager_controllers import ControllerManager
from src.worker.job_worker import JobExecutionWorker
from src.views.sidebar.sidebar import Sidebar
from src.views.pages.home.home import HomePage
from src.views.pages.settings.settings import SettingsPage
from src.views.pages.facebook.facebook import FacebookPage

from src.utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self, controllers: ControllerManager):
        super().__init__()
        self.setWindowTitle("PhoneFarm Management")
        self.resize(1600, 600)
        
        self.controllers = controllers
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, stretch=1)
        
        self.home_page = HomePage(self.controllers)
        # Bắt signal message từ HomePage
        self.home_page.message.connect(self._on_log_message)
        self.stacked_widget.addWidget(self.home_page)

        self.facebook_page = FacebookPage(self.controllers)
        self.stacked_widget.addWidget(self.facebook_page)

        self.setting_page = SettingsPage(self.controllers)
        self.stacked_widget.addWidget(self.setting_page)
        
        self.log_list_widget = QListWidget()
        self.log_list_widget.setFixedWidth(350)
        self.log_list_widget.setWordWrap(True)
        self.log_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: Consolas, monospace;
                font-size: 11px;
                border-left: 1px solid #333333;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.log_list_widget)

        self.page_mapping = {
            "home": 0,
            "facebooks": 1,
            "settings": 2,
        }

        self.sidebar.menu_clicked.connect(self.switch_page)
        self.switch_page("facebooks")

        self._setup_statusbar()
        self._setup_global_workers()

    def switch_page(self, menu_name: str):
        page_index = self.page_mapping.get(menu_name)
        if page_index is not None:
            self.stacked_widget.setCurrentIndex(page_index)
            if hasattr(self.stacked_widget.currentWidget(), "refresh_data"):
                self.stacked_widget.currentWidget().refresh_data()  # type: ignore
    
    def _setup_statusbar(self):
        self.status_log_label = QLabel("🚀 System Ready")
        self.status_log_label.setStyleSheet("color: #0078D7; font-weight: bold; padding-left: 5px;") 
        
        self.statusBar().addWidget(self.status_log_label, 1) 
        
        self.btn_clear_jobs = QPushButton("🗑 Clear Pending Jobs")
        self.btn_clear_jobs.setStyleSheet("color: red; font-weight: bold; border: none; padding: 0px 10px;")
        self.statusBar().addPermanentWidget(self.btn_clear_jobs)
        self.btn_clear_jobs.clicked.connect(self._on_clear_jobs_clicked)
    
    def _on_clear_jobs_clicked(self):
        pending_count = self.controllers.service_manager.redis.jobs.get_pending_count()
        
        if pending_count == 0:
            QMessageBox.information(self, "Information", "There are no jobs in the queue.")
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Cleanup", 
            f"There are {pending_count} accounts in the queue waiting to run.\n"
            "Are you sure you want to CANCEL all these pending commands?\n"
            "(Active jobs currently running will not be affected)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controllers.service_manager.redis.jobs.clear_pending_queue()
            
            msg = f"Successfully canceled {pending_count} pending commands!"
            logger.info(msg)
            self.statusBar().showMessage(msg, 5000)
    
    def _setup_global_workers(self):
        self.job_workers = []
        self.MAX_WORKERS = 4
        
        self.scaler_timer = QTimer(self)
        self.scaler_timer.timeout.connect(self._auto_scale_workers)
        self.scaler_timer.start(2000)
        
        logger.info(f"Auto-Scaling Worker Mode enabled (Maximum {self.MAX_WORKERS} threads).")

    def _auto_scale_workers(self):
        self.job_workers = [w for w in self.job_workers if w.isRunning()]

        pending_count = self.controllers.service_manager.redis.jobs.get_pending_count()
        current_workers = len(self.job_workers)
        
        if pending_count > 0 and current_workers < self.MAX_WORKERS:
            slots_available = self.MAX_WORKERS - current_workers
            workers_to_spawn = min(pending_count, slots_available)
            
            for _ in range(workers_to_spawn):
                worker = JobExecutionWorker(self.controllers)
                worker.request_update_device.connect(self._on_worker_update_device)
                worker.request_scrcpy.connect(self._on_worker_request_scrcpy)
                worker.message.connect(self._on_log_message)
                
                self.job_workers.append(worker)
                worker.start()
                
    def closeEvent(self, event):
        if hasattr(self, 'scaler_timer'):
            self.scaler_timer.stop()
            
        if hasattr(self, 'job_workers'):
            for worker in self.job_workers:
                worker.stop()
                
        self.controllers.stop_all()
        event.accept()
    
    def _on_worker_update_device(self, device):
        self.controllers.device_controller.update(device)
    
    def _on_worker_request_scrcpy(self, device):
        self.controllers.device_controller.launch_scrcpy_for_job(device, self.MAX_WORKERS)
    
    def _on_log_message(self, log_message):
        logger.info(log_message)
        self.log_list_widget.addItem(log_message)
        while self.log_list_widget.count() > 50:
            self.log_list_widget.takeItem(0)
        self.log_list_widget.scrollToBottom()