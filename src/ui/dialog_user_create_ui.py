# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_user_create.ui'
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
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_dialog__create_new_user(object):
    def setupUi(self, dialog__create_new_user):
        if not dialog__create_new_user.objectName():
            dialog__create_new_user.setObjectName(u"dialog__create_new_user")
        dialog__create_new_user.resize(362, 87)
        self.verticalLayout = QVBoxLayout(dialog__create_new_user)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.newuser__dialog_username_label = QLabel(dialog__create_new_user)
        self.newuser__dialog_username_label.setObjectName(u"newuser__dialog_username_label")

        self.horizontalLayout.addWidget(self.newuser__dialog_username_label)

        self.newuser__dialog_username_qlineedit = QLineEdit(dialog__create_new_user)
        self.newuser__dialog_username_qlineedit.setObjectName(u"newuser__dialog_username_qlineedit")

        self.horizontalLayout.addWidget(self.newuser__dialog_username_qlineedit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(dialog__create_new_user)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(dialog__create_new_user)
        self.buttonBox.accepted.connect(dialog__create_new_user.accept)
        self.buttonBox.rejected.connect(dialog__create_new_user.reject)

        QMetaObject.connectSlotsByName(dialog__create_new_user)
    # setupUi

    def retranslateUi(self, dialog__create_new_user):
        dialog__create_new_user.setWindowTitle(QCoreApplication.translate("dialog__create_new_user", u"Create new user", None))
        self.newuser__dialog_username_label.setText(QCoreApplication.translate("dialog__create_new_user", u"Username", None))
    # retranslateUi

