# src/worker/job_worker.py
import time
from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, QThread

from src.entities import Job
from src.constants import Platform, DeviceStatus, JobAction, ProxyType
from src.automation.facebook.router import route_facebook_job
from src.automation.tiktok.router import route_tiktok_job
from src.worker.job_env import setup_device_environment, teardown_device_environment
from src.utils.logger import logger

if TYPE_CHECKING:
    from src.controllers._manager_controllers import ControllerManager

class JobExecutionWorker(QThread):
    message = Signal(str)
    request_scrcpy = Signal(object)
    request_update_device = Signal(object)

    def __init__(self, controllers: "ControllerManager"):
        super().__init__()
        self.controllers = controllers
        self.redis_facade = controllers.service_manager.redis
        self.is_running = True
    
    def run(self):
        idle_count = 0 
        
        while self.is_running:
            job_data = self.redis_facade.jobs.pop_job(timeout=2)
            
            if not job_data: 
                idle_count += 1
                if idle_count >= 5:
                    break
                # logger.debug("No job available. Waiting...")
                continue
                
            idle_count = 0
            job = Job.from_dict(job_data)
            if not job:
                # logger.debug("Invalid job data. Skipping...")
                continue
                
            device = self.controllers.device_controller.get_by_id(job.device_uuid)
            if not device or device.device_status != DeviceStatus.ONLINE:
                self.redis_facade.jobs.requeue_job(job_data)
                time.sleep(1)
                # logger.debug("Device not available. Waiting...")
                continue

            lock_key = f"farm:device:lock:{device.device_id}"
            is_locked = self.redis_facade.devices.redis.set(lock_key, "LOCKED", nx=True, ex=3600)
            
            if not is_locked:
                self.redis_facade.jobs.requeue_job(job_data)
                time.sleep(1)
                # logger.debug("Device is locked. Waiting...")
                continue

            is_setup_success = False
            proxy = None
            
            try:
                device.device_status = DeviceStatus.WORKING
                self.request_update_device.emit(device)
                self.redis_facade.jobs.set_job_active(job.uuid, job_data)
                
                user = self.controllers.user_controller.get_by_id(job.user_uuid)
                if not user:
                    err_msg = f"User {job.user_uuid} no longer exists in database."
                    logger.error(f"[{job.name}] {err_msg}")
                    self.message.emit(f"❌ Skipping Job '{job.name}': {err_msg}")
                    self.redis_facade.jobs.set_job_result(job.uuid, False, err_msg)
                    # logger.debug(f"[{job.name}] {err_msg}")
                    continue 
                
                is_setup_success, proxy, msg = setup_device_environment(self.controllers, device, user)                
                if not is_setup_success:
                    if "Proxy rotation error" in msg or "No available proxies" in msg:
                        self.redis_facade.jobs.requeue_job(job_data)
                        time.sleep(2)
                    else:
                        self.message.emit(f"❌ Setup error for Job '{job.name}': {msg}")
                        self.redis_facade.jobs.set_job_result(job.uuid, False, f"Setup Failed: {msg}")
                    # logger.debug(f"[{job.name}] {msg}")
                    continue
                
                self.message.emit(f"▶️ Starting '{job.name}' on {device.device_name}...")
                
                if job.parameters.get("open_scrcpy"):
                    self.request_scrcpy.emit(device)
                
                action = getattr(job, 'action', '')
                if action in [JobAction.FB__LAUNCH_APP, JobAction.TT__LAUNCH_APP, JobAction.LAUNCH]: 
                    self.message.emit(f"⏳ [Manual Mode] Waiting for interaction. Close Scrcpy window to finish...")
                    
                    if action == JobAction.FB__LAUNCH_APP:
                        route_facebook_job(device.device_id, job, self.message, self.controllers)
                    elif action == JobAction.TT__LAUNCH_APP:
                        route_tiktok_job(device.device_id, job, self.message)
                    
                    while self.controllers.device_controller.is_scrcpy_running(device.device_id) and self.is_running:
                        time.sleep(1) 
                        
                    self.message.emit(f"🚪 Scrcpy window closed. Cleaning up environment...")
                    
                elif job.platform == Platform.FACEBOOK:
                    route_facebook_job(device.device_id, job, self.message, self.controllers)
                    
                elif job.platform == Platform.TIKTOK:
                    route_tiktok_job(device.device_id, job, self.message)
                
                self.redis_facade.jobs.set_job_result(job.uuid, True, "Job completed successfully.")
                self.message.emit(f"✔️ Finished '{job.name}'.")
                
            except Exception as e:
                err_mes = str(e)
                logger.error(f"Job execution error on {device.device_id}: {err_mes}")
                self.redis_facade.jobs.set_job_result(job.uuid, False, err_mes)
                self.message.emit(f"❌ Error during '{job.name}': {err_mes}")
                
            finally:
                if is_setup_success:
                    teardown_device_environment(self.controllers, device, proxy)
                
                self.redis_facade.jobs.remove_job_active(job.uuid)
                
                device.device_status = DeviceStatus.ONLINE
                self.request_update_device.emit(device)
                
                self.redis_facade.devices.redis.delete(lock_key)
    
    def stop(self):
        """Gracefully stops the worker execution loop."""
        self.is_running = False
        self.wait()