# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_devices.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QVBoxLayout,
    QWidget)

class Ui_page__devices(object):
    def setupUi(self, page__devices):
        if not page__devices.objectName():
            page__devices.setObjectName(u"page__devices")
        page__devices.resize(1013, 692)
        self.gridLayout = QGridLayout(page__devices)
        self.gridLayout.setObjectName(u"gridLayout")
        self.page__devices_layout = QGridLayout()
        self.page__devices_layout.setObjectName(u"page__devices_layout")
        self.page__devices_layout.setContentsMargins(4, 4, 4, 4)
        self.devices__fbaccount_table = QTableView(page__devices)
        self.devices__fbaccount_table.setObjectName(u"devices__fbaccount_table")

        self.page__devices_layout.addWidget(self.devices__fbaccount_table, 1, 0, 1, 1)

        self.devices_adb_layout = QVBoxLayout()
        self.devices_adb_layout.setObjectName(u"devices_adb_layout")
        self.devices__adb_command_lineedit = QLineEdit(page__devices)
        self.devices__adb_command_lineedit.setObjectName(u"devices__adb_command_lineedit")

        self.devices_adb_layout.addWidget(self.devices__adb_command_lineedit)

        self.devices__logs = QListWidget(page__devices)
        self.devices__logs.setObjectName(u"devices__logs")

        self.devices_adb_layout.addWidget(self.devices__logs)


        self.page__devices_layout.addLayout(self.devices_adb_layout, 1, 2, 1, 1)

        self.devices__ttaccount_table = QTableView(page__devices)
        self.devices__ttaccount_table.setObjectName(u"devices__ttaccount_table")

        self.page__devices_layout.addWidget(self.devices__ttaccount_table, 1, 1, 1, 1)

        self.devices__devices_layout = QVBoxLayout()
        self.devices__devices_layout.setObjectName(u"devices__devices_layout")
        self.devices__devices_table = QTableView(page__devices)
        self.devices__devices_table.setObjectName(u"devices__devices_table")

        self.devices__devices_layout.addWidget(self.devices__devices_table)

        self.devices__devices_actions_layout = QHBoxLayout()
        self.devices__devices_actions_layout.setObjectName(u"devices__devices_actions_layout")
        self.devices__devices_actions_refresh_btn = QPushButton(page__devices)
        self.devices__devices_actions_refresh_btn.setObjectName(u"devices__devices_actions_refresh_btn")

        self.devices__devices_actions_layout.addWidget(self.devices__devices_actions_refresh_btn)

        self.devices__devices_actions_checkroot_btn = QPushButton(page__devices)
        self.devices__devices_actions_checkroot_btn.setObjectName(u"devices__devices_actions_checkroot_btn")

        self.devices__devices_actions_layout.addWidget(self.devices__devices_actions_checkroot_btn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.devices__devices_actions_layout.addItem(self.horizontalSpacer)


        self.devices__devices_layout.addLayout(self.devices__devices_actions_layout)


        self.page__devices_layout.addLayout(self.devices__devices_layout, 0, 0, 1, 1)

        self.devices__user_table = QTableView(page__devices)
        self.devices__user_table.setObjectName(u"devices__user_table")

        self.page__devices_layout.addWidget(self.devices__user_table, 0, 1, 1, 2)


        self.gridLayout.addLayout(self.page__devices_layout, 0, 0, 1, 1)


        self.retranslateUi(page__devices)

        QMetaObject.connectSlotsByName(page__devices)
    # setupUi

    def retranslateUi(self, page__devices):
        page__devices.setWindowTitle(QCoreApplication.translate("page__devices", u"Form", None))
        self.devices__adb_command_lineedit.setPlaceholderText(QCoreApplication.translate("page__devices", u"ADB command", None))
        self.devices__devices_actions_refresh_btn.setText(QCoreApplication.translate("page__devices", u"Refresh", None))
        self.devices__devices_actions_checkroot_btn.setText(QCoreApplication.translate("page__devices", u"Check root", None))
    # retranslateUi

