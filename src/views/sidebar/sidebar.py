# src/views/sidebar/sidebar.py
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QEvent
from src.ui.sidebar_ui import Ui_sidebar

class Sidebar(QWidget, Ui_sidebar):
    menu_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.menus = {
            "products": self.sidebar__products_container,
            "home": self.sidebar__home_container,
            "users": self.sidebar__users_container,
            "fb_accounts": self.sidebar__fbaccount_container,
            "tt_accounts": self.sidebar__ttaccount_container,
            "settings": self.sidebar__setting_container
        }

        for menu_name, container in self.menus.items():
            container.installEventFilter(self)
            container.setProperty("menu_name", menu_name) 

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            menu_name = obj.property("menu_name")
            if menu_name:
                self.menu_clicked.emit(menu_name)
                self.highlight_menu(obj)
                return True
        return super().eventFilter(obj, event)

    def highlight_menu(self, clicked_obj):
        for container in self.menus.values():
            container.setStyleSheet("") 
        clicked_obj.setStyleSheet("background-color: #d3d3d3; border-radius: 5px;")