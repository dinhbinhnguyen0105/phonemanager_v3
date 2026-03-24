# src/views/pages/facebook/facebook_action.py
from typing import Optional, List, Dict, Any, Tuple
import os
from PySide6.QtWidgets import (
    QGroupBox, 
    QVBoxLayout, 
    QHBoxLayout, 
    QGridLayout, 
    QLabel, 
    QLineEdit, 
    QTextEdit, 
    QRadioButton, 
    QButtonGroup, 
    QSpinBox,
    QWidget,
    QListWidget,
    QFileDialog,
    QAbstractItemView,
    QSizePolicy
)
from PySide6.QtCore import Qt
from src.ui.facebook_action_ui import Ui_action
from src.constants import JobAction, FacebookReaction

class ImageDropWidget(QListWidget):
    """
    Custom QListWidget supporting Drag & Drop and Double-click for multiple image selection.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setToolTip("Double-click to open file explorer.\nDrag and drop images here.\nSelect and press Delete to remove.")
        self.setMaximumHeight(80) 

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    self._add_image(path)

    def mouseDoubleClickEvent(self, event) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        for f in files:
            self._add_image(f)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in self.selectedItems():
                self.takeItem(self.row(item))
        else:
            super().keyPressEvent(event)

    def _add_image(self, path: str) -> None:
        existing = [self.item(i).text() for i in range(self.count())]
        if path not in existing:
            self.addItem(path)

    def get_paths(self) -> List[str]:
        """Returns a list of all stored file paths."""
        return [self.item(i).text() for i in range(self.count())]


class FacebookAction(QGroupBox, Ui_action):
    """
    Component for configuring individual Facebook automation actions.
    Handles dynamic UI generation based on the selected action type.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.action__content.setVisible(False)
        
        self.page_mapping = {
            JobAction.FB__SCROLL_FEED: self.action__content_scroll_feed_container,
            JobAction.FB__INTERACT_FEED: self.action__content_interact_feed_container,
            JobAction.FB__POST_GROUP: self.action__content_post_group_container,
            JobAction.FB__INTERACT_TARGET: self.action__content_interact_target_container,
            JobAction.FB__LIST_MARKETPLACE_AND_SHARE: self.action__content_list_marketplace_container
        }

        self._setup_combobox()
        self._build_scroll_feed_ui()
        self._build_interact_feed_ui()
        self._build_interact_target_ui()
        self._build_post_group_ui()
        self._build_list_marketplace_ui()
        
        self.action__actions_option.currentIndexChanged.connect(self._on_action_changed)
        self.action__delete_btn.clicked.connect(self.deleteLater)

    def _setup_combobox(self) -> None:
        options: List[Tuple[str, JobAction]] = [
            ("Scroll Feed", JobAction.FB__SCROLL_FEED),
            ("Interact Feed", JobAction.FB__INTERACT_FEED),
            ("Post to Group", JobAction.FB__POST_GROUP),
            ("Interact with Target", JobAction.FB__INTERACT_TARGET),
            ("List Marketplace & Share", JobAction.FB__LIST_MARKETPLACE_AND_SHARE),
        ]
        for label, enum_val in options:
            self.action__actions_option.addItem(label, userData=enum_val)

    def _on_action_changed(self, index: int) -> None:
        action_enum: Optional[JobAction] = self.action__actions_option.itemData(index)
        
        for i in range(self.action__content.count()):
            widget = self.action__content.widget(i)
            if not widget: continue
            widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        
        if not action_enum: 
            self.action__content.setVisible(False)
        else:
            self.action__content.setVisible(True)
            page = self.page_mapping.get(action_enum)
            if page:
                self.action__content.setCurrentWidget(page)
                page.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                page.adjustSize()
                
        self.action__content.adjustSize()
        self.adjustSize()

    def _build_scroll_feed_ui(self) -> None:
        layout = self.action__content_scroll_feed_layout
        row = QHBoxLayout()
        row.addWidget(QLabel("Time (s):"))
        self.sf_time = QLineEdit()
        self.sf_time.setPlaceholderText("e.g. 60")
        row.addWidget(self.sf_time)
        layout.addLayout(row)
        layout.addStretch()

    def _build_interact_feed_ui(self) -> None:
        layout = self.action__content_interact_feed_layout
        row_time = QHBoxLayout()
        row_time.addWidget(QLabel("Time (s):"))
        self.if_time = QLineEdit()
        self.if_time.setPlaceholderText("e.g. 120")
        row_time.addWidget(self.if_time)
        layout.addLayout(row_time)

        layout.addWidget(QLabel("Reaction:"))
        self.if_react_group = QButtonGroup(self)
        
        react_grid = QGridLayout()
        react_grid.setSpacing(5)
        
        rb_none = QRadioButton("None")
        rb_none.setChecked(True)
        rb_none.setProperty("reaction_enum", None)
        self.if_react_group.addButton(rb_none, 0)
        react_grid.addWidget(rb_none, 0, 0)
        
        row, col = 0, 1
        for i, reaction in enumerate(FacebookReaction, start=1):
            rb = QRadioButton(reaction.value.capitalize())
            rb.setProperty("reaction_enum", reaction)
            self.if_react_group.addButton(rb, i)
            
            react_grid.addWidget(rb, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addLayout(react_grid)
        layout.addStretch()

    def _build_interact_target_ui(self) -> None:
        layout = self.action__content_interact_target_layout
        row_id = QHBoxLayout()
        row_id.addWidget(QLabel("Target Post/Page ID:"))
        self.it_target_id = QLineEdit()
        row_id.addWidget(self.it_target_id)
        layout.addLayout(row_id)
        
        row_time = QHBoxLayout()
        row_time.addWidget(QLabel("Time (s):"))
        self.it_time = QLineEdit()
        row_time.addWidget(self.it_time)
        layout.addLayout(row_time)
        
        layout.addWidget(QLabel("Comment:"))
        self.it_comment = QTextEdit()
        self.it_comment.setMaximumHeight(60)
        layout.addWidget(self.it_comment)
        
        layout.addWidget(QLabel("Reaction:"))
        self.it_react_group = QButtonGroup(self)
        
        react_grid = QGridLayout()
        react_grid.setSpacing(5)
        
        rb_none = QRadioButton("None")
        rb_none.setChecked(True)
        rb_none.setProperty("reaction_enum", None)
        self.it_react_group.addButton(rb_none, 0)
        react_grid.addWidget(rb_none, 0, 0)
        
        row, col = 0, 1
        for i, reaction in enumerate(FacebookReaction, start=1):
            rb = QRadioButton(reaction.value.capitalize())
            rb.setProperty("reaction_enum", reaction)
            self.it_react_group.addButton(rb, i)
            
            react_grid.addWidget(rb, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addLayout(react_grid)
        layout.addStretch()

    def _build_post_group_ui(self) -> None:
        layout = self.action__content_post_group_layout
        row_uid = QHBoxLayout()
        row_uid.addWidget(QLabel("Group UID:"))
        self.pg_group_uid = QLineEdit()
        row_uid.addWidget(self.pg_group_uid)
        layout.addLayout(row_uid)
        
        layout.addWidget(QLabel("Content Source:"))
        self.pg_source_group = QButtonGroup(self)
        
        source_grid = QGridLayout()
        source_grid.setSpacing(5)
        sources = ["Product ID", "Random Product", "Custom Content"]
        
        row, col = 0, 0
        for i, s in enumerate(sources):
            rb = QRadioButton(s)
            if i == 0: rb.setChecked(True)
            self.pg_source_group.addButton(rb, i)
            
            source_grid.addWidget(rb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(source_grid)
        
        self.pg_pid_container = QWidget()
        pg_pid_layout = QVBoxLayout(self.pg_pid_container)
        pg_pid_layout.setContentsMargins(0, 0, 0, 0)
        row_pid = QHBoxLayout()
        row_pid.addWidget(QLabel("Product ID:"))
        self.pg_product_id = QLineEdit()
        row_pid.addWidget(self.pg_product_id)
        pg_pid_layout.addLayout(row_pid)
        
        self.pg_custom_container = QWidget()
        pg_custom_layout = QVBoxLayout(self.pg_custom_container)
        pg_custom_layout.setContentsMargins(0, 0, 0, 0)
        pg_custom_layout.addWidget(QLabel("Custom Title:"))
        self.pg_custom_title = QLineEdit()
        pg_custom_layout.addWidget(self.pg_custom_title)
        pg_custom_layout.addWidget(QLabel("Custom Description:"))
        self.pg_custom_desc = QTextEdit()
        self.pg_custom_desc.setMaximumHeight(50)
        pg_custom_layout.addWidget(self.pg_custom_desc)
        pg_custom_layout.addWidget(QLabel("Custom Images (Drag & Drop or Double-click):"))
        self.pg_custom_images = ImageDropWidget()
        pg_custom_layout.addWidget(self.pg_custom_images)
        
        layout.addWidget(self.pg_pid_container)
        layout.addWidget(self.pg_custom_container)
        self.pg_custom_container.setVisible(False)
        self.pg_source_group.idToggled.connect(self._on_pg_source_toggled)
        layout.addStretch()

    def _on_pg_source_toggled(self, btn_id: int, checked: bool) -> None:
        if checked:
            self.pg_pid_container.setVisible(btn_id == 0)
            self.pg_custom_container.setVisible(btn_id == 2)

    def _build_list_marketplace_ui(self) -> None:
        layout = self.action__content_list_marketplace_layout
        row_share = QHBoxLayout()
        row_share.addWidget(QLabel("Number of Groups to Share:"))
        self.mp_share_count = QSpinBox()
        self.mp_share_count.setRange(0, 100)
        row_share.addWidget(self.mp_share_count)
        layout.addLayout(row_share)
        
        layout.addWidget(QLabel("Content Source:"))
        self.mp_source_group = QButtonGroup(self)
        
        source_grid = QGridLayout()
        source_grid.setSpacing(5)
        sources = ["Product ID", "Random Product", "Custom Content"]
        
        row, col = 0, 0
        for i, s in enumerate(sources):
            rb = QRadioButton(s)
            if i == 0: rb.setChecked(True)
            self.mp_source_group.addButton(rb, i)
            
            source_grid.addWidget(rb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(source_grid)
        
        self.mp_pid_container = QWidget()
        mp_pid_layout = QVBoxLayout(self.mp_pid_container)
        mp_pid_layout.setContentsMargins(0, 0, 0, 0)
        row_pid = QHBoxLayout()
        row_pid.addWidget(QLabel("Product ID:"))
        self.mp_product_id = QLineEdit()
        row_pid.addWidget(self.mp_product_id)
        mp_pid_layout.addLayout(row_pid)
        
        self.mp_custom_container = QWidget()
        mp_custom_layout = QVBoxLayout(self.mp_custom_container)
        mp_custom_layout.setContentsMargins(0, 0, 0, 0)
        mp_custom_layout.addWidget(QLabel("Custom Title:"))
        self.mp_custom_title = QLineEdit()
        mp_custom_layout.addWidget(self.mp_custom_title)
        mp_custom_layout.addWidget(QLabel("Custom Description:"))
        self.mp_custom_desc = QTextEdit()
        self.mp_custom_desc.setMaximumHeight(50)
        mp_custom_layout.addWidget(self.mp_custom_desc)
        mp_custom_layout.addWidget(QLabel("Custom Images (Drag & Drop or Double-click):"))
        self.mp_custom_images = ImageDropWidget()
        mp_custom_layout.addWidget(self.mp_custom_images)
        
        layout.addWidget(self.mp_pid_container)
        layout.addWidget(self.mp_custom_container)
        self.mp_custom_container.setVisible(False)
        self.mp_source_group.idToggled.connect(self._on_mp_source_toggled)
        layout.addStretch()

    def _on_mp_source_toggled(self, btn_id: int, checked: bool) -> None:
        if checked:
            self.mp_pid_container.setVisible(btn_id == 0)
            self.mp_custom_container.setVisible(btn_id == 2)

    def get_value(self) -> Optional[dict]:
        """
        Extracts configuration data from UI elements.
        
        Returns:
            dict: Configuration parameters mapped to JobAction, or None if widget is inactive.
        """
        if not self.isEnabled() or not self.isVisible(): 
            return None
        action: Optional[JobAction] = self.action__actions_option.currentData()
        if not action:
            return None 

        data: Dict[str, Any] = {
            "action": action, 
            "params": {}
        }
        source_keys: List[str] = ["product_id", "random_product", "custom_content"]

        if action == JobAction.FB__SCROLL_FEED:
            data["params"]["time_s"] = self.sf_time.text()

        elif action == JobAction.FB__INTERACT_FEED:
            data["params"]["time_s"] = self.if_time.text()
            btn = self.if_react_group.checkedButton()
            data["params"]["reaction"] = btn.property("reaction_enum") if btn else None

        elif action == JobAction.FB__INTERACT_TARGET:
            data["params"]["target_id"] = self.it_target_id.text()
            data["params"]["time_s"] = self.it_time.text()
            data["params"]["comment"] = self.it_comment.toPlainText()
            btn = self.it_react_group.checkedButton()
            data["params"]["reaction"] = btn.property("reaction_enum") if btn else None

        elif action == JobAction.FB__POST_GROUP:
            data["params"]["group_uid"] = self.pg_group_uid.text()
            source_id = self.pg_source_group.checkedId()
            data["params"]["source_type"] = source_keys[source_id]
            if source_id == 0:
                data["params"]["product_id"] = self.pg_product_id.text()
            elif source_id == 2:
                data["params"]["custom_title"] = self.pg_custom_title.text()
                data["params"]["custom_desc"] = self.pg_custom_desc.toPlainText()
                data["params"]["custom_images"] = self.pg_custom_images.get_paths()

        elif action == JobAction.FB__LIST_MARKETPLACE_AND_SHARE:
            data["params"]["share_groups_count"] = self.mp_share_count.value()
            source_id = self.mp_source_group.checkedId()
            data["params"]["source_type"] = source_keys[source_id]
            if source_id == 0:
                data["params"]["product_id"] = self.mp_product_id.text()
            elif source_id == 2:
                data["params"]["custom_title"] = self.mp_custom_title.text()
                data["params"]["custom_desc"] = self.mp_custom_desc.toPlainText()
                data["params"]["custom_images"] = self.mp_custom_images.get_paths()
        return data