import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))


from src.views.pages.facebook.facebook_action import FacebookAction

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Facebook Action UI")
        self.resize(600, 450)

        # Tạo Widget trung tâm và Layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Khởi tạo và thêm Widget bạn vừa code vào giao diện
        self.fb_action_widget = FacebookAction()
        layout.addWidget(self.fb_action_widget)

        # 2. Thêm một nút bấm để test việc lấy dữ liệu
        self.btn_get_value = QPushButton("In kết quả get_value() ra Console")
        self.btn_get_value.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        layout.addWidget(self.btn_get_value)
        
        layout.addStretch() # Đẩy các thành phần lên trên cùng

        # Kết nối sự kiện click của nút với hàm in kết quả
        self.btn_get_value.clicked.connect(self.print_action_data)

    def print_action_data(self):
        """Lấy dữ liệu từ widget và in ra console với định dạng JSON đẹp mắt"""
        data = self.fb_action_widget.get_value()
        
        print("\n" + "="*40)
        print("DỮ LIỆU GET_VALUE() TRẢ VỀ:")
        print("="*40)
        if not data:
            print("Chưa chọn Action nào!")
        else:
            # In ra dạng JSON để dễ nhìn
            print(json.dumps(data, indent=4, ensure_ascii=False))
        print("="*40 + "\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())