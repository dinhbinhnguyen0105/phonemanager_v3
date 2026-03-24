# track_redis_proxies.py
import time
import os
import sys
from datetime import datetime
from pathlib import Path


# Thêm đường dẫn gốc để có thể import từ src (nếu chạy ở thư mục gốc thì không cần)
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.drivers.redis.redis_manager import RedisStateManager

def clear_screen():
    """Xóa màn hình console cho gọn gàng mỗi lần refresh"""
    os.system('cls' if os.name == 'nt' else 'clear')

def track_proxies():
    try:
        # Lấy client Redis từ Manager của bạn
        client = RedisStateManager.get_client()
        
        # Ping thử xem Redis có đang chạy không
        if not client.ping():
            print("🚨 Không thể kết nối đến Redis Server!")
            return

        while True:
            clear_screen()
            print(f"=== BẢNG THEO DÕI PROXY REDIS REAL-TIME ===")
            print(f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 43)

            # 1. Quét Hàng đợi rảnh rỗi (Pools)
            print("\n🟢 HÀNG ĐỢI RẢNH RỖI (AVAILABLE POOLS):")
            pool_types = ['static', 'api', 'local']
            total_available = 0
            
            for p_type in pool_types:
                pool_key = f"farm:proxy:pool:available:{p_type}"
                count = client.llen(pool_key)
                total_available += count # type: ignore
                print(f"  - {p_type.upper():<10}: {count:>3} proxies")
            
            print(f"  >> Tổng rảnh: {total_available}")

            # 2. Quét Proxy đang làm việc (Working)
            print("\n🔴 PROXY ĐANG LÀM VIỆC (WORKING):")
            working_proxies = client.hgetall("farm:proxy:working")
            if not working_proxies:
                print("  (Không có thiết bị nào đang dùng proxy)")
            else:
                for uuid, serial in working_proxies.items(): # type: ignore
                    # Lấy thêm thông tin IP:Port từ info hash
                    info = client.hgetall(f"farm:proxy:info:{uuid}")
                    host = info.get("host", "N/A") # type: ignore
                    port = info.get("port", "N/A") # type: ignore
                    p_type = info.get("type", "unknown").upper() # type: ignore
                    
                    print(f"  - Thiết bị [{serial}] đang dùng [{p_type}] {host}:{port} (UUID: {uuid[:8]}...)")

            print("\n" + "=" * 43)
            print("Đang theo dõi... Nhấn Ctrl+C để thoát.")
            
            # Tạm dừng 2 giây rồi quét lại
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n👋 Đã thoát trình theo dõi.")
    except Exception as e:
        print(f"\n❌ Lỗi khi đọc Redis: {e}")

if __name__ == "__main__":
    track_proxies()