# src/services/external_data_service.py
import os
import sys
import re
import random
from typing import List, Optional, Dict, Any
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from src.repositories.external_data_repo import ExternalDataRepository
from src.entities import (
    RealEstateProduct, 
    RealEstateTemplate, 
    RealEstateTemplate__Name,
    RealEstateProduct__TransactionType,
    RealEstateProduct__Category
)
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
        product = self.repo.get_one_recent_product(transaction_type=RealEstateProduct__TransactionType.SALE, recent_day=7)
        if not product:
            logger.warning("No recent product found.")
            return None
        return product.pid

    def get_smart_template(
        self, transaction_type: Any, category: Any, template_name: RealEstateTemplate__Name
    ) -> Optional[RealEstateTemplate]:
        """
        Finds the most suitable template based on transaction type and category, 
        falling back to default if necessary.
        """
        template = self.repo.get_random_template(template_name, transaction_type, category)

        if template:
            return template
        logger.info(
            f"Specific template '{template_name.value}' not found for cat {category}, falling back to default."
        )
        return self.repo.get_default_template(template_name, transaction_type, category)

    def generate_content_for_product(
        self, product_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates final Title and Description for a product by processing templates 
        and replacing dynamic tags with actual product data.
        """
        trans_type = product_dict.get("transaction_type")
        cat = product_dict.get("category")

        title_tmpl_obj = self.get_smart_template(trans_type, cat, RealEstateTemplate__Name.TITLE)
        desc_tmpl_obj = self.get_smart_template(trans_type, cat, RealEstateTemplate__Name.DESCRIPTION)

        raw_title = title_tmpl_obj.value if title_tmpl_obj else ""
        raw_desc = desc_tmpl_obj.value if desc_tmpl_obj else ""

        final_title = self._process_template_replacement(raw_title, product_dict).upper()
        final_desc = self._process_template_replacement(raw_desc, product_dict)
        
        footer = "Do tính chất công việc di chuyển ngoài đường thường xuyên, em có thể lỡ tin nhắn trên Facebook. Quý anh/chị vui lòng gọi trực tiếp SDT/ Zalo trên bài đăng giúp em nhé.\n\n------------------------------\n🌺Ký gửi mua, bán - cho thuê, thuê bất động sản xin liên hệ 0375 155 525 - Đ. Bình🌺\n------------------------------\n"
        return {
            "title": final_title,
            "description": f"{final_title}\n\n{final_desc}\n\n{footer}",
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
            self.image_container_dir, str(product_id), f"with_watermark_{product_id}"
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

        for attr_name, config_list_name in SETTING_FIELD_MAP.items():
            text_val = product_dict.get(f"{attr_name}_text") or ""

            if attr_name in ["ward", "district", "province"]:
                text_val = str(text_val).title()

            replacements[f"<{attr_name}>"] = text_val

        replacements["<pid>"] = str(product_dict.get("pid") or "")
        replacements["<street>"] = str(product_dict.get("street") or "").title()
        replacements["<description>"] = str(product_dict.get("description") or "")
        replacements["<function>"] = str(product_dict.get("function") or "")

        replacements["<area>"] = str(product_dict.get("area") or "0")
        replacements["<price>"] = product_dict.get("price_formatted", "0")
        replacements["<structure>"] = str(product_dict.get("structure") or "0")
        replacements["<unit>"] = product_dict.get("unit_text") or ""

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


if __name__ == "__main__":
    import json
    from PySide6.QtCore import QCoreApplication

    # 1. Khởi tạo QCoreApplication (Bắt buộc để QSqlDatabase/SQL Drivers hoạt động)
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication(sys.argv)

    # Khởi tạo repo và service để chạy độc lập
    test_repo = ExternalDataRepository()
    test_service = ExternalDataService(test_repo)

    print("="*50)
    print("🧪 TESTING EXTERNAL DATA SERVICE")
    print("="*50)

    # 1. Lấy danh sách PIDs
    pids = test_service.get_product_pids()
    print(f"[*] Tổng số PID tìm thấy: {len(pids)}")

    if pids:
        sample_pid = pids[0]
        
        # 2. Kiểm tra lấy chi tiết sản phẩm
        print(f"\n[*] Lấy chi tiết sản phẩm PID: {sample_pid}")
        details = test_service.get_product_details(sample_pid)
        if details:
            # In ra 5 keys đầu tiên để kiểm tra
            print(f"-> Thành công. Street: {details.get('street')}, Price: {details.get('price_formatted')}")

        # 3. Kiểm tra sinh nội dung từ Template
        print(f"\n[*] Thử nghiệm sinh nội dung cho PID: {sample_pid}")
        content = test_service.generate_content_by_pid(sample_pid)
        if content:
            print("-" * 30)
            print(f"TITLE:\n{content.get('title')}")
            print(f"\nIMAGES FOUND: {len(content.get('image_paths', []))}")
            print("-" * 30)
            print(f"DESCRIPTION:\n{content.get('description')}")

    else:
        print("[!] Không tìm thấy dữ liệu trong database để test.")

    print("\n" + "="*50)
    