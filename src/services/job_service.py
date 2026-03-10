# src/services/job_service.py
import uuid
import time
from typing import List, Dict, Any, Optional
from src.drivers.redis._manager_redis import RedisStateFacade

class JobService:
    """
    Service layer for managing background task queues.
    This class acts as a Producer, creating and tracking job progress via Redis.
    It does not inherit from BaseService as jobs are stored in Redis, not SQLite.
    """
    
    def __init__(self, redis_facade: RedisStateFacade):
        self.redis = redis_facade

    def create_job(self, action: str, target: str = "", params: Dict[str, Any] = None) -> str:
        """
        Creates a single job and pushes it to the Redis pending queue.

        :param action: Name of the script/action to perform (e.g., 'surf_tiktok').
        :param target: Specific target for the action (e.g., Post UID).
        :param params: Additional parameters for the action.
        :return: The generated unique job ID.
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "action": action,
            "target": target,
            "params": params or {},
            "status": "pending",
            "created_at": int(time.time())
        }
        
        # Dispatch to the infrastructure layer to push into Redis
        self.redis.jobs.push_job(job_data)
        return job_id

    def create_bulk_jobs(self, action: str, count: int, target: str = "", params: Dict[str, Any] = None) -> List[str]:
        """
        Creates multiple jobs (e.g., to distribute tasks across several devices).

        :param action: Name of the script/action to perform.
        :param count: The number of job instances to create.
        :param target: Specific target for the action.
        :param params: Additional parameters.
        :return: A list of generated job IDs.
        """
        job_ids = []
        for _ in range(count):
            job_id = self.create_job(action, target, params)
            job_ids.append(job_id)
        return job_ids

    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the result of a job after it has been processed by a worker.

        :param job_id: The unique identifier of the job.
        :return: A dictionary containing the job result, or None if not found.
        """
        result = self.redis.jobs.hget_all(f"result:{job_id}")
        return result if result else None

    def get_queue_length(self) -> int:
        """
        Checks the number of jobs currently waiting in the pending queue.

        :return: Number of pending jobs.
        """
        queue_key = self.redis.jobs._key("pending:queue")
        return self.redis.client.llen(queue_key)
        
    def clear_all_pending_jobs(self) -> None:
        """Clears the pending job queue (useful for emergency stop actions)."""
        queue_key = self.redis.jobs._key("pending:queue")
        self.redis.client.delete(queue_key)