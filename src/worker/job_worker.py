# src/worker/job_worker.py
import time
from typing import Optional, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal, QThread

from src.entities import Job
from src.constants import Platform, DeviceStatus, JobAction
from src.automation.facebook.router import route_facebook_job
from src.automation.tiktok.router import route_tiktok_job
from src.worker.job_env import setup_device_environment, teardown_device_environment
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager

class JobExecutionWorker(QThread):
    """
    Worker thread responsible for polling jobs from Redis and executing them on mobile devices.
    
    This worker handles the full lifecycle of a job:
    1. Polling the pending queue from Redis.
    2. Setting up the device environment (Proxy, Network, User switching).
    3. Executing either manual (Scrcpy-based) or automated scripts.
    4. Tearing down the environment and reporting results.
    
    The worker includes an auto-termination mechanism if it remains idle for too long.
    """
    message = Signal(str)
    request_scrcpy = Signal(object)
    request_update_device = Signal(object)

    def __init__(self, controllers: "ControllerManager"):
        super().__init__()
        self.controllers = controllers
        self.redis_facade = controllers.service_manager.redis
        self.is_running = True
    
    def run(self):
        """
        Main execution loop for the thread.
        
        It continuously pops jobs from Redis with a 2-second timeout.
        If no jobs are found for 5 consecutive iterations, the thread terminates to save resources.
        """
        idle_count = 0 
        
        while self.is_running:
            job_data = self.redis_facade.jobs.pop_job(timeout=2)
            
            if not job_data: 
                idle_count += 1
                if idle_count >= 5:
                    break 
                continue
                
            idle_count = 0
            job = Job.from_dict(job_data)
            
            if not job: 
                continue
                
            # 1. Retrieve device information from the database
            device = self.controllers.device_controller.get_by_id(job.device_uuid)
            
            if not device or device.device_status != DeviceStatus.ONLINE:
                logger.debug(f"Device {job.device_uuid} is offline/busy in DB.")
                self.redis_facade.jobs.requeue_job(job_data)
                time.sleep(120)
                continue
            lock_key = f"farm:device:lock:{device.device_id}"
            is_locked = self.redis_facade.devices.redis.set(lock_key, "LOCKED", nx=True, ex=3600)
            
            if not is_locked:
                logger.debug(f"Device {device.device_id} is currently locked by another worker.")
                self.redis_facade.jobs.requeue_job(job_data)
                time.sleep(120)
                continue

            # If locking is successful, proceed with UI updates and state transition
            device.device_status = DeviceStatus.WORKING
            self.request_update_device.emit(device)
            self.redis_facade.jobs.set_job_active(job.uuid, job_data)
            
            user = self.controllers.user_controller.get_by_id(job.user_uuid)
            if not user:
                err_msg = f"User {job.user_uuid} no longer exists in Database."
                logger.error(f"[{job.name}] {err_msg}")
                self.message.emit(f"❌ Skipping Job '{job.name}': {err_msg}")
                self.redis_facade.jobs.set_job_result(job.uuid, False, err_msg)
                
                device.device_status = DeviceStatus.ONLINE
                self.request_update_device.emit(device)
                self.redis_facade.jobs.remove_job_active(job.uuid)
                
                continue
                
            proxy = None
            is_setup_success = False

            try:
                is_setup_success, proxy, msg = setup_device_environment(self.controllers, device, user)
                if not is_setup_success:
                    if not proxy: 
                        self.controllers.service_manager.redis.jobs.requeue_job(job_data)
                    else: 
                        self.message.emit(f"❌ Setup error for Job '{job.name}': {msg}")
                        self.controllers.service_manager.redis.jobs.set_job_result(job.uuid, False, msg)
                    continue

                self.message.emit(f"▶️ Starting '{job.name}' on {device.device_name}...")
                
                if job.parameters.get("open_scrcpy"):
                    self.request_scrcpy.emit(device)
                    # time.sleep(2) 
                
                action = getattr(job, 'action', '')
                if action in [JobAction.FB__LAUNCH_APP, JobAction.TT__LAUNCH_APP, JobAction.LAUNCH]: 
                    self.message.emit(f"⏳ [Manual Mode] Waiting for interaction. Close Scrcpy window to finish...")
                    if action == JobAction.FB__LAUNCH_APP:
                        route_facebook_job(device.device_id, job, self.message, self.controllers)
                        pass
                    elif action == JobAction.TT__LAUNCH_APP:
                        route_tiktok_job(device.device_id, job, self.message)
                        pass
                    elif action == JobAction.LAUNCH:
                        pass
                    
                    while self.controllers.device_controller.is_scrcpy_running(device.device_id) and self.is_running:
                        time.sleep(1) 
                        
                    self.message.emit(f"🚪 Scrcpy window closed. Cleaning up environment...")
                    
                elif job.platform == Platform.FACEBOOK:
                    route_facebook_job(device.device_id, job, self.message, self.controllers)
                    
                elif job.platform == Platform.TIKTOK:
                    route_tiktok_job(device.device_id, job, self.message)
                
                self.redis_facade.jobs.set_job_result(job.uuid, True, "Job completed successfully.")
                self.message.emit(f"✔️  Finished '{job.name}'.")
                
            except Exception as e:
                err_mes = str(e)
                self.redis_facade.jobs.set_job_result(job.uuid, False, err_mes)
                self.message.emit(f"❌ Error during '{job.name}': {err_mes}")
                
            finally:
                if is_setup_success:
                    teardown_device_environment(self.controllers, device, proxy)
                device.device_status = DeviceStatus.ONLINE
                self.request_update_device.emit(device)
                self.redis_facade.jobs.remove_job_active(job.uuid)
                self.redis_facade.devices.redis.delete(lock_key)
                # self.message.emit(f"✔️  Finished '{job.name}' on {device.device_name}")
    
    def stop(self):
        """
        Gracefully stops the worker execution.
        """
        self.is_running = False
        self.wait()

