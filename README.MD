# Báo cáo Đồ án: Game Bắn Zombie 3D với Python và Ursina

## 1. Mở đầu

### 1.1. Giới thiệu đề tài
Đề tài là một trò chơi bắn zombie (Zombie FPS) góc nhìn thứ nhất. Người chơi sẽ vào vai một nhân vật sinh tồn, đối mặt với các đợt tấn công của zombie trong một môi trường 3D.

### 1.2. Lý do chọn đề tài
Mục đích chính của việc chọn đề tài này là mong muốn tự tay xây dựng một trò chơi bằng ngôn ngữ lập trình Python nhằm phục vụ nhu cầu giải trí, đồng thời rèn luyện kỹ năng lập trình game và xử lý logic không gian 3D.

### 1.3. Mục đích và mục tiêu của đề tài
Mục tiêu cốt lõi của đề tài là xây dựng thành công một tựa game Python có khả năng hoạt động ổn định và mượt mà trong môi trường đồ họa 3D, ứng dụng được các kiến thức về lập trình hướng đối tượng và xử lý va chạm.

### 1.4. Yêu cầu đồ án
Để hoàn thiện, đồ án cần đáp ứng các yêu cầu sau:
- Xây dựng bản đồ (map) 3D cho trò chơi.
- Hiển thị mô hình zombie, súng và các hiệu ứng hình ảnh liên quan.
- Cho phép người chơi di chuyển, tương tác và chiến đấu trong môi trường 3D.
- Tích hợp hệ thống cấp độ (level) tăng dần độ khó.
- Tích hợp hệ thống vật phẩm (máu, đạn) hỗ trợ người chơi.

---

## 2. Giới thiệu

### 2.1. Ngôn ngữ lập trình Python
Python là ngôn ngữ lập trình bậc cao, dễ đọc, dễ học và phổ biến nhờ hệ sinh thái thư viện khổng lồ. Mặc dù không phải là ngôn ngữ chuyên biệt tối ưu nhất cho game 3D (như C++ hay C#), Python vẫn cho phép phát triển game nhanh chóng và hiệu quả thông qua các engine hỗ trợ.

### 2.2. Thư viện game Ursina Engine
Ursina là một game engine 3D dành cho Python, được xây dựng dựa trên nền tảng Panda3D. Điểm mạnh của Ursina là cú pháp cực kỳ đơn giản, giúp nhà phát triển dễ dàng tạo cửa sổ game, tải mô hình 3D, xử lý ánh sáng và va chạm chỉ với vài dòng code.

### 2.3. Các module chính của Ursina được sử dụng
- **Entity**: Lớp cơ sở để tạo mọi vật thể trong game (người chơi, zombie, đạn, cảnh quan). Cung cấp các thuộc tính như vị trí (`position`), góc quay (`rotation`), và tỷ lệ (`scale`).
- **FirstPersonController**: Module cung cấp sẵn hệ thống điều khiển góc nhìn thứ nhất, giúp xử lý di chuyển và góc nhìn camera một cách tiện lợi.
- **Raycast / BoxCollider / MeshCollider**: Xử lý va chạm vật lý giữa đạn và zombie, hoặc người chơi và môi trường.
- **Audio**: Module quản lý âm thanh (tiếng súng, tiếng zombie, nhạc nền).
- **Text / Button**: Xử lý giao diện người dùng (UI) như hiển thị máu, điểm số và menu trò chơi.

### 2.4. Trò chơi Bắn Zombie
- **Bắt đầu**: Người chơi xuất hiện tại điểm sinh tồn trên bản đồ với vũ khí cơ bản.
- **Tiến trình**: Zombie sẽ spawn (xuất hiện) và di chuyển về phía người chơi. Người chơi cần tiêu diệt chúng để ghi điểm và tồn tại.
- **Lên Level**: Khi tiêu diệt đủ số lượng zombie hoặc sống sót qua một khoảng thời gian nhất định, trò chơi sẽ chuyển sang cấp độ tiếp theo với số lượng và độ trâu của zombie tăng lên.
- **Kết thúc (Game Over)**: Trò chơi kết thúc khi lượng máu của người chơi giảm xuống 0 do bị zombie tấn công.

---

## 3. Tổng quan về đồ án

### 3.1. Phân tích hệ thống

#### 3.1.1. Mục tiêu chung
Xây dựng một hệ thống game modular, dễ bảo trì và dễ mở rộng. Các logic về kết xuất đồ họa, xử lý AI, vật lý và quản lý dữ liệu được tách biệt.

#### 3.1.2. Giới thiệu các Entity/Module chính
- **`main.py`**: Điểm neo của chương trình, chịu trách nhiệm khởi tạo cửa sổ game Ursina, nạp cảnh chơi, và chạy vòng lặp game chính (update loop).
- **`ui/`**: Chứa các đoạn code xử lý giao diện hiển thị cho người chơi (HUD: thanh máu, đạn dược, điểm số, màn hình menu/game over).
- **`entities/`**: Chứa định nghĩa các thực thể trong game (Player, Zombie, Weapon, Bullet, Item). Mỗi thực thể sẽ xử lý logic riêng của nó (ví dụ: Zombie xử lý logic tìm đường và tấn công).
- **`core/`**: Chứa các lớp quản lý luồng trò chơi cốt lõi (GameManager, LevelManager, CollisionSystem), điều phối sự kiện giữa các entity.

#### 3.1.3. Dataflow của hệ thống
- **Input**: Người chơi thao tác qua Chuột và Bàn phím.
- **Xử lý (Core/Entities)**: `FirstPersonController` cập nhật vị trí; `Weapon` sinh ra đạn; `GameManager` kiểm tra va chạm (`Raycast`) giữa đạn và zombie; AI của zombie tính toán đường đi đuổi theo người chơi.
- **Cập nhật dữ liệu**: Máu của zombie giảm, điểm số của người chơi tăng.
- **Output (UI/Audio)**: Giao diện cập nhật điểm số, phát âm thanh bắn súng/zombie chết, cập nhật mô hình 3D trên màn hình.

### 3.2. Sơ đồ chức năng
```text
Zombie-FPS-Project/
│
├── main.py (Khởi động trò chơi)
│
├── core/ (Hệ thống điều phối cốt lõi)
│   ├── game_manager (Quản lý trạng thái game)
│   └── level_manager (Quản lý chuyển màn)
│
├── entities/ (Thực thể 3D)
│   ├── player (Người chơi)
│   ├── zombie (Quái vật)
│   └── weapon (Vũ khí)
│
└── ui/ (Giao diện người dùng)
    ├── hud (Máu, đạn, điểm)
    └── menu (Màn hình chính, Game Over)
```

### 3.3. Thiết kế và Cài đặt

**Các thành phần chứa dữ liệu:**
- **`assets/`**: Thư mục lưu trữ tài nguyên đa phương tiện như mô hình 3D, hình ảnh texture, và âm thanh.
- **`database/`**: Nơi lưu trữ file cấu hình game hoặc lưu trạng thái điểm số cao (high score).
- **`levels/`**: Chứa dữ liệu định nghĩa cho từng màn chơi (tọa độ spawn của zombie, vị trí tường chắn).

#### 3.3.1. Giao diện (UI)
Sử dụng các component UI của Ursina. Giao diện được thiết kế đơn giản, tập trung vào trải nghiệm bắn súng: chữ to rõ, thanh máu và điểm số trực quan, dễ theo dõi.

#### 3.3.2. Cơ sở dữ liệu
Hệ thống lưu trữ đơn giản để theo dõi tiến trình của người chơi, thông số vũ khí, điểm sát thương của từng loại zombie và mức điểm kỷ lục qua các lần chơi.

#### 3.3.3. Cấu trúc vòng lặp game
Sử dụng hàm `update()` làm vòng lặp chính. Mỗi frame sẽ thực hiện:
1. Nhận input từ người chơi.
2. Cập nhật vị trí, góc nhìn người chơi.
3. Chạy logic AI của zombie.
4. Kiểm tra và xử lý va chạm vật lý (đạn, người chơi, zombie).
5. Render lại khung hình.

#### 3.3.4. Thuật toán tìm đường của Zombie
Zombie sử dụng thuật toán Vector Hướng cơ bản: Liên tục lấy vị trí của Player, tính toán vector hướng từ zombie đến Player, chuẩn hóa vector và di chuyển dần về phía người chơi thông qua góc xoay (`look_at()`) và di chuyển tới trước.

---

## 4. Đánh giá kết quả
- **Đạt được**: Trò chơi đã khởi chạy thành công, tải được mô hình 3D và môi trường. Người chơi có thể tương tác chơi game bình thường: di chuyển, ngắm bắn, hạ gục zombie, nhặt vật phẩm và thăng cấp (lên level) theo đúng các yêu cầu ban đầu.
- **Hạn chế**: Cần tối ưu thêm thuật toán tìm đường để zombie có thể tránh chướng ngại vật mượt mà hơn.

## 5. Kết luận và Hướng phát triển
Đồ án đã xây dựng thành công một trò chơi bắn súng 3D cơ bản bằng ngôn ngữ Python, áp dụng tốt các khái niệm lập trình và quản lý tài nguyên.

**Hướng phát triển trong tương lai:**
- Bổ sung thêm nhiều bản đồ (map) đa dạng.
- Thêm hệ thống vật phẩm rớt ra phong phú hơn.
- Thiết kế thêm skin cho súng, người chơi và thiết kế các chủng loại zombie mới (như zombie đánh xa, tốc độ cao).
- Cải thiện đồ họa, âm thanh và bổ sung cốt truyện.
