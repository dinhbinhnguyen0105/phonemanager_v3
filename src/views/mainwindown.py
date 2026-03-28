# src/views/mainwindow.py
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QLabel, QListView, QListWidgetItem, QListWidget

from src.worker.job_worker import JobExecutionWorker
from src.controllers._manager_controllers import ControllerManager

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
        """
        Initializes the application status bar with real-time system metrics.

        This method configures the visual style of the status bar and adds labels 
        to track active jobs, connected devices, and proxy availability. It also 
        includes a permanent action button for queue management and starts a 
        QTimer to refresh these statistics every 1.5 seconds.
        """
        self.statusBar().setStyleSheet("QStatusBar { background-color: #1e1e1e; border-top: 1px solid #333333; }")

        self.status_jobs_label = QLabel("⚡ Jobs: 0 Pending | 0 Running")
        self.status_jobs_label.setStyleSheet("color: #e67e22; font-weight: bold; padding: 0 15px; border-right: 1px solid #555;") 
        self.statusBar().addWidget(self.status_jobs_label)

        self.status_devices_label = QLabel("📱 Devices: 0 Online")
        self.status_devices_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 0 15px; border-right: 1px solid #555;") 
        self.statusBar().addWidget(self.status_devices_label)

        self.status_proxies_label = QLabel("🌐 Proxies: 0 Available | 0 In Use")
        self.status_proxies_label.setStyleSheet("color: #2ecc71; font-weight: bold; padding: 0 15px;") 
        self.statusBar().addWidget(self.status_proxies_label)
        
        self.btn_clear_jobs = QPushButton("🗑 Clear Pending Jobs")
        self.btn_clear_jobs.setStyleSheet("color: #e74c3c; font-weight: bold; border: none; padding: 0px 10px;")
        self.statusBar().addPermanentWidget(self.btn_clear_jobs)
        self.btn_clear_jobs.clicked.connect(self._on_clear_jobs_clicked)

        self.status_update_timer = QTimer(self)
        self.status_update_timer.timeout.connect(self._update_statusbar_stats)
        self.status_update_timer.start(1500)
    
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
    def _update_statusbar_stats(self):
        """
        Periodically fetches real-time metrics from Redis to update the Status Bar labels.

        This method queries the Redis facade to retrieve the current counts of 
        pending and active jobs, online and working devices, and available 
        versus in-use proxies. It updates the UI labels to provide the user 
        with an immediate overview of the system state. Exceptions are 
        silently ignored to handle transient Redis connection issues without 
        crashing the UI thread.
        """
        try:
            redis_facade = self.controllers.service_manager.redis

            pending_count = redis_facade.jobs.get_pending_count()
            active_jobs_count = len(redis_facade.jobs.get_all_active_jobs())
            self.status_jobs_label.setText(f"⚡ Jobs: {pending_count} Pending | {active_jobs_count} Running")

            online_count = len(redis_facade.devices.get_all_online())
            self.status_devices_label.setText(f"📱 Devices: {online_count} Online | {active_jobs_count} Working")

            available_count = len(redis_facade.proxies.get_all_available())
            working_proxies_count = len(redis_facade.proxies.hget_all("working"))
            self.status_proxies_label.setText(f"🌐 Proxies: {available_count} Available | {working_proxies_count} In Use")

        except Exception:
            pass
                
    def closeEvent(self, event):
        """
        Handles the application cleanup process when the main window is closed.

        This method ensures a graceful shutdown by stopping all active timers 
        (UI scaling and status updates) and terminating background job workers. 
        It also triggers a global stop command for all controllers to release 
        system resources before accepting the close event.

        Args:
            event (QCloseEvent): The window close event.
        """
        if hasattr(self, 'scaler_timer'):
            self.scaler_timer.stop()
            
        if hasattr(self, 'status_update_timer'):
            self.status_update_timer.stop()
            
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