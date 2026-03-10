# utils\yaml_handler.py
import os
import yaml
from pathlib import Path
from typing import Any, Dict

class ConfigNode:
    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigNode(value))
            else:
                setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

class Settings:
    def __init__(self, filename: str = "settings.yaml"):
        self._settings_data = {}
        self.loaded = False
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.setting_path = os.path.join(self.root_dir, filename)
        self.load()
    
    def load(self) -> None:
        if not os.path.exists(self.setting_path):
            raise FileNotFoundError(f"Settings file '{self.setting_path}' not found.")
        try:
            with open(self.setting_path, "r", encoding="utf-8") as file:
                self._settings_data = yaml.safe_load(file) or {}
                self.loaded = True
                for key, value in self._settings_data.items():
                    if isinstance(value, dict):
                        setattr(self, key, ConfigNode(value))
                    else:
                        setattr(self, key, value)
        except Exception as e:
            raise ValueError(f"Error loading settings from '{self.setting_path}': {e}")

    def get_raw(self) -> Dict[str, Any]:
        return self._settings_data

settings = Settings()

