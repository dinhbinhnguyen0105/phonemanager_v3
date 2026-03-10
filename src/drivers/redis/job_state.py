# src/drivers/redis/job_state.py

import json
from typing import Optional, Dict, Any
from src.drivers.redis.base_state import BaseState


class JobState(BaseState):
    """
    Manages the lifecycle and state of background jobs in Redis.
    Handles queuing of pending jobs and storage of task execution results.
    """
    
    def __init__(self, redis_client):
        super().__init__(redis_client, namespace='farm:job')
        
    def push_job(self, job_data: Dict[str, Any]) -> None:
        """
        Pushes a new job into the pending queue for workers to process.
        
        :param job_data: Dictionary containing job details (e.g., job_id, action, target).
        """
        job_json = json.dumps(job_data)
        self.redis.lpush(self._key("pending:queue"), job_json)
        
    def pop_job(self, timeout: int = 2) -> Optional[Dict[str, Any]]:
        """
        Blocks and waits to retrieve a job from the pending queue.
        
        :param timeout: Time in seconds to wait before returning None.
        :return: A dictionary containing the job data, or None if no job is available.
        """
        result = self.redis.brpop(self._key("pending:queue"), timeout=timeout)
        if result:
            # result[0] is the key, result[1] is the job_json
            _, job_json = result
            return json.loads(job_json)
        return None
        
    def set_job_result(self, job_id: str, success: bool, log: str = "") -> None:
        """
        Stores the execution result of a job so it can be retrieved by the UI or services.
        
        :param job_id: The unique identifier of the job.
        :param success: Boolean indicating whether the job was successful.
        :param log: Optional descriptive log or error message regarding the execution.
        """
        self.hset_dict(f"result:{job_id}", {
            "success": success,
            "log": log
        })