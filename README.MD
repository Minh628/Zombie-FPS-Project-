🧟‍♂️ Zombie FPS Project (Ursina Engine)

Dự án game bắn súng góc nhìn thứ nhất (FPS) tiêu diệt Zombie, được xây dựng bằng Python và Ursina Engine. Tài liệu này mô tả cấu trúc thư mục tiêu chuẩn, giúp team phân chia công việc dễ dàng và tránh conflict code (xung đột mã nguồn) khi làm việc chung qua Git.

📂 Cấu trúc thư mục (Folder Structure)

zombie_fps_project/
│
├── assets/                 # Nơi chứa toàn bộ tài nguyên tĩnh (Không chứa code)
│   ├── models/             # File 3D (.obj, .gltf, .blend) - VD: zombie.obj, ak47.obj
│   ├── textures/           # Hình ảnh bề mặt (.png, .jpg)
│   ├── sounds/             # Âm thanh (.wav, .mp3) - VD: gunshot.wav
│   ├── fonts/              # Font chữ cho UI
│   └── images/             # Hình ảnh 2D dùng cho UI/HUD
│
├── core/                   # Cấu hình và các logic quản lý hệ thống cốt lõi
│   ├── config.py           # Lưu hằng số (Tốc độ game, độ phân giải, âm lượng,...)
│   ├── engine_setup.py     # Khởi tạo engine Panda3D/Ursina và dọn dẹp cache
│   ├── game_manager.py     # Quản lý state of game (Play, Pause, Game Over)
│   ├── pathfinding.py      # Logic tìm đường cho Zombie (Vector Wall Sliding, A* Breadcrumb)
│   └── utils.py            # Các hàm tính toán dùng chung
│
├── database/               # Logic quản lý Cơ sở dữ liệu (Database)
│   ├── db_manager.py       # Các hàm kết nối, thêm/sửa/xóa (CRUD) dữ liệu
│   └── models.py           # Định nghĩa cấu trúc bảng/Object (VD: Leaderboard, PlayerSave)
│
├── data/                   # Nơi chứa file database thực tế (Không đẩy lên Git)
│   └── save_data.db        # File CSDL SQLite
│
├── entities/               # Các thực thể tương tác trong game
│   ├── player.py           # Kế thừa FirstPersonController, xử lý máu, di chuyển
│   ├── weapon.py           # Lớp cơ sở xử lý súng (raycast, cooldown, nạp đạn)
│   ├── enemies/            # Quản lý kẻ địch
│   │   ├── zombie_base.py  # Class gốc của zombie (AI di chuyển, culling hoạt ảnh)
│   │   ├── zombie_fast.py  # Biến thể zombie chạy nhanh
│   │   └── zombie_boss.py  # Biến thể zombie trùm (Máu trâu, có hoạt ảnh riêng)
│   ├── items/              # Vật phẩm tương tác nhặt được trên bản đồ
│   │   └── ammo_box.py     # Hộp tiếp đạn cứu trợ
│   └── weapons/            # Các loại vũ khí cụ thể kế thừa từ weapon.py
│       ├── ak47.py         # Súng trường tấn công AK47
│       ├── pistol.py       # Súng lục cầm tay
│       └── knife.py        # Dao cận chiến
│
├── ui/                     # Giao diện người dùng
│   ├── ui_manager.py       # Quản lý vòng đời và chuyển cảnh các giao diện UI
│   ├── main_menu.py        # Màn hình bắt đầu game, bảng xếp hạng
│   ├── hud.py              # Overlay trong game (thanh máu người chơi, số đạn, giáp)
│   ├── pause_menu.py       # Trạng thái tạm dừng trò chơi (Resume, Restart, Main Menu)
│   └── game_over_screen.py # Giao diện khi người chơi thua cuộc
│
├── levels/                 # Các màn chơi (Scenes)
│   └── level_01.py         # Set up map, vị trí spawn quái, ánh sáng cho Level 1
│
├── .gitignore              # Bỏ qua các file rác, file DB nội bộ khi đẩy code lên Git
├── requirements.txt        # Liệt kê các thư viện cần cài đặt
├── main.py                 # Entry point: Nơi khởi tạo game và nối các module lại
└── README.md               # Tài liệu dự án (File bạn đang đọc)

🛠 Hướng dẫn chi tiết từng thư mục

1. assets/ (Tài nguyên)

Dành cho Game Designer / 3D Artist / Sound Engineer.

Chỉ chứa file thiết kế, không chứa code Python. Mọi code trong dự án khi gọi tài nguyên đều phải trỏ đường dẫn về đây.

2. database/ & data/ (Cơ sở dữ liệu)

database/db_manager.py: Chứa logic kết nối CSDL. Ví dụ: Dùng sqlite3 để tạo bảng, lưu trữ điểm số cao (Highscore), hoặc trạng thái máu/vũ khí hiện tại của người chơi.

data/: Thư mục này chỉ để ở local máy mỗi người, chứa các file .db hoặc .json. Nhớ thêm thư mục này vào .gitignore.

3. entities/ (Thực thể)

Nơi làm việc chính của Gameplay Developer.

Mỗi vật thể sống hoặc tương tác được trong game (Player, Súng, Quái vật, Hộp tiếp đạn) đều là một Class riêng biệt kế thừa từ Entity của Ursina.
Các vũ khí cụ thể nằm trong thư mục `weapons/` kế thừa từ `weapon.py`, còn vật phẩm nằm trong `items/`.

4. ui/ (Giao diện)

Dành cho UI/UX Developer.

Chứa các màn hình hiển thị trong game. `ui_manager.py` sẽ chịu trách nhiệm bật tắt và chuyển đổi trạng thái giữa `main_menu.py`, `hud.py`, `pause_menu.py`, và `game_over_screen.py`.
File hud.py sẽ giao tiếp với player.py để cập nhật thanh máu và đạn lên màn hình thông qua các hàm Observer/Callback.

