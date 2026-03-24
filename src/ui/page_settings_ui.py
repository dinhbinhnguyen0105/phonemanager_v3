# src\ui\page_settings_ui.py
# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'page_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QHeaderView, QLineEdit, QPushButton,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_PageSettings(object):
    def setupUi(self, PageSettings):
        if not PageSettings.objectName():
            PageSettings.setObjectName(u"PageSettings")
        PageSettings.resize(910, 640)
        PageSettings.setStyleSheet(u"#PageSettings{\n"
"  font-family: \"Courier New\";\n"
"font-size: 13px;\n"
"  background-color: #FFFFFF;\n"
"}\n"
"QGroupBox {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  background-color: rgba(248, 249, 250, 1);\n"
"}\n"
"QLineEdit {\n"
"  padding: 4px 0;\n"
"  border: 1px solid #ced4da;\n"
"  border-radius: 8px;\n"
"  margin-left: 8px;\n"
"  padding-left: 4px;\n"
"  background-color: #FFFFFF;\n"
"  color:#212529;\n"
"}\n"
"QPlainTextEdit {\n"
"	background-color: #FFFFFF;\n"
"  color:#212529;\n"
"}\n"
"QLabel {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: rgb(90, 93, 97);\n"
"}\n"
"QRadioButton {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: #212529;\n"
"}\n"
"QComboBox {\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: #212529;\n"
"}\n"
"QCheckBox{\n"
"  font-family: \"Courier New\";\n"
"  font-size: 13px;\n"
"  color: #212529;\n"
"}\n"
"QPushButton {\n"
"  color: #212529;\n"
"}\n"
"\n"
"")
        self.horizontalLayout = QHBoxLayout(PageSettings)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 8, 8, 8)
        self.PageSettings_layout = QVBoxLayout()
        self.PageSettings_layout.setSpacing(4)
        self.PageSettings_layout.setObjectName(u"PageSettings_layout")
        self.PageSettings_layout.setContentsMargins(-1, 0, -1, 0)
        self.setting_option = QComboBox(PageSettings)
        self.setting_option.setObjectName(u"setting_option")

        self.PageSettings_layout.addWidget(self.setting_option)

        self.setting_input = QGroupBox(PageSettings)
        self.setting_input.setObjectName(u"setting_input")
        self.horizontalLayout_12 = QHBoxLayout(self.setting_input)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(4, 4, 4, 4)
        self.setting_input_layout = QHBoxLayout()
        self.setting_input_layout.setObjectName(u"setting_input_layout")
        self.setting_value = QLineEdit(self.setting_input)
        self.setting_value.setObjectName(u"setting_value")

        self.setting_input_layout.addWidget(self.setting_value)

        self.setting_is_selected = QCheckBox(self.setting_input)
        self.setting_is_selected.setObjectName(u"setting_is_selected")

        self.setting_input_layout.addWidget(self.setting_is_selected)

        self.setting_save_btn = QPushButton(self.setting_input)
        self.setting_save_btn.setObjectName(u"setting_save_btn")

        self.setting_input_layout.addWidget(self.setting_save_btn)


        self.horizontalLayout_12.addLayout(self.setting_input_layout)


        self.PageSettings_layout.addWidget(self.setting_input)

        self.setting_table = QTableView(PageSettings)
        self.setting_table.setObjectName(u"setting_table")

        self.PageSettings_layout.addWidget(self.setting_table)


        self.horizontalLayout.addLayout(self.PageSettings_layout)


        self.retranslateUi(PageSettings)

        QMetaObject.connectSlotsByName(PageSettings)
    # setupUi

    def retranslateUi(self, PageSettings):
        PageSettings.setWindowTitle(QCoreApplication.translate("PageSettings", u"Form", None))
        self.setting_input.setTitle(QCoreApplication.translate("PageSettings", u"Add new profile container directory", None))
        self.setting_value.setPlaceholderText(QCoreApplication.translate("PageSettings", u"Click to select profile container directory", None))
        self.setting_is_selected.setText(QCoreApplication.translate("PageSettings", u"Set selected", None))
        self.setting_save_btn.setText(QCoreApplication.translate("PageSettings", u"Save", None))
    # retranslateUi

