# src/drivers/redis/job_state.py

import json
from typing import Optional, Dict, Any, List
from src.drivers.redis.base_state import BaseState


class JobState(BaseState):
    """
    Manages the lifecycle and state of background jobs in Redis.
    Handles queuing of pending jobs, tracking active jobs, and storing results.
    """
    
    def __init__(self, redis_client):
        super().__init__(redis_client, namespace='farm:job')
        
    # ==========================================
    # 1. PENDING QUEUE (WAITING LIST)
    # ==========================================
    def push_job(self, job_data: Dict[str, Any]) -> None:
        """
        Pushes a new job into the pending queue for workers to process.
        Uses LPUSH (push to left) and BRPOP (pop from right) to create a FIFO model.
        """
        job_json = json.dumps(job_data)
        self.redis.lpush(self._key("pending:queue"), job_json)
        
    def requeue_job(self, job_data: Dict[str, Any]) -> None:
        """
        Pushes a job back into the queue if the device or proxy is busy.
        Reuses push_job to place it back at the end of the queue.
        """
        self.push_job(job_data)
        
    def pop_job(self, timeout: int = 2) -> Optional[Dict[str, Any]]:
        """
        Blocks and waits to retrieve a job from the pending queue.
        """
        result: Any = self.redis.brpop(self._key("pending:queue"), timeout=timeout)  # type: ignore
        if result:
            _, job_json = result
            return json.loads(job_json)
        return None
        
    def get_pending_count(self) -> int:
        """Counts the number of jobs waiting in the queue (Used for UI display)."""
        return self.redis.llen(self._key("pending:queue")) # type: ignore
        
    def clear_pending_queue(self) -> None:
        """Clears the entire queue (Used when the user clicks Stop/Cancel All)."""
        self.redis.delete(self._key("pending:queue"))

    # ==========================================
    # 2. ACTIVE JOBS (MANAGING RUNNING JOBS)
    # ==========================================
    def set_job_active(self, job_id: str, job_data: Dict[str, Any]) -> None:
        """
        Marks a job as currently processing (Resource locking).
        Stores the data in the 'active_jobs' Hash structure.
        """
        job_json = json.dumps(job_data)
        self.hset_dict("active_jobs", {job_id: job_json})
        
    def remove_job_active(self, job_id: str) -> None:
        """
        Removes a job from the active list (Upon completion or error).
        """
        self.hdel("active_jobs", job_id)
        
    def get_all_active_jobs(self) -> List[Dict[str, Any]]:
        """Retrieves a list of all jobs currently being processed by workers."""
        raw_data = self.hget_all("active_jobs")
        active_jobs = []
        for _, job_json in raw_data.items():
            active_jobs.append(json.loads(job_json))
        return active_jobs

    # ==========================================
    # 3. JOB RESULTS (EXECUTION RESULTS)
    # ==========================================
    def set_job_result(self, job_id: str, success: bool, log: str = "") -> None:
        """
        Stores the execution result of a job.
        """
        self.hset_dict(f"result:{job_id}", {
            "success": int(success),
            "log": str(log)
        })
        
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Retrieves the execution results of a specific job."""
        data =  self.hget_all(f"result:{job_id}")
        if not data:
            return {}
        else:
            return {
                "success": bool(data.get("success", 0)),
                "log": data.get("log", "")
            }

    def clear_all_job_data(self) -> None:
        """
        NEW: Completely wipes all job-related data from Redis.
        This includes pending queues, active job locks, and result history.
        """
        # 1. Clear the pending queue
        self.clear_pending_queue()
        
        # 2. Clear the active jobs hash
        self.redis.delete(self._key("active_jobs"))
        
        # 3. Clear all individual result hashes
        # Caution: SCAN is used to avoid blocking the Redis server with large datasets
        cursor = 0
        pattern = self._key("result:*")
        while True:
            cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=100) # type: ignore
            if keys:
                self.redis.delete(*keys)
            if cursor == 0:
                break