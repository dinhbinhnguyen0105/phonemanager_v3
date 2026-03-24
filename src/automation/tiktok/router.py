# src/automation/tiktok/router.py

from src.entities import Job
from src.constants import JobAction
from src.automation.tiktok.actions import launch

def route_tiktok_job(device_id: str, job: Job, logger_signal=None):
    """
    Routes TikTok-specific automation tasks to their respective action handlers.
    
    This function identifies the required 'action' from the job entity and 
    delegates the execution to the corresponding script within the TikTok module.
    
    Args:
        device_id (str): The identifier for the target Android device.
        job (Job): The job entity containing the action type and execution parameters.
        logger_signal (Optional[Signal]): Signal used to relay execution logs to the UI.
        
    Raises:
        ValueError: If the requested TikTok action is not recognized or implemented.
    """
    action = getattr(job, 'action', '')
    
    if action == JobAction.TT__LAUNCH_APP:
        launch.run_launch_app(device_id, job, logger_signal)
    else:
        raise ValueError(f"Action '{action}' is not currently supported.")