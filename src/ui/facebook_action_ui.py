# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'facebook_action.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_action(object):
    def setupUi(self, action):
        if not action.objectName():
            action.setObjectName(u"action")
        action.resize(557, 344)
        self.gridLayout_2 = QGridLayout(action)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.action__layout = QGridLayout()
        self.action__layout.setObjectName(u"action__layout")
        self.action__layout.setContentsMargins(-1, -1, 12, 12)
        self.action__delete_btn = QPushButton(action)
        self.action__delete_btn.setObjectName(u"action__delete_btn")

        self.action__layout.addWidget(self.action__delete_btn, 0, 1, 1, 1)

        self.action__actions_option = QComboBox(action)
        self.action__actions_option.addItem("")
        self.action__actions_option.setObjectName(u"action__actions_option")

        self.action__layout.addWidget(self.action__actions_option, 0, 0, 1, 1)

        self.action__content = QStackedWidget(action)
        self.action__content.setObjectName(u"action__content")
        self.action__content_list_marketplace_container = QWidget()
        self.action__content_list_marketplace_container.setObjectName(u"action__content_list_marketplace_container")
        self.verticalLayout_3 = QVBoxLayout(self.action__content_list_marketplace_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.action__content_list_marketplace_layout = QVBoxLayout()
        self.action__content_list_marketplace_layout.setSpacing(0)
        self.action__content_list_marketplace_layout.setObjectName(u"action__content_list_marketplace_layout")

        self.verticalLayout_3.addLayout(self.action__content_list_marketplace_layout)

        self.action__content.addWidget(self.action__content_list_marketplace_container)
        self.action__content_scroll_feed_container = QWidget()
        self.action__content_scroll_feed_container.setObjectName(u"action__content_scroll_feed_container")
        self.verticalLayout_2 = QVBoxLayout(self.action__content_scroll_feed_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.action__content_scroll_feed_layout = QVBoxLayout()
        self.action__content_scroll_feed_layout.setObjectName(u"action__content_scroll_feed_layout")

        self.verticalLayout_2.addLayout(self.action__content_scroll_feed_layout)

        self.action__content.addWidget(self.action__content_scroll_feed_container)
        self.action__content_interact_feed_container = QWidget()
        self.action__content_interact_feed_container.setObjectName(u"action__content_interact_feed_container")
        self.verticalLayout = QVBoxLayout(self.action__content_interact_feed_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.action__content_interact_feed_layout = QVBoxLayout()
        self.action__content_interact_feed_layout.setObjectName(u"action__content_interact_feed_layout")

        self.verticalLayout.addLayout(self.action__content_interact_feed_layout)

        self.action__content.addWidget(self.action__content_interact_feed_container)
        self.action__content_interact_target_container = QWidget()
        self.action__content_interact_target_container.setObjectName(u"action__content_interact_target_container")
        self.verticalLayout_5 = QVBoxLayout(self.action__content_interact_target_container)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.action__content_interact_target_layout = QVBoxLayout()
        self.action__content_interact_target_layout.setObjectName(u"action__content_interact_target_layout")

        self.verticalLayout_5.addLayout(self.action__content_interact_target_layout)

        self.action__content.addWidget(self.action__content_interact_target_container)
        self.action__content_post_group_container = QWidget()
        self.action__content_post_group_container.setObjectName(u"action__content_post_group_container")
        self.verticalLayout_6 = QVBoxLayout(self.action__content_post_group_container)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.action__content_post_group_layout = QVBoxLayout()
        self.action__content_post_group_layout.setObjectName(u"action__content_post_group_layout")

        self.verticalLayout_6.addLayout(self.action__content_post_group_layout)

        self.action__content.addWidget(self.action__content_post_group_container)

        self.action__layout.addWidget(self.action__content, 1, 0, 1, 1)


        self.gridLayout_2.addLayout(self.action__layout, 0, 0, 1, 1)


        self.retranslateUi(action)

        self.action__content.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(action)
    # setupUi

    def retranslateUi(self, action):
        action.setTitle(QCoreApplication.translate("action", u"Action", None))
        self.action__delete_btn.setText(QCoreApplication.translate("action", u"Delete", None))
        self.action__actions_option.setItemText(0, QCoreApplication.translate("action", u"--- Select Action ---", None))

    # retranslateUi

