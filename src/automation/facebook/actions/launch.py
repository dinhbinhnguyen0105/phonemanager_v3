# src/automation/facebook/actions/launch.py
import sys
import traceback
from src.entities import Job
from src.automation.core.base_automator import BaseAutomator
from src.utils.logger import logger

def run_launch_app(device_id: str, job: Job, logger_signal):
    """
    Execution script to launch the Facebook application on a mobile device.
    
    This function handles the application startup securely by performing a force-stop 
    to ensure a clean cold start, launching the app via package name or deep link, 
    and verifying that the UI reaches the foreground before proceeding.

    Args:
        device_id (str): The unique identifier of the target Android device.
        job (Job): The job entity containing execution parameters such as deep links.
        logger_signal (SignalInstance): PySide6 signal used to transmit logs to the UI.

    Raises:
        Exception: If the application fails to reach the foreground within the timeout 
                  or if a system error occurs during the launch process.
    """
    bot = BaseAutomator(device_id, logger_signal)
    package_name = "com.facebook.katana"
    deeplink = job.parameters.get("deeplink")
    
    try:
        bot.log("🔄 Preparing to launch Facebook...")
        
        bot.d.app_stop(package_name)
        bot.smart_sleep(1)
        
        bot.launch_app(package_name, deeplink)
        
        bot.log("⏳ Waiting for the application to load...")
        is_app_ready = bot.d.app_wait(package_name, front=True, timeout=15.0)
        
        if not is_app_ready:
            bot.log("⚠️ Facebook took too long to load or didn't open properly.")
            raise Exception("Application failed to reach foreground within 15 seconds.")
        else:
            bot.smart_sleep(3) 
            bot.log("✔️ Facebook application is now ready.")
            
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error(f"Launch Error on {device_id}:\n{''.join(tb_details)}")
        
        bot.log(f"❌ Error launching Facebook: {e}")
        raise e
        
    finally:
        bot.teardown()