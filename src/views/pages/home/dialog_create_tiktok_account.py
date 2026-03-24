# src/views/pages/home/dialog_create_tiktok_account.py
from PySide6.QtWidgets import QDialog
from src.ui.dialog_tt_create_ui import Ui_dialog__tt_create
from src.entities import Social

class Dialog_CreateTikTokAccount(QDialog, Ui_dialog__tt_create):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.ttcreatedialog__cookie_container.hide()

    def get_data(self) -> Social:
        return Social(
            social_id=self.ttcreatedialog__uid_lineedit.text().strip(),
            social_name=self.ttcreatedialog__username_lineedit.text().strip(),
            social_password=self.ttcreatedialog__password_lineedit.text().strip(),
            social_status=1,
            social_group=0,
            social_platform="tiktok"
        )