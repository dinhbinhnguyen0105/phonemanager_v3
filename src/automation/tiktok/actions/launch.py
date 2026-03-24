# src/automation/tiktok/actions/launch.py
from src.entities import Job
from src.automation.core.base_automator import BaseAutomator

def run_launch_app(device_id: str, job: Job, logger_signal):
    """
    Execution script to launch the TikTok application on a mobile device.
    
    This function initializes a BaseAutomator instance to manage the TikTok 
    application lifecycle. It prioritizes launching via a deep link if 
    available in the job parameters for targeted navigation; otherwise, 
    it initiates a standard startup of the 'com.zhiliaoapp.musically' package.
    
    Args:
        device_id (str): The identifier for the target Android device.
        job (Job): The job entity containing execution parameters and deep link data.
        logger_signal (Signal): The PySide6 signal used to relay execution logs to the UI.
    """
    bot = BaseAutomator(device_id, logger_signal)
    
    deeplink = job.params_dict.get("deeplink")
    package_name = "com.zhiliaoapp.musically" 
    
    bot.launch_app(package_name, deeplink)
    bot.smart_sleep(5)
    
    bot.log("✔️  TikTok application is now ready.")