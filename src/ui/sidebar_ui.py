# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sidebar.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_sidebar(object):
    def setupUi(self, sidebar):
        if not sidebar.objectName():
            sidebar.setObjectName(u"sidebar")
        sidebar.resize(829, 806)
        self.verticalLayout_2 = QVBoxLayout(sidebar)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.sidebar__products_container = QWidget(sidebar)
        self.sidebar__products_container.setObjectName(u"sidebar__products_container")
        self.horizontalLayout = QHBoxLayout(self.sidebar__products_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sidebar__products_layout = QHBoxLayout()
        self.sidebar__products_layout.setObjectName(u"sidebar__products_layout")
        self.sidebar__products_icon = QLabel(self.sidebar__products_container)
        self.sidebar__products_icon.setObjectName(u"sidebar__products_icon")

        self.sidebar__products_layout.addWidget(self.sidebar__products_icon)

        self.sidebar__products_label = QLabel(self.sidebar__products_container)
        self.sidebar__products_label.setObjectName(u"sidebar__products_label")

        self.sidebar__products_layout.addWidget(self.sidebar__products_label)


        self.horizontalLayout.addLayout(self.sidebar__products_layout)


        self.verticalLayout.addWidget(self.sidebar__products_container)

        self.sidebar__home_container = QWidget(sidebar)
        self.sidebar__home_container.setObjectName(u"sidebar__home_container")
        self.horizontalLayout_2 = QHBoxLayout(self.sidebar__home_container)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.sidebar__home_layout = QHBoxLayout()
        self.sidebar__home_layout.setObjectName(u"sidebar__home_layout")
        self.sidebar__home_icon = QLabel(self.sidebar__home_container)
        self.sidebar__home_icon.setObjectName(u"sidebar__home_icon")

        self.sidebar__home_layout.addWidget(self.sidebar__home_icon)

        self.sidebar__home_label = QLabel(self.sidebar__home_container)
        self.sidebar__home_label.setObjectName(u"sidebar__home_label")

        self.sidebar__home_layout.addWidget(self.sidebar__home_label)


        self.horizontalLayout_2.addLayout(self.sidebar__home_layout)


        self.verticalLayout.addWidget(self.sidebar__home_container)

        self.sidebar__devices_container = QWidget(sidebar)
        self.sidebar__devices_container.setObjectName(u"sidebar__devices_container")
        self.horizontalLayout_7 = QHBoxLayout(self.sidebar__devices_container)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.sidebar__device_layout = QHBoxLayout()
        self.sidebar__device_layout.setObjectName(u"sidebar__device_layout")
        self.sidebar__device_icon = QLabel(self.sidebar__devices_container)
        self.sidebar__device_icon.setObjectName(u"sidebar__device_icon")

        self.sidebar__device_layout.addWidget(self.sidebar__device_icon)

        self.sidebar__device_layout1 = QLabel(self.sidebar__devices_container)
        self.sidebar__device_layout1.setObjectName(u"sidebar__device_layout1")

        self.sidebar__device_layout.addWidget(self.sidebar__device_layout1)


        self.horizontalLayout_7.addLayout(self.sidebar__device_layout)


        self.verticalLayout.addWidget(self.sidebar__devices_container)

        self.sidebar__users_container = QWidget(sidebar)
        self.sidebar__users_container.setObjectName(u"sidebar__users_container")
        self.horizontalLayout_3 = QHBoxLayout(self.sidebar__users_container)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.sidebar__users_layout = QHBoxLayout()
        self.sidebar__users_layout.setObjectName(u"sidebar__users_layout")
        self.sidebar__users_icon = QLabel(self.sidebar__users_container)
        self.sidebar__users_icon.setObjectName(u"sidebar__users_icon")

        self.sidebar__users_layout.addWidget(self.sidebar__users_icon)

        self.sidebar__users_label = QLabel(self.sidebar__users_container)
        self.sidebar__users_label.setObjectName(u"sidebar__users_label")

        self.sidebar__users_layout.addWidget(self.sidebar__users_label)


        self.horizontalLayout_3.addLayout(self.sidebar__users_layout)


        self.verticalLayout.addWidget(self.sidebar__users_container)

        self.sidebar__fbaccount_container = QWidget(sidebar)
        self.sidebar__fbaccount_container.setObjectName(u"sidebar__fbaccount_container")
        self.horizontalLayout_4 = QHBoxLayout(self.sidebar__fbaccount_container)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.sidebar__fbaccount_layout = QHBoxLayout()
        self.sidebar__fbaccount_layout.setObjectName(u"sidebar__fbaccount_layout")
        self.sidebar__fbaccount_icon = QLabel(self.sidebar__fbaccount_container)
        self.sidebar__fbaccount_icon.setObjectName(u"sidebar__fbaccount_icon")

        self.sidebar__fbaccount_layout.addWidget(self.sidebar__fbaccount_icon)

        self.sidebar__fbaccount_label = QLabel(self.sidebar__fbaccount_container)
        self.sidebar__fbaccount_label.setObjectName(u"sidebar__fbaccount_label")

        self.sidebar__fbaccount_layout.addWidget(self.sidebar__fbaccount_label)


        self.horizontalLayout_4.addLayout(self.sidebar__fbaccount_layout)


        self.verticalLayout.addWidget(self.sidebar__fbaccount_container)

        self.sidebar__ttaccount_container = QWidget(sidebar)
        self.sidebar__ttaccount_container.setObjectName(u"sidebar__ttaccount_container")
        self.horizontalLayout_5 = QHBoxLayout(self.sidebar__ttaccount_container)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.sidebar__ttaccount_layout = QHBoxLayout()
        self.sidebar__ttaccount_layout.setObjectName(u"sidebar__ttaccount_layout")
        self.sidebar__ttaccount_icon = QLabel(self.sidebar__ttaccount_container)
        self.sidebar__ttaccount_icon.setObjectName(u"sidebar__ttaccount_icon")

        self.sidebar__ttaccount_layout.addWidget(self.sidebar__ttaccount_icon)

        self.sidebar__ttaccount_label = QLabel(self.sidebar__ttaccount_container)
        self.sidebar__ttaccount_label.setObjectName(u"sidebar__ttaccount_label")

        self.sidebar__ttaccount_layout.addWidget(self.sidebar__ttaccount_label)


        self.horizontalLayout_5.addLayout(self.sidebar__ttaccount_layout)


        self.verticalLayout.addWidget(self.sidebar__ttaccount_container)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.sidebar__setting_container = QWidget(sidebar)
        self.sidebar__setting_container.setObjectName(u"sidebar__setting_container")
        self.horizontalLayout_6 = QHBoxLayout(self.sidebar__setting_container)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.sidebar__setting_layout = QHBoxLayout()
        self.sidebar__setting_layout.setObjectName(u"sidebar__setting_layout")
        self.sidebar__setting_icon = QLabel(self.sidebar__setting_container)
        self.sidebar__setting_icon.setObjectName(u"sidebar__setting_icon")

        self.sidebar__setting_layout.addWidget(self.sidebar__setting_icon)

        self.sidebar__setting_label = QLabel(self.sidebar__setting_container)
        self.sidebar__setting_label.setObjectName(u"sidebar__setting_label")

        self.sidebar__setting_layout.addWidget(self.sidebar__setting_label)


        self.horizontalLayout_6.addLayout(self.sidebar__setting_layout)


        self.verticalLayout.addWidget(self.sidebar__setting_container)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(sidebar)

        QMetaObject.connectSlotsByName(sidebar)
    # setupUi

    def retranslateUi(self, sidebar):
        sidebar.setWindowTitle(QCoreApplication.translate("sidebar", u"Form", None))
        self.sidebar__products_icon.setText(QCoreApplication.translate("sidebar", u"product_icon", None))
        self.sidebar__products_label.setText(QCoreApplication.translate("sidebar", u"Products", None))
        self.sidebar__home_icon.setText(QCoreApplication.translate("sidebar", u"home_icon", None))
        self.sidebar__home_label.setText(QCoreApplication.translate("sidebar", u"Home", None))
        self.sidebar__device_icon.setText(QCoreApplication.translate("sidebar", u"device_icon", None))
        self.sidebar__device_layout1.setText(QCoreApplication.translate("sidebar", u"Devices", None))
        self.sidebar__users_icon.setText(QCoreApplication.translate("sidebar", u"user_icon", None))
        self.sidebar__users_label.setText(QCoreApplication.translate("sidebar", u"Users", None))
        self.sidebar__fbaccount_icon.setText(QCoreApplication.translate("sidebar", u"fb_icon", None))
        self.sidebar__fbaccount_label.setText(QCoreApplication.translate("sidebar", u"Facebook accounts", None))
        self.sidebar__ttaccount_icon.setText(QCoreApplication.translate("sidebar", u"tt_icon", None))
        self.sidebar__ttaccount_label.setText(QCoreApplication.translate("sidebar", u"Tiktok accounts", None))
        self.sidebar__setting_icon.setText(QCoreApplication.translate("sidebar", u"setting_icon", None))
        self.sidebar__setting_label.setText(QCoreApplication.translate("sidebar", u"Settings", None))
    # retranslateUi

