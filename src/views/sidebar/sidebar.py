# src/views/sidebar/sidebar.py
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QEvent, Qt
from PySide6.QtGui import QPixmap
from src.ui.sidebar_ui import Ui_sidebar

class Sidebar(QWidget, Ui_sidebar):
    menu_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.menus = {
            "products": self.sidebar__products_container,
            "home": self.sidebar__home_container,
            "devices": self.sidebar__devices_container,
            "users": self.sidebar__users_container,
            "facebooks": self.sidebar__fbaccount_container,
            "tt_accounts": self.sidebar__ttaccount_container,
            "settings": self.sidebar__setting_container
        }

        self.icons = {
            "products": (self.sidebar__products_icon, "src/assets/product.png"),
            "home": (self.sidebar__home_icon, "src/assets/home.png"),
            "devices": (self.sidebar__device_icon, "src/assets/device.png"),
            "users": (self.sidebar__users_icon, "src/assets/user.png"),
            "facebooks": (self.sidebar__fbaccount_icon, "src/assets/facebook.png"),
            "tt_accounts": (self.sidebar__ttaccount_icon, "src/assets/tiktok.png"),
            "settings": (self.sidebar__setting_icon, "src/assets/setting.png"),
        }

        self.labels = {
            "products": self.sidebar__products_label,
            "home": self.sidebar__home_label,
            "devices": self.sidebar__device_layout1, 
            "users": self.sidebar__users_label,
            "facebooks": self.sidebar__fbaccount_label,
            "tt_accounts": self.sidebar__ttaccount_label,
            "settings": self.sidebar__setting_label,
        }

        self._setup_icons()
        self._convert_labels_to_tooltips()
        self._apply_stylesheet()

        for menu_name, container in self.menus.items():
            container.installEventFilter(self)
            container.setProperty("menu_name", menu_name) 
            container.setProperty("selected", False)

    def _setup_icons(self):
        icon_size = 24  
        
        for menu_name, (icon_label, img_path) in self.icons.items():
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    icon_size, icon_size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setFixedSize(icon_size, icon_size)
                icon_label.setText("")

    def _convert_labels_to_tooltips(self):
        for menu_name, label_widget in self.labels.items():
            container = self.menus[menu_name]
            
            tooltip_text = label_widget.text()
            container.setToolTip(tooltip_text)
            
            label_widget.hide()
            label_widget.deleteLater()

    def _apply_stylesheet(self):
        style = """
        Sidebar {
            background-color: #f8f9fa;
            border-right: 1px solid #e0e0e0;
        }

        QWidget[menu_name] {
            background-color: transparent;
            border-radius: 8px;
            margin: 6px;
            padding: 8px; 
        }

        QWidget[menu_name]:hover {
            background-color: #e9ecef;
        }

        QWidget[selected="true"] {
            background-color: #e3f2fd;
            border: 1px solid #bbdefb;
        }
        
        QToolTip {
            background-color: #333333;
            color: white;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 4px;
            font-size: 12px;
        }
        """
        self.setStyleSheet(style)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            menu_name = obj.property("menu_name")
            if menu_name:
                self.menu_clicked.emit(menu_name)
                self.highlight_menu(obj)
                return True
        return super().eventFilter(obj, event)

    def highlight_menu(self, clicked_obj):
        for container in self.menus.values():
            container.setProperty("selected", False)
            container.style().unpolish(container)
            container.style().polish(container)
            
        clicked_obj.setProperty("selected", True)
        clicked_obj.style().unpolish(clicked_obj)
        clicked_obj.style().polish(clicked_obj)