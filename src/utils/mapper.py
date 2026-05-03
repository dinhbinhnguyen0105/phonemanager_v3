from typing import Dict, Any, List, Optional
from enum import Enum
from src.entities import RealEstateProduct, RealEstateProduct__Unit
from src.utils.yaml_handler import realestate_config


def get_config_label(data_list: List[str], index: int, default: str = "Unknown") -> str:
    if 0 <= index < len(data_list):
        return data_list[index]
    return f"{default} ({index})"


def get_enum_index(enum_member: Any) -> int:
    """Helper to get the index of an enum member for config mapping."""
    if isinstance(enum_member, Enum):
        return list(enum_member.__class__).index(enum_member)
    return -1


def enrich_real_estate_product(entity: RealEstateProduct) -> Dict[str, Any]:
    base_data = entity.to_dict()
    
    # Formatting price based on unit
    unit_text = get_config_label(realestate_config.units, get_enum_index(entity.unit))
    price_val = entity.price
    price_str = ""
    
    if entity.unit == RealEstateProduct__Unit.BILLION:
        # Nếu giá >= 1,000,000 thì coi là VNĐ thô -> cần chia. Ngược lại coi là đã quy đổi (tỷ).
        in_billions = price_val / 1_000_000_000 if price_val >= 1_000_000 else price_val
        price_str = f"{in_billions:g}" # Remove trailing zeros
    elif entity.unit in [RealEstateProduct__Unit.MILLION, RealEstateProduct__Unit.MILLION_PER_MONTH]:
        # Tương tự cho đơn vị triệu
        in_millions = price_val / 1_000_000 if price_val >= 1_000_000 else price_val
        price_str = f"{in_millions:g}"
    else:
        price_str = f"{price_val:,.0f}"

    filled_data = {
        **base_data,
        "street": entity.street.title(),
        "transaction_type_text": get_config_label(
            realestate_config.transactions, get_enum_index(entity.transaction_type)
        ),
        "status_text": get_config_label(
            realestate_config.status, get_enum_index(entity.status)
        ),
        "province_text": get_config_label(
            realestate_config.provinces, get_enum_index(entity.province)
        ),
        "district_text": get_config_label(
            realestate_config.districts, get_enum_index(entity.district)
        ),
        "ward_text": get_config_label(
            realestate_config.wards, get_enum_index(entity.ward)
        ),
        "category_text": get_config_label(
            realestate_config.categories, get_enum_index(entity.category)
        ),
        "legal_text": get_config_label(
            realestate_config.legals, get_enum_index(entity.legal)
        ),
        "building_line_text": get_config_label(
            realestate_config.building_lines, get_enum_index(entity.building_line)
        ),
        "furniture_text": get_config_label(
            realestate_config.furniture, get_enum_index(entity.furniture)
        ),
        "unit_text": unit_text,
        "price_formatted": f"{price_str}",
        "area_formatted": f"{entity.area:g} m²",
    }

    return filled_data
