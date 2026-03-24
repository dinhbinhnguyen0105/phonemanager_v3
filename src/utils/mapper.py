from typing import Dict, Any, List
from src.entities import RealEstateProduct
from src.utils.yaml_handler import realestate_config


def get_config_label(data_list: List[str], index: int, default: str = "Unknown") -> str:
    if 0 <= index < len(data_list):
        return data_list[index]
    return f"{default} ({index})"


def enrich_real_estate_product(entity: RealEstateProduct) -> Dict[str, Any]:
    base_data = entity.to_dict()
    filled_data = {
        **base_data,
        "transaction_type_text": get_config_label(
            realestate_config.transactions, entity.transaction_type
        ),
        "status_text": ("Khả dụng" if entity.status else "Không khả dụng"),
        "province_text": get_config_label(realestate_config.provinces, entity.province),
        "district_text": get_config_label(realestate_config.districts, entity.district),
        "ward_text": get_config_label(realestate_config.wards, entity.ward),
        "category_text": get_config_label(
            realestate_config.categories, entity.category
        ),
        "legal_text": get_config_label(realestate_config.legals, entity.legal),
        "building_line_text": get_config_label(
            realestate_config.building_lines, entity.building_line
        ),
        "furniture_text": get_config_label(
            realestate_config.furniture, entity.furniture
        ),
        "price_formatted": f"{entity.price:,.0f}",
        "area_formatted": f"{entity.area} m²",
    }

    return filled_data
