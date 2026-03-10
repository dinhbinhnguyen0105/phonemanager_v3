# src/views/mainwindow.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from src.controllers._manager_controllers import ControllerManager

from src.views.sidebar.sidebar import Sidebar
from src.views.pages.home.home import HomePage

class MainWindow(QMainWindow):
    def __init__(self, controllers: ControllerManager):
        super().__init__()
        self.setWindowTitle("PhoneFarm Management")
        self.resize(1280, 720)
        
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
        self.stacked_widget.addWidget(self.home_page)
        self.page_mapping = {
            "devices": 0,
            # "users": 1, 
            # "fb_accounts": 2...
        }

        self.sidebar.menu_clicked.connect(self.switch_page)

    def switch_page(self, menu_name: str):
        page_index = self.page_mapping.get(menu_name)
        if page_index is not None:
            self.stacked_widget.setCurrentIndex(page_index)
            
    def closeEvent(self, event):
        self.controllers.stop_all()
        event.accept()