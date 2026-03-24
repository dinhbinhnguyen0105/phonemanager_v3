# src/views/pages/home/dialog_create_new_user.py
from PySide6.QtWidgets import QDialog
from src.ui.dialog_user_create_ui import Ui_dialog__create_new_user

class Dialog_CreateNewUser(QDialog, Ui_dialog__create_new_user):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
    def get_username(self) -> str:
        return self.newuser__dialog_username_qlineedit.text().strip()