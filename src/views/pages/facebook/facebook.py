# src/views/pages/facebook/facebook.py
from typing import List, Dict, Any, Optional
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QMenu,
    QMessageBox
)
from src.models.table_model import SocialTableModel
from src.entities import Device, Proxy, User, Social, Job
from src.constants import DeviceStatus, Platform, JobAction, JobStatus
from src.database.connection import DatabaseManager
from src.controllers._manager_controllers import ControllerManager
from src.utils.logger import logger

from src.ui.page_facebooks_ui import Ui_page__facebooks
from src.views.pages.facebook.facebook_action import FacebookAction

# =====================================================================
# BUSINESS LOGIC & WORKER DISPATCHER LAYER
# =====================================================================

class FacebookPageLogic(QObject):
    """
    Handles background business logic and data processing for the Facebook page.
    Acts as a bridge between the UI and low-level controllers/services.
    """
    delete_completed = Signal()
    message = Signal(str)

    def __init__(self, controllers: ControllerManager):
        super().__init__()
        self.controllers = controllers
        self.redis_facade = controllers.service_manager.redis

    def queue_launch_jobs(self, socials: List[Social]):
        """
        Creates and pushes basic launch jobs to Redis for the provided social accounts.
        """
        self.message.emit(f"🚀 Scheduling launch for {len(socials)} Facebook accounts...")
        logger.info(f"Scheduling launch for {len(socials)} Facebook accounts...")
        self.redis_facade.jobs.clear_all_job_data()
        queued_count = 0

        for social in socials:
            if not social.user_uuid:
                self.message.emit(f"⚠️ Skipping '{social.social_name}': Not linked to any Profile.")
                continue
                
            user = self.controllers.user_controller.get_by_id(social.user_uuid)
            if not user or not user.device_uuid:
                self.message.emit(f"⚠️ Skipping '{social.social_name}': Target Device not found.")
                continue

            job = Job(
                name=f"Launch FB - {social.social_name}",
                social_uuid=social.uuid,
                user_uuid=user.uuid,
                device_uuid=user.device_uuid,
                platform=Platform.FACEBOOK,
                action=JobAction.FB__LAUNCH_APP, 
                status=JobStatus.PENDING
            )
            job.parameters = {
                "open_scrcpy": True,
                "deeplink": "fb://feed",
            }

            try:
                self.redis_facade.jobs.push_job(job.to_dict())
                queued_count += 1
            except Exception as e:
                self.message.emit(f"❌ Error pushing job for {social.social_name}: {e}")
                logger.error(f"Error pushing job for {social.social_name}: {e}")
        
        if queued_count > 0:
            self.message.emit(f"✔️  Successfully queued {queued_count} launch jobs.")

    def delete_social_accounts(self, socials: List[Social]):
        """
        Deletes the specified social accounts from the database.
        """
        for social in socials:
            self.controllers.social_controller.delete(social.uuid)
        self.message.emit(f"🗑️ Deleted {len(socials)} social accounts.")
        self.delete_completed.emit()

    def push_jobs_to_redis(self, jobs: List[Job]):
        """
        Pushes a list of summarized/prepared jobs into the Redis pending queue.
        """
        queued_count = 0
        for job in jobs:
            try:
                self.redis_facade.jobs.push_job(job.to_dict())
                queued_count += 1
            except Exception as e:
                self.message.emit(f"❌ Error pushing job '{job.name}': {e}")
                logger.error(f"Error pushing job '{job.name}': {e}")
        
        if queued_count > 0:
            self.message.emit(f"🚀 Successfully pushed {queued_count} jobs to pending queue.")


# =====================================================================
# UI PRESENTATION LAYER
# =====================================================================

class FacebookPage(QWidget, Ui_page__facebooks):
    """
    UI controller for the Facebook account management page.
    Manages the account table, dynamic action panel, and localized job preview.
    """
    message = Signal(str)

    def __init__(self, controllers: ControllerManager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.controllers = controllers
        self.logic = FacebookPageLogic(controllers)
        
        self.logic.message.connect(self.message.emit)
        
        self.social_model: Optional[SocialTableModel] = None
        self.current_saved_actions: List[Dict[str, Any]] = []
        self.pending_jobs: List[Job] = []
        
        self._setup_model()
        self._setup_facebook_table()
        self._setup_actions_panel()
        self._connect_signals()
    
    def _setup_model(self):
        """Initializes the database table model with Facebook-specific filtering."""
        self.social_model = SocialTableModel(DatabaseManager())
        self.social_model.setFilter("social_platform = 'facebook'")
        self.social_model.select()
    
    def _setup_facebook_table(self):
        """Configures the behavior and visuals of the main account table."""
        self.page__facebooks_facebook_table.setModel(self.social_model)
        self.page__facebooks_facebook_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.page__facebooks_facebook_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.page__facebooks_facebook_table.setSortingEnabled(True)
        self.page__facebooks_facebook_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.page__facebooks_facebook_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.page__facebooks_facebook_table.customContextMenuRequested.connect(self._show_context_menu)
        
        hidden_columns = ["uuid", "user_uuid", "proxy_uuid", "created_at", "updated_at", "social_platform"]
        self._hide_columns(hidden_columns)

    def _apply_filters(self):
        """
        Applies dynamic SQL filtering to the table model based on search inputs.

        This method retrieves text from various search input fields, sanitizes the 
        input by stripping whitespace, and constructs a SQL 'WHERE' clause. It 
        supports partial matches using the 'LIKE' operator and combines multiple 
        criteria using 'AND' logic. The resulting filter is applied to the 
        social_model to refresh the displayed data.
        """
        if not self.social_model:
            return
            
        uid_text = self.page__facebooks_search_uid_input.text().strip()
        username_text = self.page__facebooks_search_username_input.text().strip()
        group_text = self.page__facebooks_search_group_input.text().strip()
        
        filter_conditions = ["social_platform = 'facebook'"]
        
        if uid_text:
            filter_conditions.append(f"social_id LIKE '%{uid_text}%'")
        if username_text:
            filter_conditions.append(f"social_name LIKE '%{username_text}%'")
        if group_text:
            filter_conditions.append(f"social_group LIKE '%{group_text}%'")
            
        final_filter = " AND ".join(filter_conditions)
        
        self.social_model.setFilter(final_filter)
        self.social_model.select()

    def _setup_actions_panel(self):
        """Configures the side panel for dynamic action configuration and job preview."""
        self.page__facebooks_actions_scrollarea.setFixedWidth(380)
        self.page__facebooks_actions_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.page__facebooks_actions_scrollarea.setWidgetResizable(True)
        
        self.page__facebook_actions_container.setMaximumWidth(360) 
        self.page__facebook_actions_layout.addStretch()

        self.page__facebooks_layout.removeWidget(self.page__facebooks_actions_list)
        self.page__facebooks_actions_list.deleteLater()
        
        self.page__facebooks_actions_tree = QTreeWidget(self)
        self.page__facebooks_actions_tree.setHeaderHidden(True)
        self.page__facebooks_layout.addWidget(self.page__facebooks_actions_tree, 1, 1, 6, 1)

    def _hide_columns(self, column_names: List[str]):
        """Hides internal database columns from the UI table view."""
        if not self.social_model:
            return
        record = self.social_model.record()
        for i in range(record.count()):
            if record.fieldName(i) in column_names:
                self.page__facebooks_facebook_table.setColumnHidden(i, True)

    def _connect_signals(self):
        """Connects signals between the UI, logic layer, and global controllers."""
        selection_model = self.page__facebooks_facebook_table.selectionModel()
        selection_model.selectionChanged.connect(self._on_table_selection_changed)
        
        self.page__facebook_actions_add_btn.clicked.connect(self._on_add_action_clicked)
        self.page__facebooks_buttons_save_btn.clicked.connect(self._on_save_actions_clicked)
        self.page__facebooks_buttons_add_btn.clicked.connect(self._on_add_to_pending_clicked)
        
        self.controllers.device_controller.device_state_changed.connect(self.refresh_data)
        self.logic.delete_completed.connect(self.refresh_data)

        self.page__facebooks_search_uid_input.textChanged.connect(self._apply_filters)
        self.page__facebooks_search_username_input.textChanged.connect(self._apply_filters)
        self.page__facebooks_search_group_input.textChanged.connect(self._apply_filters)

    def _parse_social_from_record(self, record) -> Social:
        """Helper to convert a table record into a Social entity object."""
        return Social(
            uuid=record.value("uuid"),
            user_uuid=record.value("user_uuid"),
            social_id=record.value("social_id"),
            social_name=record.value("social_name"),
            social_password=record.value("social_password"),
            social_status=int(record.value("social_status") or 0),
            social_group=int(record.value("social_group") or 0),
            social_platform=record.value("social_platform"),
            created_at=record.value("created_at"),
            updated_at=record.value("updated_at")
        )

    def _show_context_menu(self, pos):
        """Generates and displays the context menu based on account connectivity."""
        if not self.social_model:
            return
            
        selected_indexes = self.page__facebooks_facebook_table.selectionModel().selectedRows()
        if not selected_indexes:
            return
        
        online_socials = []
        offline_socials = []
        all_socials = []
        
        for idx in selected_indexes:
            if idx.isValid():
                record = self.social_model.record(idx.row())
                social = self._parse_social_from_record(record)
                all_socials.append(social)
                
                is_online = False
                if social.user_uuid:
                    user = self.controllers.user_controller.get_by_id(social.user_uuid)
                    if user and user.device_uuid:
                        device = self.controllers.device_controller.get_by_id(user.device_uuid)
                        if device and str(device.device_status).lower() == "online":
                            is_online = True
                
                if is_online:
                    online_socials.append(social)
                else:
                    offline_socials.append(social)
        
        menu = QMenu(self)
        
        if online_socials:
            launch_act = menu.addAction(f"🚀 Launch ({len(online_socials)} online accounts)")
            launch_act.triggered.connect(lambda: self.logic.queue_launch_jobs(online_socials)) 
            
        if offline_socials:
            offline_act = menu.addAction(f"⚠️ {len(offline_socials)} accounts offline (Cannot launch)")
            offline_act.setEnabled(False) 
            
        menu.addSeparator()
        
        delete_act = menu.addAction(f"🗑 Delete ({len(all_socials)} accounts)")
        delete_act.triggered.connect(lambda: self._prompt_delete_socials(all_socials))
        
        menu.exec(self.page__facebooks_facebook_table.viewport().mapToGlobal(pos))

    def _prompt_delete_socials(self, socials: List[Social]):
        """Handles user confirmation for account deletion and UI cleanup."""
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete these {len(socials)} accounts from the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logic.delete_social_accounts(socials)
            
            deleted_uuids = [s.uuid for s in socials]
            self.pending_jobs = [job for job in self.pending_jobs if job.social_uuid not in deleted_uuids]
            self._render_pending_jobs()

    def _on_add_action_clicked(self):
        """Instantiates a new action widget in the dynamic configuration panel."""
        action_widget = FacebookAction(self)
        btn_index = self.page__facebook_actions_layout.indexOf(self.page__facebook_actions_add_btn)
        self.page__facebook_actions_layout.insertWidget(btn_index, action_widget)

    def _on_save_actions_clicked(self):
        """Processes configured actions and targets to generate local pending jobs."""
        if not self.social_model: return
        selected_indexes = self.page__facebooks_facebook_table.selectionModel().selectedRows()
        
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "Please select at least one Facebook account from the table.")
            return

        actions_data = []
        for i in range(self.page__facebook_actions_layout.count()):
            item = self.page__facebook_actions_layout.itemAt(i)
            widget = item.widget() if item is not None else None
            
            if isinstance(widget, FacebookAction):
                val = widget.get_value()
                if val is not None:
                    actions_data.append(val)
        
        self.current_saved_actions = actions_data
        
        selected_social_uuids = []
        selected_social_records = []
        
        for idx in selected_indexes:
            if idx.isValid():
                record = self.social_model.record(idx.row())
                social = self._parse_social_from_record(record)
                selected_social_uuids.append(social.uuid)
                selected_social_records.append(social)

        self.pending_jobs = [job for job in self.pending_jobs if job.social_uuid not in selected_social_uuids]
        
        skipped_count = 0
        added_jobs_count = 0

        if actions_data:
            for social in selected_social_records:
                if not social.user_uuid:
                    skipped_count += 1
                    continue
                    
                user = self.controllers.user_controller.get_by_id(social.user_uuid)
                if not user or not user.device_uuid:
                    skipped_count += 1
                    continue
                
                for act_data in actions_data:
                    action_enum = act_data['action']
                    params = dict(act_data['params']) 
                    
                    # ==========================================
                    # ⚡ CONTENT DATA PROCESSING (EXTERNAL DATA)
                    # ==========================================
                    if action_enum in [JobAction.FB__POST_GROUP, JobAction.FB__LIST_MARKETPLACE_AND_SHARE]:
                        source_type = params.get("source_type")
                        
                        # Case 1: Manual User Input (Custom)
                        if source_type == "custom_content":
                            params["title"] = params.pop("custom_title", "")
                            params["description"] = params.pop("custom_desc", "")
                            params["image_paths"] = params.pop("custom_images", [])
                            
                        # Case 2: Post based on a specific Product ID
                        elif source_type == "product_id":
                            pid = params.get("product_id")
                            # if pid:
                            if not self.controllers.external_db_controller.get_by_pid(pid if type(pid) == str else str(pid)):
                                pid = self.controllers.external_db_controller.get_random_pid()
                            if pid:
                                content = self.controllers.external_db_controller.generate_content_by_pid(pid)
                            else:
                                continue 
                            if content:
                                params["title"] = content.get("title", "")
                                params["description"] = content.get("description", "")
                                params["image_paths"] = content.get("image_paths", [])
                            else:
                                self.message.emit(f"⚠️ Could not generate content for PID {pid}.")
                                    
                        # Case 3: Randomly select a recently updated product
                        elif source_type == "random_product":
                            pid = self.controllers.external_db_controller.get_random_pid()
                            if pid:
                                content = self.controllers.external_db_controller.generate_content_by_pid(pid)
                                if content:
                                    params["title"] = content.get("title", "")
                                    params["description"] = content.get("description", "")
                                    params["image_paths"] = content.get("image_paths", [])
                                    params["product_id"] = pid 
                                else:
                                    self.message.emit(f"⚠️ Error generating content from random PID {pid}.")
                            else:
                                self.message.emit("⚠️ No random products found in the system.")

                        # Cleanup redundant keys to keep params lightweight and clean
                        params.pop("source_type", None)

                    # CREATE JOB ONCE PARAMS ARE FULLY PREPARED
                    job = Job(
                        name=f"Automate - {social.social_name} ({social.social_id}) - {action_enum}",
                        social_uuid=social.uuid,
                        user_uuid=user.uuid,
                        device_uuid=user.device_uuid,
                        platform=Platform.FACEBOOK,
                        action=action_enum,
                        status=JobStatus.PENDING,
                        parameters=params
                    )
                    self.pending_jobs.append(job)
                    added_jobs_count += 1

        self._render_pending_jobs()

        if actions_data:
            msg = f"Updated {added_jobs_count} Jobs for {len(selected_social_uuids)} accounts."
        else:
            msg = f"Removed all Jobs for {len(selected_social_uuids)} selected accounts as no actions were defined."
        
        self.message.emit(f"💾 {msg}")
            
        if skipped_count > 0:
            msg += f"\n\n⚠️ Skipped {skipped_count} accounts as they are not linked to a Profile/Device."
            
        logger.info(f"Updated pending jobs. Current total: {len(self.pending_jobs)} Jobs.")
        QMessageBox.information(self, "Update Successful", msg)

    def _render_pending_jobs(self):
        """Visualizes locally generated jobs in a hierarchical tree format."""
        self.page__facebooks_actions_tree.clear()
        
        grouped_jobs = {}
        for job in self.pending_jobs:
            if job.social_uuid not in grouped_jobs:
                social = self.controllers.social_controller.get_by_id(job.social_uuid)
                social_name = social.social_name if social else "Unknown Account"
                social_id = social.social_id if social else "Unknown ID"
                
                grouped_jobs[job.social_uuid] = {
                    "account_name": social_name,
                    "social_id": social_id,
                    "jobs": []
                }
            grouped_jobs[job.social_uuid]["jobs"].append(job)
            
        for suid, data in grouped_jobs.items():
            account_item = QTreeWidgetItem(self.page__facebooks_actions_tree)
            account_item.setText(0, f"👤 {data['account_name']} ({data['social_id']})")
            account_item.setExpanded(True)
            
            for job in data["jobs"]:
                action_item = QTreeWidgetItem(account_item)
                action_item.setText(0, f"⚡ {job.action.value}")
                action_item.setExpanded(False)
                
                for key, value in job.parameters.items():
                    param_item = QTreeWidgetItem(action_item)
                    
                    val_str = str(value)
                    if len(val_str) > 60:
                        val_str = val_str[:60] + "..."
                        
                    param_item.setText(0, f"▪ {key}: {val_str}")

    def _on_add_to_pending_clicked(self):
        """Delegates local jobs to the logic layer for Redis deployment."""
        if not self.pending_jobs:
            self.message.emit("⚠️ No jobs available to push. Please Save configuration first.")
            return
        self.logic.push_jobs_to_redis(self.pending_jobs)
        msg = f"✔️ Add to {len(self.pending_jobs)} pending jobs to redis"
        logger.success(msg)
        self.message.emit(msg)

        self.pending_jobs.clear()
        self._render_pending_jobs()

    def _on_table_selection_changed(self, selected, deselected):
        """Handles UI updates when row selection changes in the account table."""
        if not self.social_model:
            return
        selected_indexes = self.page__facebooks_facebook_table.selectionModel().selectedRows()
        
        if len(selected_indexes) == 1:
            idx = selected_indexes[0]
            if idx.isValid():
                record = self.social_model.record(idx.row())
                social = self._parse_social_from_record(record)
                
                user = self.controllers.user_controller.get_by_id(social.user_uuid) if social.user_uuid else None
                device = self.controllers.device_controller.get_by_id(user.device_uuid) if user and user.device_uuid else None
                
                self._update_info_panel(device, user)
        else:
            self._update_info_panel(None, None)

    def _update_info_panel(self, device: Optional[Device], user: Optional[User]):
        """Populates the side information panel with details from selected entities."""
        if device:
            self.page__facebooks_info__deviceudid_info.setText(device.device_id)
            self.page__facebooks_info__devicestatus_info.setText(device.device_status.capitalize())
        else:
            self.page__facebooks_info__deviceudid_info.setText("---")
            self.page__facebooks_info__devicestatus_info.setText("---")
            
        if user:
            self.page__facebooks_info__userid_info.setText(str(user.user_id))
            self.page__facebooks_info__username_info.setText(user.user_name)
            self.page__facebooks_info__userstatus_info.setText(user.user_status.capitalize())
        else:
            self.page__facebooks_info__userid_info.setText("---")
            self.page__facebooks_info__username_info.setText("---")
            self.page__facebooks_info__userstatus_info.setText("---")

    def refresh_data(self):
        """Synchronizes the table model with the database state."""
        if self.social_model:
            self.social_model.select()
