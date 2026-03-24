# src/automation/facebook/actions/launch.py
from src.entities import Job
from src.automation.core.base_automator import BaseAutomator

def run_launch_app(device_id: str, job: Job, logger_signal):
    """
    Execution script to launch the Facebook application on a mobile device.
    
    This function initializes a BaseAutomator instance to handle the application 
    startup. It supports launching via a specific deep link if provided in the 
    job parameters; otherwise, it performs a standard cold start of the 
    'com.facebook.katana' package.
    
    Args:
        device_id (str): The identifier for the target Android device.
        job (Job): The job entity containing execution parameters.
        logger_signal (Signal): The PySide6 signal used to relay logs to the UI.
    """
    bot = BaseAutomator(device_id, logger_signal)
    
    deeplink = job.parameters.get("deeplink")
    package_name = "com.facebook.katana"
    
    bot.launch_app(package_name, deeplink)
    bot.smart_sleep(5)
    
    bot.log("✔️  Facebook application is now ready.")