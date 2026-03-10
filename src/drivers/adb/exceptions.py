# src/drivers/adb/exceptions.py
class ADBBaseError(Exception):
    """Base exception for ADB operations."""
    pass

class ADBConnectionError(ADBBaseError):
    """Raised when connection to ADB server or device fails."""
    pass

class ADBCommandError(ADBBaseError):
    """Raised when an ADB command returns a non-zero exit code."""
    def __init__(self, message, stdout=None, stderr=None):
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr

class DeviceNotFoundError(ADBBaseError):
    """Raised when the specified device is not found."""
    pass

class DeviceOfflineError(ADBBaseError):
    """Raised when the device is present but offline."""
    pass
