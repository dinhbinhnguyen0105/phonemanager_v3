import sys
import json
from pathlib import Path
from PySide6.QtCore import QCoreApplication
import contextlib
from typing import Any, Dict, List, Optional

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir)) # Fix: Removed duplicate sys.path.append

# Import core components
# We need to import the actual managers, but their internal dependencies (like repos) will be mocked.
from src.drivers.redis._manager_redis import RedisStateFacade
from src.services._manager_services import ServiceManager
from src.repositories._manager_repositories import RepositoryManager
from src.database.connection import DatabaseManager
from src.controllers._manager_controllers import ControllerManager

# Import the function to be tested and its dependencies
from src.entities import RealEstateProduct # Also need to import Enums for sample_product
from src.constants import (
    Product__Status, RealEstateProduct__TransactionType, RealEstateProduct__Province,
    RealEstateProduct__District, RealEstateProduct__Ward, RealEstateProduct__Category, RealEstateProduct__Unit,
    RealEstateProduct__Legal, RealEstateProduct__BuildingLine, RealEstateProduct__Furniture
)
from src.utils.mapper import enrich_real_estate_product
from src.utils.logger import logger
from src.utils.yaml_handler import realestate_config # To ensure config is loaded

# --- TEST FUNCTION ---
def run_enrich_product_test():
    # 1. Initialize QCoreApplication (if needed for any underlying Qt objects, e.g., signals)
    # ControllerManager and BaseController (which DeviceController, UserController, etc. inherit from)
    # are QObjects and emit signals, so QCoreApplication is necessary.
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication(sys.argv)

    logger.info("="*50)
    logger.info("🚀 KHỞI TẠO HỆ THỐNG ĐỂ TEST enrich_real_estate_product")
    logger.info("="*50)
    
    # Store original ping method to restore it later
    original_redis_ping = None

    try:
        # 2. Khởi tạo Database Manager (thực tế)
        db_manager = DatabaseManager()
        db_manager.init_tables()
        logger.info("Database initialized successfully.")

        # 3. Khởi tạo Repository Manager (thực tế)
        repo_manager = RepositoryManager(db_manager=db_manager)
        logger.info("Repositories initialized successfully.")

        # 4. Khởi tạo Redis State Facade
        redis_facade = RedisStateFacade()
        logger.info("Redis State Facade initialized successfully.")
        
        # Mock the ping method to avoid actual Redis connection if not available
        original_redis_ping = redis_facade.ping
        redis_facade.ping = lambda: True # Buộc ping trả về True để kiểm thử
        
        if redis_facade.ping():
            logger.success("Connected to Redis successfully (mocked).")
        else:
            logger.warning("Failed to connect to Redis. Some Redis-dependent services might not function.")

        # 5. Khởi tạo Service Manager
        service_manager = ServiceManager(repo_manager=repo_manager, redis_facade=redis_facade)
        logger.info("Services initialized successfully.")
        service_manager.init_system() # Call init_system to check Redis connection and repo init

        # 6. Khởi tạo Controller Manager
        controller_manager = ControllerManager(service_manager=service_manager)
        logger.info("Controllers initialized successfully.")

        logger.info("\n" + "="*50)
        logger.info("🧪 BẮT ĐẦU TEST enrich_real_estate_product")
        logger.info("="*50)

        # 7. Lấy một thực thể RealEstateProduct từ DB, hoặc tạo mới nếu không có
        sample_product: RealEstateProduct

        # Cố gắng lấy một sản phẩm ngẫu nhiên để đăng bài (transaction_type=SALE.index, trong 30 ngày gần nhất)
        # get_random_product_for_posting trả về Dict[str, Any], cần chuyển đổi lại thành RealEstateProduct
        random_product_dict = service_manager.external_db.get_random_product_for_posting(
            transaction_type=RealEstateProduct__TransactionType.SALE.index, days=30
        )

        if random_product_dict:
            # Chuyển đổi dictionary đã làm giàu thành đối tượng RealEstateProduct
            # Lưu ý: RealEstateProduct.from_dict cần được triển khai để xử lý các trường Enum
            # Hiện tại, chúng ta sẽ tạo lại đối tượng từ các giá trị thô nếu có thể, hoặc dùng lại logic tạo mẫu.
            sample_product = service_manager.external_db.repo.get_one_product(random_product_dict['pid'])
            logger.info(f"Sử dụng sản phẩm ngẫu nhiên từ DB: PID={sample_product.pid}.")
        else:
            logger.warning("Không tìm thấy sản phẩm nào trong DB. Tạo sản phẩm mẫu mới.")
            sample_product = RealEstateProduct(
                id=None, # DB sẽ tự tạo UUID
                pid="TESTPID001",
                street="Thái Phiên",
                description="Mô tả chi tiết sản phẩm bất động sản mẫu.",
                function="Nhà ở, kinh doanh",
                area=57.5,
                price=4100000000, # 4.1 tỷ
                structure=2.0, # 2 tầng
                transaction_type=RealEstateProduct__TransactionType.SALE,
                status=Product__Status.SELLING, # Corresponds to 'Khả dụng'
                category=RealEstateProduct__Category.TOWNHOUSE,
                province=RealEstateProduct__Province.LAM_DONG,
                district=RealEstateProduct__District.DA_LAT,
                ward=RealEstateProduct__Ward.PHUONG_1,
                building_line=RealEstateProduct__BuildingLine.CAR_ACCESS_ROAD,
                legal=RealEstateProduct__Legal.VI_BANG_PURCHASE,
                furniture=RealEstateProduct__Furniture.NO_FURNITURE,
                unit=RealEstateProduct__Unit.BILLION, # Added unit for the new logic
                created_at=None,
                updated_at=None
            )
            # Chèn sản phẩm mẫu vào DB
            inserted_product = service_manager.external_db.repo.insert(sample_product)
            if inserted_product:
                sample_product = inserted_product # Sử dụng sản phẩm đã được chèn (có UUID)
            
        logger.info(f"Sample RealEstateProduct created: {sample_product}")

        # 8. Gọi hàm enrich_real_estate_product
        enriched_product = enrich_real_estate_product(sample_product)

        logger.info("\n--- KẾT QUẢ enrich_real_estate_product ---")
        logger.info(json.dumps(enriched_product, indent=4, ensure_ascii=False))

        # 9. Thêm các assertion để kiểm tra kết quả
        assert enriched_product["id"] == sample_product.id, f"ID mismatch: Expected {sample_product.id}, got {enriched_product['id']}"
        assert enriched_product["pid"] == sample_product.pid, f"PID mismatch: Expected {sample_product.pid}, got {enriched_product['pid']}"
        assert enriched_product["street"] == sample_product.street.title(), f"Street mismatch: Expected '{sample_product.street.title()}', got '{enriched_product['street']}'"
        
        # Assert for price_formatted based on the new logic
        expected_unit_text = realestate_config.units[sample_product.unit.index]
        expected_price_value = ""
        if sample_product.unit == RealEstateProduct__Unit.BILLION:
            price_in_billions = sample_product.price / 1_000_000_000
            if price_in_billions == int(price_in_billions):
                expected_price_value = f"{int(price_in_billions):,}"
            else:
                expected_price_value = f"{price_in_billions:,.2f}"
        elif sample_product.unit == RealEstateProduct__Unit.MILLION_PER_MONTH:
            price_in_millions = sample_product.price / 1_000_000
            if price_in_millions == int(price_in_millions):
                expected_price_value = f"{int(price_in_millions):,}"
            else:
                expected_price_value = f"{price_in_millions:,.2f}"
        else:
            expected_price_value = f"{sample_product.price:,.0f}"
        
        assert enriched_product["price_formatted"] == f"{expected_price_value} {expected_unit_text}", f"Price formatted mismatch: Expected '{expected_price_value} {expected_unit_text}', got '{enriched_product['price_formatted']}'"
        assert enriched_product["area_formatted"] == f"{sample_product.area:g} m²", f"Area formatted mismatch: Expected {f'{sample_product.area:g} m²'}, got {enriched_product['area_formatted']}"
        assert enriched_product["transaction_type_text"] == realestate_config.transactions[sample_product.transaction_type.index], f"Transaction type text mismatch: Expected {realestate_config.transactions[sample_product.transaction_type.index]}, got {enriched_product['transaction_type_text']}"
        assert enriched_product["status_text"] == realestate_config.status[sample_product.status.index], f"Status text mismatch: Expected {realestate_config.status[sample_product.status.index]}, got {enriched_product['status_text']}"
        assert enriched_product["province_text"] == realestate_config.provinces[sample_product.province.index], f"Province text mismatch: Expected {realestate_config.provinces[sample_product.province.index]}, got {enriched_product['province_text']}"
        assert enriched_product["district_text"] == realestate_config.districts[sample_product.district.index], f"District text mismatch: Expected {realestate_config.districts[sample_product.district.index]}, got {enriched_product['district_text']}"
        assert enriched_product["ward_text"] == realestate_config.wards[sample_product.ward.index], f"Ward text mismatch: Expected {realestate_config.wards[sample_product.ward.index]}, got {enriched_product['ward_text']}"
        assert enriched_product["category_text"] == realestate_config.categories[sample_product.category.index], f"Category text mismatch: Expected {realestate_config.categories[sample_product.category.index]}, got {enriched_product['category_text']}"
        assert enriched_product["legal_text"] == realestate_config.legals[sample_product.legal.index], f"Legal text mismatch: Expected {realestate_config.legals[sample_product.legal.index]}, got {enriched_product['legal_text']}"
        assert enriched_product["building_line_text"] == realestate_config.building_lines[sample_product.building_line.index], f"Building line text mismatch: Expected {realestate_config.building_lines[sample_product.building_line.index]}, got {enriched_product['building_line_text']}"
        assert enriched_product["furniture_text"] == realestate_config.furniture[sample_product.furniture.index], f"Furniture text mismatch: Expected {realestate_config.furniture[sample_product.furniture.index]}, got {enriched_product['furniture_text']}"
        assert enriched_product["unit_text"] == expected_unit_text, f"Unit text mismatch: Expected {expected_unit_text}, got {enriched_product['unit_text']}"
        
        logger.success("✅ enrich_real_estate_product test completed successfully with assertions.")

    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình test: {e}")
    finally:
        # Khôi phục phương thức ping gốc của RedisStateFacade
        if original_redis_ping:
            redis_facade.ping = original_redis_ping
        # Dọn dẹp tài nguyên
        if 'service_manager' in locals():
            service_manager.shutdown()
        logger.info("\n" + "="*50)
        logger.info("✔️  HOÀN THÀNH TEST enrich_real_estate_product")
        logger.info("="*50)

if __name__ == "__main__":
    run_enrich_product_test()