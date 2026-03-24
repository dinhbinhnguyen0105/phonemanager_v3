# worker\generic_worker.py
from PySide6.QtCore import QThread, Signal
from typing import Callable, Any
from src.utils.logger import logger

class GenericWorker(QThread):
    success = Signal(str, object) # worker name, result
    error = Signal(str, str) # worker name, error message

    def __init__(self, task_name: str, target_func: Callable, *args, **kwargs):
        super().__init__()
        self.task_name = task_name
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logger.info(f"Starting worker: {self.task_name}")
        try:
            results = self.target_func(*self.args, **self.kwargs)
            self.success.emit(self.task_name, results)
        except Exception as e:
            self.error.emit(self.task_name, str(e))