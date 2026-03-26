import os
import subprocess
import sqlite3

# ================= CẤU HÌNH =================
MAC_IP = '192.168.1.11'
MAC_USER = 'dinhbinhnguyen' 

MAC_DB_PATH = '/Volumes/KINGSTON/Ext_dev/python/my_manager.repositories/database/database.db'
MAC_IMAGES_BASE_PATH = '/Volumes/KINGSTON/Ext_dev/python/my_manager.repositories/images_product'

WIN_DB_DIR = r'C:\Users\dinhb\Desktop\repositories\db'
WIN_DB_PATH = os.path.join(WIN_DB_DIR, 'database.db')
WIN_IMAGES_BASE_PATH = r'C:\Users\dinhb\Desktop\repositories\images_products'
# ============================================

def run_scp(source, destination, is_dir=False):
    """Hàm chạy lệnh SCP tuần tự"""
    cmd = ['scp']
    if is_dir:
        cmd.append('-r')
    cmd.extend([source, destination])

    print(f"Đang chạy: {' '.join(cmd)}")
    try:
        # Chạy lệnh bình thường, cho phép hiển thị prompt nhập password lên màn hình
        subprocess.run(cmd, check=True)
        print("=> Xong.\n")
    except subprocess.CalledProcessError as e:
        print(f"=> LỖI: {e}\n")

def main():
    os.makedirs(WIN_DB_DIR, exist_ok=True)
    os.makedirs(WIN_IMAGES_BASE_PATH, exist_ok=True)

    # 1. Kéo Database
    print("--- BƯỚC 1: Kéo Database từ Mac ---")
    # Đã bỏ dấu nháy đơn xung quanh đường dẫn MAC
    mac_db_source = f"{MAC_USER}@{MAC_IP}:{MAC_DB_PATH}"
    run_scp(mac_db_source, WIN_DB_DIR)

    if not os.path.exists(WIN_DB_PATH):
        print("Lỗi: Không tìm thấy file Database trên Windows sau khi kéo. Dừng script.")
        return

    # 2. Đọc Database
    print("--- BƯỚC 2: Đọc Database ---")
    conn = sqlite3.connect(WIN_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM RealEstateProducts WHERE status = 1")
        products = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Lỗi truy vấn: {e}")
        conn.close()
        return

    conn.close()

    if not products:
        print("Không có sản phẩm nào có status = 1.")
        return

    print(f"Tìm thấy {len(products)} sản phẩm cần kiểm tra.\n")

    # 3. Đồng bộ Hình ảnh tuần tự
    print("--- BƯỚC 3: Đồng bộ Hình ảnh ---")
    for row in products:
        product_id = str(row[0])
        win_img_dir = os.path.join(WIN_IMAGES_BASE_PATH, product_id)

        if not os.path.exists(win_img_dir):
            print(f"--- Đang xử lý [ID: {product_id}] ---")
            # Đã bỏ dấu nháy đơn xung quanh đường dẫn MAC
            mac_img_source = f"{MAC_USER}@{MAC_IP}:{MAC_IMAGES_BASE_PATH}/{product_id}"
            
            # Quá trình này sẽ dừng lại để chờ bạn nhập mật khẩu cho từng thư mục
            run_scp(mac_img_source, WIN_IMAGES_BASE_PATH, is_dir=True)
        else:
            print(f"[ID: {product_id}] Đã có sẵn. Bỏ qua.")

    print("\n--- HOÀN TẤT ĐỒNG BỘ ---")

if __name__ == "__main__":
    main()