# test_runner.py
import sys
import signal
from PySide6.QtCore import QCoreApplication, QThread, QTimer
from PySide6.QtWidgets import QApplication

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.tasks.scan_device_info import ScanDeviceInfo
from src.entities import Device
from src.utils.logger import logger

class MainThreadTest:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        self.thread = QThread()
        self.worker = ScanDeviceInfo()

        self._setup_thread()
        self._setup_signals()

    def _setup_thread(self):
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.device_info.connect(self.on_process)
        # self.worker.device_disconnected.connect(self.on_device_disconnect)

        
        # Gọi hàm stop khi app chuẩn bị quit
        self.app.aboutToQuit.connect(self.cleanup)

    def _setup_signals(self):
        """Cấu hình để Qt nhận diện được Ctrl+C từ terminal"""
        # Bắt sự kiện Ctrl + C và gọi hàm handle_sigint
        signal.signal(signal.SIGINT, self.handle_sigint)

        # Tạo một QTimer chạy rỗng mỗi 500ms. 
        # Điều này ép vòng lặp C++ của Qt nhường lại quyền xử lý cho Python 
        # trong chốc lát, giúp Python bắt được tín hiệu Ctrl+C.
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)

    def handle_sigint(self, signum, frame):
        """Hàm được gọi khi người dùng nhấn Ctrl+C"""
        logger.info("\n[MAIN THREAD] Nhận được tín hiệu Ctrl+C. Đang đóng ứng dụng...")
        self.app.quit()

    def cleanup(self):
        self.worker.stop()

        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def run(self):
        logger.info("Starting main application...")
        self.thread.start()
        logger.info("Main thread setup complete. Waiting for device events...")
        logger.info("Press Ctrl+C in the console to quit.")
        
        sys.exit(self.app.exec())

    def on_process(self, device_info: Device):
        logger.success(f"[MAIN THREAD] Device connected: {device_info}")

    def on_device_disconnect(self, device_info: Device):
        logger.warning(f"[MAIN THREAD] Device disconnected: {device_info}")

    def on_error(self, message: str):
        logger.error(f"[MAIN THREAD] Worker error: {message}")
        self.app.quit()

if __name__ == "__main__":
    main_app = MainThreadTest()
    main_app.run()