# utils\yaml_handler.py
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List

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

class RealEstateConfig:
    def __init__(self, filename: str = "realestate_config.yaml"):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.config_path = self.root_dir / filename
        self.loaded = False

        # --- 1. Real Estate Product Fields ---
        self.transactions: List[str] = []
        self.status: List[str] = []
        self.categories: List[str] = []
        self.provinces: List[str] = []
        self.districts: List[str] = []
        self.wards: List[str] = []
        self.building_lines: List[str] = []
        self.legals: List[str] = []
        self.furniture: List[str] = []
        self.units: List[str] = []

        # --- 2. Contact Fields (Mới) ---
        self.contact_phones: List[str] = []
        self.contact_phone_icons: List[str] = []
        self.contact_names: List[str] = []

        # --- 3. Icons (Mới) ---
        self.icons: List[str] = []

        self.load()

    def load(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f) or {}

                # 1. Load Real Estate Product Data
                re_data = raw_data.get("real_estate_product", {})
                self.transactions = re_data.get("transactions", [])
                self.status = re_data.get("status", [])
                self.categories = re_data.get("categories", [])
                self.provinces = re_data.get("provinces", [])
                self.districts = re_data.get("districts", [])
                self.wards = re_data.get("wards", [])
                self.building_lines = re_data.get("building_lines", [])
                self.legals = re_data.get("legals", [])
                self.furniture = re_data.get("furniture", [])
                self.units = re_data.get("units", [])

                # 2. Load Contact Data
                contact_data = raw_data.get("contact", {})
                self.contact_phones = contact_data.get("phone_number", [])
                self.contact_phone_icons = contact_data.get("phone_icon", [])
                self.contact_names = contact_data.get("name", [])

                # 3. Load Icons
                self.icons = raw_data.get("icons", [])

                self.loaded = True

        except Exception as e:
            raise Exception(f"Failed to load {self.config_path.name}")


realestate_config = RealEstateConfig()
settings = Settings()

