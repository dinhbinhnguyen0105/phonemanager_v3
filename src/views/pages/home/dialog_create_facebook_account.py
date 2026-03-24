# src/views/pages/home/dialog_create_facebook_account.py
from PySide6.QtWidgets import QDialog
from src.ui.dialog_fb_create_ui import Ui_dialog__fb_create 
from src.entities import Social

class Dialog_CreateFacebookAccount(QDialog, Ui_dialog__fb_create):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.fbcreatedialog__2fa_container.hide()
        self.fbcreatedialog__cookie_container.hide()

    def get_data(self) -> Social:
        group_text = self.fbcreatedialog__group_lineedit.text().strip()
        group_id = int(group_text) if group_text.isdigit() else 0

        return Social(
            social_id=self.fbcreatedialog__uid_lineedit.text().strip(),
            social_name=self.fbcreatedialog__username_lineedit.text().strip(),
            social_password=self.fbcreatedialog__password_lineedit.text().strip(),
            social_status=1,
            social_group=group_id,
            social_platform="facebook"            
        )