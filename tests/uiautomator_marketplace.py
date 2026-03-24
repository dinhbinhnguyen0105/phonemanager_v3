import os
import sys
from pathlib import Path

# Thêm đường dẫn project vào sys.path để Python nhận diện được thư mục 'src'
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))


from src.entities import Job
from src.constants import Platform, JobAction, JobStatus

# Sửa lại đường dẫn import này cho đúng với vị trí file thực tế của bạn
from src.automation.facebook.actions.list_marketplace_share import run_list_marketplace_share

# ==========================================
# 1. MÔ PHỎNG SIGNAL CỦA PYSIDE6
# ==========================================
class MockLoggerSignal:
    """Lớp giả lập Signal để in log trực tiếp ra Terminal thay vì gửi lên UI"""
    def emit(self, message: str):
        print(f">>> [UI LOG] {message}")


# ==========================================
# 2. HÀM CHẠY TEST
# ==========================================
def test_marketplace_automation():
    # Device ID từ log của bạn
    device_id = "QV70165B11"
    device_id = "3300f6545d72831d"
    
    # Khởi tạo đối tượng Job với UUID và thông tin thực tế
    job = Job(
        uuid='27323a99-deed-4208-a655-2f2f35bd2418',
        name='Automate - SOV36 - fb_list_marketplace_and_share',
        social_uuid='3bcbea75-411d-40cd-9f4d-984e445103e1',
        device_uuid='da95e31d-c6c0-4b7c-9fc6-c64146abc95b',
        user_uuid='5388c2cd-9277-42cf-9111-3cda2c86daeb',
        platform=Platform.FACEBOOK,
        action=JobAction.FB__LIST_MARKETPLACE_AND_SHARE,
        status=JobStatus.PENDING
    )
    
    # Parse payload parameters thành Python Dictionary
    # Lưu ý: Dùng raw string (r"") cho các đường dẫn để tránh lỗi Unicode escape trên Windows
    params = {
        "share_groups_count": 0, 
        "title": "BÁN NHÀ PHỐ 57.5M² THÁI PHIÊN, ĐÀ LẠT GIÁ 4.1 TỶ CÓ 1PK, 1BẾP, 2PN, 2WC", 
        "description": "BÁN NHÀ PHỐ 57.5M² THÁI PHIÊN, ĐÀ LẠT GIÁ 4.1 TỶ CÓ 1PK, 1BẾP, 2PN, 2WC\n\n☀️ Thông tin nhà phố bán 57.5m² Đà Lạt, Lâm Đồng\n🌝 2 tầng, tiện ích 1pk, 1bếp, 2pn, 2wc\n🌼 Bao gồm nội thất cơ bản\n🔥 Pháp lý: 0️⃣3️⃣7️⃣5️⃣ 1️⃣5️⃣5️⃣ 5️⃣2️⃣5️⃣ 🥋\n- Đường ô tô bằng phẳng \n✅Gần các tiện ích ngay trường tiểu học Thái Phiên . Thích hợp cho quý anh chị định cư lâu dài \n🆔: 0efc7d11\n☎ Liên hệ: 0375 155 525 - Đ. Bình", 
        # "image_paths": [
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_0.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_1.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_2.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_3.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_4.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_5.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_6.jpg", 
        #     r"C:\Users\dinhb\Desktop\Dev\python\phonemanager_v3\repositories\images\f45a0449-ff6c-4f67-aff5-0739e54a4475\source_f45a0449-ff6c-4f67-aff5-0739e54a4475\logo_f45a0449-ff6c-4f67-aff5-0739e54a4475_7.jpg"
        # ], 
        "product_id": "0efc7d11"
    }
    
    job.parameters = params
    
    mock_signal = MockLoggerSignal()
    
    print(f"========== BẮT ĐẦU TEST TRÊN THIẾT BỊ {device_id} ==========")
    try:
        # Gọi thẳng vào hàm Automation
        run_list_marketplace_share(device_id, job, mock_signal) # type: ignore
        print("========== TEST KẾT THÚC THÀNH CÔNG ==========")
        
    except Exception as e:
        print(f"========== TEST THẤT BẠI ==========")
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    test_marketplace_automation()