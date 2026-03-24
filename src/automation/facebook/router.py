# src/automation/facebook/router.py
from typing import TYPE_CHECKING
from src.entities import Job
from src.constants import JobAction
from src.automation.facebook.actions.launch import run_launch_app
from src.automation.facebook.actions.list_marketplace_share import run_list_marketplace_share
from src.utils.logger import logger

if TYPE_CHECKING:
    from PySide6.QtCore import SignalInstance
    from src.controllers._manager_controllers import ControllerManager


def route_facebook_job(device_id: str, job: Job, logger_signal: "SignalInstance", controllers: "ControllerManager"):
    """
    Routes Facebook-specific automation tasks to their respective action handlers.
    
    This function acts as a dispatcher within the Facebook automation module, 
    identifying the required 'action' from the job entity and executing the 
    corresponding logic.
    
    Args:
        device_id (str): The identifier for the target Android device.
        job (Job): The job entity containing the action type and execution parameters.
        logger_signal (Optional[Signal]): Signal used to relay execution logs to the UI.
        
    Raises:
        ValueError: If the requested Facebook action is not recognized or implemented.
    """
    action = getattr(job, 'action', '')

    if action == JobAction.FB__LAUNCH_APP:
        run_launch_app(device_id, job, logger_signal)
        
    elif action == JobAction.FB__SCROLL_FEED:
        logger.debug(job)
    elif action == JobAction.FB__INTERACT_FEED:
        logger.debug(job)
    elif action == JobAction.FB__POST_GROUP:
        logger.debug(job)
    elif action == JobAction.FB__INTERACT_TARGET:
        logger.debug(job)
    elif action == JobAction.FB__LIST_MARKETPLACE_AND_SHARE:
        run_list_marketplace_share(device_id, job, logger_signal, controllers)
        
    else:
        raise ValueError(f"Facebook action '{action}' is not currently supported.")