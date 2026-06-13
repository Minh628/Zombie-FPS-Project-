# engine_setup.py - Cấu hình hệ thống và dọn dẹp cache trước khi khởi tạo Ursina
import os
import shutil
from panda3d.core import loadPrcFileData

def setup_engine_configs():
    """Hàm khởi tạo các cấu hình hệ thống cấp thấp trước khi game bắt đầu."""
    
    # 1. Dọn dẹp cache cũ (nếu có) để tránh xung đột
    cache_dir = 'models_compressed'
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"[Engine] Da tu dong xoa cache '{cache_dir}'.")
        except Exception as e:
            print(f"[Engine] Loi khi xoa cache: {e}")

    # 2. Vô hiệu hóa tính năng tạo file cache .bam của Panda3D
    # Đảm bảo game luôn đọc dữ liệu gốc từ .glb để không bị hỏng màu khi sửa code
    loadPrcFileData('', 'model-cache-dir ')
    
    print("[Engine] Hoan tat cau hinh he thong!")
