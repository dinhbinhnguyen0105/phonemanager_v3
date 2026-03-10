# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_tt_create.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QGroupBox, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_dialog__tt_create(object):
    def setupUi(self, dialog__tt_create):
        if not dialog__tt_create.objectName():
            dialog__tt_create.setObjectName(u"dialog__tt_create")
        dialog__tt_create.resize(381, 280)
        self.verticalLayout = QVBoxLayout(dialog__tt_create)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.ttcreatedialog__uid_container = QGroupBox(dialog__tt_create)
        self.ttcreatedialog__uid_container.setObjectName(u"ttcreatedialog__uid_container")
        self.gridLayout_uid = QGridLayout(self.ttcreatedialog__uid_container)
        self.gridLayout_uid.setSpacing(0)
        self.gridLayout_uid.setObjectName(u"gridLayout_uid")
        self.gridLayout_uid.setContentsMargins(0, 0, 0, 0)
        self.ttcreatedialog__uid_lineedit = QLineEdit(self.ttcreatedialog__uid_container)
        self.ttcreatedialog__uid_lineedit.setObjectName(u"ttcreatedialog__uid_lineedit")

        self.gridLayout_uid.addWidget(self.ttcreatedialog__uid_lineedit, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.ttcreatedialog__uid_container)

        self.ttcreatedialog__username_container = QGroupBox(dialog__tt_create)
        self.ttcreatedialog__username_container.setObjectName(u"ttcreatedialog__username_container")
        self.gridLayout_username = QGridLayout(self.ttcreatedialog__username_container)
        self.gridLayout_username.setSpacing(0)
        self.gridLayout_username.setObjectName(u"gridLayout_username")
        self.gridLayout_username.setContentsMargins(0, 0, 0, 0)
        self.ttcreatedialog__username_lineedit = QLineEdit(self.ttcreatedialog__username_container)
        self.ttcreatedialog__username_lineedit.setObjectName(u"ttcreatedialog__username_lineedit")

        self.gridLayout_username.addWidget(self.ttcreatedialog__username_lineedit, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.ttcreatedialog__username_container)

        self.ttcreatedialog__password_container = QGroupBox(dialog__tt_create)
        self.ttcreatedialog__password_container.setObjectName(u"ttcreatedialog__password_container")
        self.gridLayout_password = QGridLayout(self.ttcreatedialog__password_container)
        self.gridLayout_password.setSpacing(0)
        self.gridLayout_password.setObjectName(u"gridLayout_password")
        self.gridLayout_password.setContentsMargins(0, 0, 0, 0)
        self.ttcreatedialog__password_lineedit = QLineEdit(self.ttcreatedialog__password_container)
        self.ttcreatedialog__password_lineedit.setObjectName(u"ttcreatedialog__password_lineedit")

        self.gridLayout_password.addWidget(self.ttcreatedialog__password_lineedit, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.ttcreatedialog__password_container)

        self.ttcreatedialog__cookie_container = QGroupBox(dialog__tt_create)
        self.ttcreatedialog__cookie_container.setObjectName(u"ttcreatedialog__cookie_container")
        self.gridLayout_cookie = QGridLayout(self.ttcreatedialog__cookie_container)
        self.gridLayout_cookie.setSpacing(0)
        self.gridLayout_cookie.setObjectName(u"gridLayout_cookie")
        self.gridLayout_cookie.setContentsMargins(0, 0, 0, 0)
        self.ttcreatedialog__cookie_lineedit = QLineEdit(self.ttcreatedialog__cookie_container)
        self.ttcreatedialog__cookie_lineedit.setObjectName(u"ttcreatedialog__cookie_lineedit")

        self.gridLayout_cookie.addWidget(self.ttcreatedialog__cookie_lineedit, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.ttcreatedialog__cookie_container)

        self.buttonBox = QDialogButtonBox(dialog__tt_create)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(dialog__tt_create)
        self.buttonBox.accepted.connect(dialog__tt_create.accept)
        self.buttonBox.rejected.connect(dialog__tt_create.reject)

        QMetaObject.connectSlotsByName(dialog__tt_create)
    # setupUi

    def retranslateUi(self, dialog__tt_create):
        dialog__tt_create.setWindowTitle(QCoreApplication.translate("dialog__tt_create", u"Create new TikTok account", None))
        self.ttcreatedialog__uid_container.setTitle(QCoreApplication.translate("dialog__tt_create", u"TikTok UID / ID", None))
        self.ttcreatedialog__username_container.setTitle(QCoreApplication.translate("dialog__tt_create", u"Username", None))
        self.ttcreatedialog__password_container.setTitle(QCoreApplication.translate("dialog__tt_create", u"Password", None))
        self.ttcreatedialog__cookie_container.setTitle(QCoreApplication.translate("dialog__tt_create", u"Cookie", None))
    # retranslateUi

