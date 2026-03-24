# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_facebooks.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_page__facebooks(object):
    def setupUi(self, page__facebooks):
        if not page__facebooks.objectName():
            page__facebooks.setObjectName(u"page__facebooks")
        page__facebooks.resize(1000, 673)
        self.gridLayout_2 = QGridLayout(page__facebooks)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(8, 8, 8, 8)
        self.page__facebooks_layout = QGridLayout()
        self.page__facebooks_layout.setSpacing(0)
        self.page__facebooks_layout.setObjectName(u"page__facebooks_layout")
        self.page__facebooks_layout.setContentsMargins(0, -1, 12, 12)
        self.page__facebooks_search = QGroupBox(page__facebooks)
        self.page__facebooks_search.setObjectName(u"page__facebooks_search")
        self.page__facebooks_search.setMinimumSize(QSize(0, 0))
        self.gridLayout_3 = QGridLayout(self.page__facebooks_search)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.page__facebooks_search_layout = QGridLayout()
        self.page__facebooks_search_layout.setObjectName(u"page__facebooks_search_layout")
        self.page__facebooks_search_uid_input = QLineEdit(self.page__facebooks_search)
        self.page__facebooks_search_uid_input.setObjectName(u"page__facebooks_search_uid_input")

        self.page__facebooks_search_layout.addWidget(self.page__facebooks_search_uid_input, 0, 0, 1, 1)

        self.page__facebooks_search_username_input = QLineEdit(self.page__facebooks_search)
        self.page__facebooks_search_username_input.setObjectName(u"page__facebooks_search_username_input")

        self.page__facebooks_search_layout.addWidget(self.page__facebooks_search_username_input, 0, 1, 1, 1)

        self.page__facebooks_search_group_input = QLineEdit(self.page__facebooks_search)
        self.page__facebooks_search_group_input.setObjectName(u"page__facebooks_search_group_input")

        self.page__facebooks_search_layout.addWidget(self.page__facebooks_search_group_input, 1, 0, 1, 1)


        self.gridLayout_3.addLayout(self.page__facebooks_search_layout, 0, 0, 1, 1)


        self.page__facebooks_layout.addWidget(self.page__facebooks_search, 0, 0, 1, 2)

        self.page__facebooks_facebook_table = QTableView(page__facebooks)
        self.page__facebooks_facebook_table.setObjectName(u"page__facebooks_facebook_table")

        self.page__facebooks_layout.addWidget(self.page__facebooks_facebook_table, 1, 0, 6, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.page__facebooks_info_container = QGroupBox(page__facebooks)
        self.page__facebooks_info_container.setObjectName(u"page__facebooks_info_container")
        self.verticalLayout_2 = QVBoxLayout(self.page__facebooks_info_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.page__facebooks_info_layout = QFormLayout()
        self.page__facebooks_info_layout.setObjectName(u"page__facebooks_info_layout")
        self.page__facebooks_info_layout.setContentsMargins(-1, -1, 0, 0)
        self.page__facebooks_info__deviceudid_label = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__deviceudid_label.setObjectName(u"page__facebooks_info__deviceudid_label")

        self.page__facebooks_info_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.page__facebooks_info__deviceudid_label)

        self.page__facebooks_info__deviceudid_info = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__deviceudid_info.setObjectName(u"page__facebooks_info__deviceudid_info")

        self.page__facebooks_info_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.page__facebooks_info__deviceudid_info)

        self.page__facebooks_info__devicestatus_label = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__devicestatus_label.setObjectName(u"page__facebooks_info__devicestatus_label")

        self.page__facebooks_info_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.page__facebooks_info__devicestatus_label)

        self.page__facebooks_info__devicestatus_info = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__devicestatus_info.setObjectName(u"page__facebooks_info__devicestatus_info")

        self.page__facebooks_info_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.page__facebooks_info__devicestatus_info)

        self.page__facebooks_info__userid_label = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__userid_label.setObjectName(u"page__facebooks_info__userid_label")

        self.page__facebooks_info_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.page__facebooks_info__userid_label)

        self.page__facebooks_info__userid_info = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__userid_info.setObjectName(u"page__facebooks_info__userid_info")

        self.page__facebooks_info_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.page__facebooks_info__userid_info)

        self.page__facebooks_info__userstatus_label = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__userstatus_label.setObjectName(u"page__facebooks_info__userstatus_label")

        self.page__facebooks_info_layout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.page__facebooks_info__userstatus_label)

        self.page__facebooks_info__userstatus_info = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__userstatus_info.setObjectName(u"page__facebooks_info__userstatus_info")

        self.page__facebooks_info_layout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.page__facebooks_info__userstatus_info)

        self.page__facebooks_info__username_label = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__username_label.setObjectName(u"page__facebooks_info__username_label")

        self.page__facebooks_info_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.page__facebooks_info__username_label)

        self.page__facebooks_info__username_info = QLabel(self.page__facebooks_info_container)
        self.page__facebooks_info__username_info.setObjectName(u"page__facebooks_info__username_info")

        self.page__facebooks_info_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.page__facebooks_info__username_info)


        self.verticalLayout_2.addLayout(self.page__facebooks_info_layout)


        self.verticalLayout.addWidget(self.page__facebooks_info_container)

        self.page__facebooks_actions_scrollarea = QScrollArea(page__facebooks)
        self.page__facebooks_actions_scrollarea.setObjectName(u"page__facebooks_actions_scrollarea")
        self.page__facebooks_actions_scrollarea.setWidgetResizable(True)
        self.page__facebook_actions_container = QWidget()
        self.page__facebook_actions_container.setObjectName(u"page__facebook_actions_container")
        self.page__facebook_actions_container.setGeometry(QRect(0, 0, 302, 440))
        self.horizontalLayout = QHBoxLayout(self.page__facebook_actions_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.page__facebook_actions_layout = QVBoxLayout()
        self.page__facebook_actions_layout.setObjectName(u"page__facebook_actions_layout")
        self.page__facebook_actions_add_btn = QPushButton(self.page__facebook_actions_container)
        self.page__facebook_actions_add_btn.setObjectName(u"page__facebook_actions_add_btn")

        self.page__facebook_actions_layout.addWidget(self.page__facebook_actions_add_btn)


        self.horizontalLayout.addLayout(self.page__facebook_actions_layout)

        self.page__facebooks_actions_scrollarea.setWidget(self.page__facebook_actions_container)

        self.verticalLayout.addWidget(self.page__facebooks_actions_scrollarea)

        self.page__facebooks_buttons = QGroupBox(page__facebooks)
        self.page__facebooks_buttons.setObjectName(u"page__facebooks_buttons")
        self.horizontalLayout_3 = QHBoxLayout(self.page__facebooks_buttons)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.page__facebooks_buttons_layout = QHBoxLayout()
        self.page__facebooks_buttons_layout.setObjectName(u"page__facebooks_buttons_layout")
        self.page__facebooks_buttons_save_btn = QPushButton(self.page__facebooks_buttons)
        self.page__facebooks_buttons_save_btn.setObjectName(u"page__facebooks_buttons_save_btn")

        self.page__facebooks_buttons_layout.addWidget(self.page__facebooks_buttons_save_btn)

        self.page__facebooks_buttons_add_btn = QPushButton(self.page__facebooks_buttons)
        self.page__facebooks_buttons_add_btn.setObjectName(u"page__facebooks_buttons_add_btn")

        self.page__facebooks_buttons_layout.addWidget(self.page__facebooks_buttons_add_btn)


        self.horizontalLayout_3.addLayout(self.page__facebooks_buttons_layout)


        self.verticalLayout.addWidget(self.page__facebooks_buttons)


        self.page__facebooks_layout.addLayout(self.verticalLayout, 0, 2, 7, 1)

        self.page__facebooks_actions_list = QListWidget(page__facebooks)
        self.page__facebooks_actions_list.setObjectName(u"page__facebooks_actions_list")

        self.page__facebooks_layout.addWidget(self.page__facebooks_actions_list, 1, 1, 6, 1)


        self.gridLayout_2.addLayout(self.page__facebooks_layout, 0, 0, 1, 1)


        self.retranslateUi(page__facebooks)

        QMetaObject.connectSlotsByName(page__facebooks)
    # setupUi

    def retranslateUi(self, page__facebooks):
        page__facebooks.setWindowTitle(QCoreApplication.translate("page__facebooks", u"Facebooks", None))
        self.page__facebooks_search.setTitle(QCoreApplication.translate("page__facebooks", u"Search", None))
        self.page__facebooks_search_uid_input.setPlaceholderText(QCoreApplication.translate("page__facebooks", u"UID", None))
        self.page__facebooks_search_username_input.setPlaceholderText(QCoreApplication.translate("page__facebooks", u"Username", None))
        self.page__facebooks_search_group_input.setPlaceholderText(QCoreApplication.translate("page__facebooks", u"Group", None))
        self.page__facebooks_info_container.setTitle(QCoreApplication.translate("page__facebooks", u"Info", None))
        self.page__facebooks_info__deviceudid_label.setText(QCoreApplication.translate("page__facebooks", u"Device ID (Serial):", None))
        self.page__facebooks_info__deviceudid_info.setText(QCoreApplication.translate("page__facebooks", u"---", None))
        self.page__facebooks_info__devicestatus_label.setText(QCoreApplication.translate("page__facebooks", u"Device Status", None))
        self.page__facebooks_info__devicestatus_info.setText(QCoreApplication.translate("page__facebooks", u"---", None))
        self.page__facebooks_info__userid_label.setText(QCoreApplication.translate("page__facebooks", u"User ID:", None))
        self.page__facebooks_info__userid_info.setText(QCoreApplication.translate("page__facebooks", u"---", None))
        self.page__facebooks_info__userstatus_label.setText(QCoreApplication.translate("page__facebooks", u"User's status", None))
        self.page__facebooks_info__userstatus_info.setText(QCoreApplication.translate("page__facebooks", u"---", None))
        self.page__facebooks_info__username_label.setText(QCoreApplication.translate("page__facebooks", u"User name", None))
        self.page__facebooks_info__username_info.setText(QCoreApplication.translate("page__facebooks", u"---", None))
        self.page__facebook_actions_add_btn.setText(QCoreApplication.translate("page__facebooks", u"Add action", None))
        self.page__facebooks_buttons.setTitle("")
        self.page__facebooks_buttons_save_btn.setText(QCoreApplication.translate("page__facebooks", u"Save", None))
        self.page__facebooks_buttons_add_btn.setText(QCoreApplication.translate("page__facebooks", u"Add to pending", None))
    # retranslateUi

