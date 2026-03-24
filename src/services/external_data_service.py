# src/services/external_data_service.py
import os
import re
import random
from typing import List, Optional, Dict, Any

from src.repositories.external_data_repo import ExternalDataRepository
from src.entities import RealEstateProduct, RealEstateTemplateType
from src.utils.mapper import enrich_real_estate_product
from src.utils.logger import logger
from src.utils.yaml_handler import realestate_config

SETTING_FIELD_MAP: Dict[str, str] = {
    "transaction_type": "transactions",
    "status": "status",
    "category": "categories",
    "province": "provinces",
    "district": "districts",
    "ward": "wards",
    "building_line": "building_lines",
    "legal": "legals",
    "furniture": "furniture",
}


class ExternalDataService:
    """
    Service layer for managing external real estate data operations.
    Handles product retrieval, content generation through template processing, 
    and image resource management.
    """
    def __init__(self, repository: ExternalDataRepository):
        self.repo = repository
        self.image_container_dir = repository.image_container_dir

    def get_all_products_raw(self) -> List[RealEstateProduct]:
        """
        Retrieves all real estate products in their raw entity format.
        """
        return self.repo.get_all_products()

    def get_all_products_display(self) -> List[Dict[str, Any]]:
        """
        Retrieves all real estate products enriched with display-friendly values.
        """
        products = self.repo.get_all_products()
        return [enrich_real_estate_product(p) for p in products]

    def get_product_pids(self) -> List[str]:
        """
        Retrieves a list of all available Product IDs (PIDs).
        """
        return self.repo.get_all_pid()

    def get_product_details(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves details for a specific product by its PID and enriches it for display.
        """
        product = self.repo.get_one_product(pid)
        if product:
            return enrich_real_estate_product(product)
        return None

    def get_random_product_for_posting(
        self, transaction_type: int, days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Selects a random product updated within a specific timeframe for social media posting.
        """
        product = self.repo.get_one_recent_product(transaction_type, days)
        if product:
            logger.info(f"Selected random product: {product.pid} ({product.street})")
            return enrich_real_estate_product(product)

        logger.warning(
            f"No recent product found for transaction type {transaction_type} in last {days} days."
        )
        return None

    def get_random_pid(self) -> Optional[str]:
        """
        Retrieves a random PID from the most recent products.
        """
        product = self.repo.get_one_recent_product(transaction_type=0, recent_day=7)
        if not product:
            logger.warning("No recent product found.")
            return None
        return product.pid

    def get_smart_template(
        self, transaction_type: int, category: int, part: int
    ) -> Optional[RealEstateTemplateType]:
        """
        Finds the most suitable template based on transaction type and category, 
        falling back to default if necessary.
        """
        template = self.repo.get_random_template(transaction_type, category, part)

        if template:
            return template
        logger.info(
            f"Specific template not found for cat {category}, falling back to default."
        )
        return self.repo.get_default_template(transaction_type, part)

    def generate_content_for_product(
        self, product_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates final Title and Description for a product by processing templates 
        and replacing dynamic tags with actual product data.
        """
        trans_type = product_dict.get("transaction_type")
        cat = product_dict.get("category")

        title_tmpl_obj = self.get_smart_template(trans_type, cat, part=0) # type: ignore
        desc_tmpl_obj = self.get_smart_template(trans_type, cat, part=1) # type: ignore

        raw_title = title_tmpl_obj.value if title_tmpl_obj else ""
        raw_desc = desc_tmpl_obj.value if desc_tmpl_obj else ""

        final_title = self._process_template_replacement(raw_title, product_dict).upper()
        final_desc = self._process_template_replacement(raw_desc, product_dict)

        return {
            "title": final_title,
            "description": f"{final_title}\n\n{final_desc}",
            "image_paths": [],
        }

    def generate_content_by_pid(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        Orchestrates the full content generation flow: retrieves product data, 
        processes templates, and identifies associated image paths.
        """
        product_dict = self.get_product_details(pid)
        if not product_dict:
            logger.warning(f"Product PID {pid} not found via generate_content_by_pid.")
            return None

        result = self.generate_content_for_product(product_dict)
        
        product_id = product_dict.get("id")
        img_dir = os.path.join(
            self.image_container_dir, str(product_id), f"logo_{product_id}"
        )
        result["image_paths"] = self.get_images_from_folder(img_dir)

        return result

    def _process_template_replacement(
        self, template: str, product_dict: Dict[str, Any]
    ) -> str:
        """
        Core logic for parsing template tags and replacing them with product data.
        Supports configuration mapping, numeric formatting, and randomized icon insertion.
        """
        if not template:
            return ""

        replacements: Dict[str, str] = {}

        def safe_float(val):
            if val is None or val == "":
                return "0"
            try:
                f = float(val)
                return f"{f:g}"
            except:
                return "0"

        def get_config_text(cfg_list, idx):
            try:
                if idx is None or int(idx) < 0:
                    return ""
                return cfg_list[int(idx)]
            except (IndexError, TypeError, ValueError):
                return str(idx) if idx is not None else ""

        for attr_name, config_list_name in SETTING_FIELD_MAP.items():
            attr_val = product_dict.get(attr_name)
            config_list = getattr(realestate_config, config_list_name, [])

            text_val = get_config_text(config_list, attr_val)

            if attr_name in ["ward", "district", "province"]:
                text_val = text_val.title()

            replacements[f"<{attr_name}>"] = text_val

        replacements["<pid>"] = str(product_dict.get("pid") or "")
        replacements["<street>"] = str(product_dict.get("street") or "").title()
        replacements["<description>"] = str(product_dict.get("description") or "")
        replacements["<function>"] = str(product_dict.get("function") or "")

        replacements["<area>"] = safe_float(product_dict.get("area"))
        replacements["<price>"] = safe_float(product_dict.get("price"))
        replacements["<structure>"] = safe_float(product_dict.get("structure"))

        replacements["<unit>"] = (
            realestate_config.units[0] if realestate_config.units else ""
        )

        phone = (
            realestate_config.contact_phones[0]
            if realestate_config.contact_phones
            else ""
        )
        name = (
            realestate_config.contact_names[0]
            if realestate_config.contact_names
            else ""
        )
        phone_icon = (
            realestate_config.contact_phone_icons[0]
            if realestate_config.contact_phone_icons
            else phone
        )

        replacements["<phone_number>"] = phone
        replacements["<name>"] = name
        replacements["<phone_number_icon>"] = phone_icon

        final_content = template
        for tag, val in replacements.items():
            final_content = final_content.replace(tag, str(val))

        icons_list = realestate_config.icons
        if icons_list:
            def random_icon_replacer(match):
                return random.choice(icons_list)

            final_content = re.sub(r"<icon>", random_icon_replacer, final_content)
        else:
            final_content = final_content.replace("<icon>", "")
        return final_content.strip()

    def get_images_from_folder(self, folder_path: str) -> List[str]:
        """
        Scans a directory for valid image files and returns their full paths sorted by name.
        """
        normalized_path = os.path.abspath(os.path.normpath(folder_path))

        if not os.path.exists(normalized_path):
            logger.warning(f"❌ Image folder not found: {normalized_path}")
            return []

        valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"}
        image_paths = []

        try:
            for filename in os.listdir(normalized_path):
                if filename.startswith("."):
                    continue

                ext = os.path.splitext(filename)[1].lower()
                if ext in valid_extensions:
                    full_path = os.path.join(normalized_path, filename)
                    image_paths.append(full_path)

            image_paths.sort()
            return image_paths

        except Exception as e:
            logger.error(f"Error scanning image folder {normalized_path}: {e}")
            return []