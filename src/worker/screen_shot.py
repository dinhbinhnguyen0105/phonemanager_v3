from PySide6.QtCore import QObject, Signal, QRunnable
from src.drivers.adb.adb_controller import ADBController

class ScreenshotSignals(QObject):
    """
    Defines the signals available for a ScreenshotTask.
    
    Since QRunnable is not a QObject and cannot emit signals directly, 
    this class acts as a dedicated signal proxy.
    """
    success = Signal(str, str)  # device_id, local_path
    error = Signal(str, str)    # device_id, error_message


class ScreenshotTask(QRunnable):
    """
    An isolated screenshot task designed to run within a QThreadPool.
    
    Each task instance operates on its own thread to execute ADB commands,
    preventing UI freezes and handling multiple device captures concurrently.
    """
    def __init__(self, device_id: str, output_dir: str):
        """
        Initializes the task with target device and destination directory.

        Args:
            device_id (str): The unique identifier of the Android device.
            output_dir (str): The local directory where the screenshot will be saved.
        """
        super().__init__()
        self.device_id = device_id
        self.output_dir = output_dir
        self.signals = ScreenshotSignals()

    def run(self):
        """
        Executes the screenshot logic.
        
        Instantiates a local ADBController to ensure thread safety and avoid 
        race conditions during concurrent ADB operations.
        """
        try:            
            adb_controller = ADBController(self.device_id)
            local_path = adb_controller.take_screenshot(self.output_dir)
            
            if local_path:
                self.signals.success.emit(self.device_id, local_path)
            else:
                self.signals.error.emit(self.device_id, "Screenshot function returned an empty path.")
        except Exception as e:
            self.signals.error.emit(self.device_id, str(e))