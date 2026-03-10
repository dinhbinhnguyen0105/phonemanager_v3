# src/views/pages/home/user_table.py
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import Signal


class UserTable(QTableView):
    users_selected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
