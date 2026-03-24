# src/drivers/scrcpy/scrcpy_client.py
import os
import shutil
from PySide6.QtCore import QProcess, QObject, Signal, Slot, QProcessEnvironment


class ScrcpyClient(QObject):
    """
    Wrapper for the Scrcpy external process.
    Handles mirroring lifecycle and environment configuration.
    """

    started = Signal(str)
    finished = Signal(str, int)
    error_occurred = Signal(str, str)

    def __init__(self, device_id: str, user_id: int, scrcpy_path="scrcpy", parent=None):
        """Initializes client and resolves scrcpy executable path."""
        super().__init__(parent)
        self.device_id = device_id
        self.user_id = user_id
        resolved = shutil.which(scrcpy_path)
        if not resolved:
            for p in ["/opt/homebrew/bin/scrcpy", "/usr/local/bin/scrcpy"]:
                if os.path.exists(p):
                    resolved = p
                    break
        self.scrcpy_path = resolved or scrcpy_path
        self.process = None

    def start_mirroring(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        """Starts the scrcpy process with grid positioning support."""
        if self.is_running():
            return
        self.process = QProcess(self)
        args = [
            "--serial", self.device_id,
            "--no-audio",
            "--legacy-paste",
            "--max-fps", "30",
            "--stay-awake",
            "--window-title", f"Device: {self.device_id} (User {self.user_id})",
            "--keyboard=uhid",
        ]

        if x is not None:
            args.extend(["--window-x", str(int(x))])
        if y is not None:
            args.extend(["--window-y", str(int(y))])
        if width is not None:
            args.extend(["--window-width", str(int(width))])
        if height is not None:
            args.extend(["--window-height", str(int(height))])

        env = QProcessEnvironment.systemEnvironment()
        adb_path = shutil.which("adb") 
        if adb_path:
            env.insert("ADB", adb_path)
        # adb_path = shutil.which("adb") or "/opt/homebrew/bin/adb"
        # if os.path.exists(adb_path):
        #     env.insert(
        #         "PATH", f"{os.path.dirname(adb_path)}{os.pathsep}{env.value('PATH')}"
        #     )

        self.process.setProcessEnvironment(env)
        self.process.started.connect(lambda: self.started.emit(self.device_id))
        self.process.finished.connect(self._handle_finish)
        self.process.start(self.scrcpy_path, args)

    def is_running(self) -> bool:
        """Checks if the mirroring process is currently active."""
        return (
            self.process is not None
            and self.process.state() == QProcess.ProcessState.Running
        )

    @Slot(int, QProcess.ExitStatus)
    def _handle_finish(self, exit_code, exit_status):
        if self.process:
            self.process.deleteLater()
            self.process = None
            
        self.finished.emit(self.device_id, exit_code)
