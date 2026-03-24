import sys
import json
from PySide6.QtCore import QCoreApplication
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

# Đảm bảo import đúng cấu trúc thư mục của project
from src.repositories.external_data_repo import ExternalDataRepository
from src.services.external_data_service import ExternalDataService
from src.controllers.external_data_controller import ExternalDataController

def run_tests():
    # 1. Khởi tạo QCoreApplication (Bắt buộc để các Signal của QObject hoạt động)
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication(sys.argv)

    print("="*50)
    print("🚀 KHỞI TẠO EXTERNAL DATA CONTROLLER")
    print("="*50)
    
    # 2. Khởi tạo các Layers: Repo -> Service -> Controller
    repo = ExternalDataRepository()
    service = ExternalDataService(repo)
    controller = ExternalDataController(service)

    # 3. Lắng nghe các Signal từ Controller (Nếu có lỗi, nó sẽ in ra đây)
    controller.error_occurred.connect(lambda err: print(f"❌ [SIGNAL ERROR]: {err}"))
    controller.msg_signal.connect(lambda msg: print(f"💬 [SIGNAL MSG]: {msg}"))

    # ==========================================
    # TEST 1: Lấy toàn bộ sản phẩm (đã format)
    # ==========================================
    print("\n[TEST 1] get_all_products_display()...")
    all_products = controller.get_all_products_display()
    print(f"-> Tổng số sản phẩm lấy được: {len(all_products)}")
    if all_products:
        # Chỉ in sản phẩm đầu tiên ra để tránh làm rác màn hình
        print(f"-> Mẫu sản phẩm đầu tiên:\n{json.dumps(all_products[0], indent=4, ensure_ascii=False)}")

    # ==========================================
    # TEST 2: Lấy danh sách PID
    # ==========================================
    print("\n[TEST 2] get_product_pids()...")
    pids = controller.get_product_pids()
    print(f"-> Tổng số PIDs lấy được: {len(pids)}")
    if pids:
        print(f"-> 5 PIDs đầu tiên: {pids[:5]}")

    # Lấy 1 PID ngẫu nhiên làm mẫu để test các hàm dưới
    sample_pid = pids[0] if pids else None

    # ==========================================
    # TEST 3: Lấy chi tiết một sản phẩm
    # ==========================================
    print(f"\n[TEST 3] get_product_details(pid='{sample_pid}')...")
    if sample_pid:
        details = controller.get_product_details(sample_pid)
        print(f"-> Chi tiết sản phẩm:\n{json.dumps(details, indent=4, ensure_ascii=False)}")
    else:
        print("-> ⚠️ Bỏ qua vì Database không có PID nào.")

    # ==========================================
    # TEST 4: Lấy sản phẩm ngẫu nhiên để đăng bài
    # ==========================================
    # Giả sử transaction_type = 0 (Bán) hoặc 1 (Cho thuê), hãy thay số này cho phù hợp với DB của bạn
    transaction_type_test = 0 
    print(f"\n[TEST 4] get_random_product_for_posting(transaction_type={transaction_type_test}, days=30)...")
    random_prod = controller.get_random_product_for_posting(transaction_type=transaction_type_test, days=30)
    if random_prod:
        print(f"-> Đã chọn sản phẩm: PID = {random_prod.get('pid')}, Đường = {random_prod.get('street', 'N/A')}")
    else:
        print("-> ⚠️ Không tìm thấy sản phẩm nào được cập nhật trong 30 ngày qua.")

    # ==========================================
    # TEST 5: Lấy PID ngẫu nhiên
    # ==========================================
    print("\n[TEST 5] get_random_pid()...")
    random_pid = controller.get_random_pid()
    print(f"-> PID ngẫu nhiên lấy được: {random_pid}")

    # ==========================================
    # TEST 6: Sinh nội dung đăng bài (Tự ráp template + Load ảnh)
    # ==========================================
    target_pid = random_pid or sample_pid
    print(f"\n[TEST 6] generate_content_by_pid(pid='{target_pid}')...")
    if target_pid:
        content = controller.generate_content_by_pid(target_pid)
        print("-> Nội dung bài đăng (Title, Description, Images) được sinh ra:")
        print(json.dumps(content, indent=4, ensure_ascii=False))
    else:
        print("-> ⚠️ Bỏ qua vì không có PID nào để test.")

    print("\n" + "="*50)
    print("✔️  HOÀN THÀNH TEST EXTERNAL DATA CONTROLLER")
    print("="*50)

if __name__ == "__main__":
    run_tests()