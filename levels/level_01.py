# level_01.py - Set up map, vị trí spawn quái, ánh sáng, hệ thống wave cho Level 1
# Tối ưu: Object Pooling - Khởi tạo sẵn zombie vào RAM, tái sử dụng thay vì destroy/new
from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random
from core.config import (
    SOUNDS_DIR
)


class Level01:
    """
    Level 1 - Thiết lập map, ánh sáng, vị trí spawn zombie.
    Tự quản lý hệ thống wave: spawn zombie, đếm wave, chuyển wave.
    Map 3D chỉ load 1 lần duy nhất, khi chơi lại chỉ reset wave.
    Tối ưu: Object Pooling cho zombie (40 Normal + 20 Fast pre-allocated).
    """

    def __init__(self):
        self.spawn_points = []
        self.entities = []
        self.ammo_boxes = []

        # --- Hệ thống Wave & Object Pool ---
        self.active_zombies = []
        self.zombie_pool = []       # Mảng quản lý tổng thể Object Pool
        self.wave = 1
        self.zombies_per_wave = 5
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = self.zombies_per_wave
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.is_wave_transitioning = False
        self.wave_transition_timer = 0
        self.is_running = False
        self.player = None
        self.boss_spawned_this_wave = False

        # Âm thanh qua 1 wave
        self.congratulations_sound = Audio(f'{SOUNDS_DIR}/congratulations.mp3', autoplay=False, loop=False)
        self.congratulations_sound.volume = 0.8

        # Callbacks → GameManager lắng nghe
        self.on_zombie_killed = None     # (points) → cộng điểm
        self.on_wave_start = None        # (wave_number) → cập nhật HUD
        self.on_wave_complete = None     # (wave_number) → thông báo

        # Load map 1 lần duy nhất
        self._setup_environment()
        self._setup_lighting()
        self._setup_spawn_points()
        self._create_zombie_pool()   # Đúc sẵn quái vào RAM

    # ==============================================================
    # OBJECT POOL: Khởi tạo sẵn zombie vào bộ nhớ
    # ==============================================================

    def _create_zombie_pool(self):
        """Khởi tạo sẵn một lực lượng quái nhàn rỗi nằm ngầm dưới map."""
        from entities.enemies.zombie_base import ZombieBase
        from entities.enemies.zombie_fast import ZombieFast
        from entities.enemies.zombie_boss import ZombieBoss

        # Tạo sẵn 40 Normal Zombie và 20 Fast Zombie ẩn dưới map
        for _ in range(40):
            z = ZombieBase(position=Vec3(0, -999, 0))
            z.despawn()
            self.zombie_pool.append(z)

        for _ in range(20):
            z = ZombieFast(position=Vec3(0, -999, 0))
            z.despawn()
            self.zombie_pool.append(z)

        for _ in range(5):
            z = ZombieBoss(position=Vec3(0, -999, 0))
            z.despawn()
            self.zombie_pool.append(z)

    def _get_zombie_from_pool(self, is_fast=False, is_boss=False):
        """Tìm một thực thể đang rảnh trong pool phù hợp với chủng loại yêu cầu."""
        from entities.enemies.zombie_fast import ZombieFast
        from entities.enemies.zombie_boss import ZombieBoss

        for zombie in self.zombie_pool:
            if not zombie.enabled:  # Kiểm tra trạng thái rảnh (đã despawn)
                if is_boss and isinstance(zombie, ZombieBoss):
                    return zombie
                elif is_fast and isinstance(zombie, ZombieFast):
                    return zombie
                elif not is_boss and not is_fast and not isinstance(zombie, ZombieFast) and not isinstance(zombie, ZombieBoss):
                    return zombie
        return None

    # ==============================================================
    # MAP SETUP (chỉ gọi 1 lần trong __init__)
    # ==============================================================

    def _setup_environment(self):
        """Tạo môi trường map Level 1."""
        mapOBJ = Entity(
            model='assets/models/map/obj/map.obj', collider='mesh',
            position=Vec3(0, 0, 0),
        )
        mapOBJ.visible = False      # Set AFTER creation so it applies once the model is loaded
        mapOBJ.color = color.rgba(0, 0, 0, 0)  # Fully transparent fallback (keeps collider active)

        mapGLTF = Entity(
            model='assets/models/map/gltf/map.gltf',
            rotation=Vec3(0, 180, 0),
            shader=lit_with_shadows_shader,
            metallic=0.2,
            roughness=0.8,
        )
        mapGLTF.position = Vec3(0, 0, 0)

        self.sky = Sky()
        self.entities.append(self.sky)

    def _setup_lighting(self):
        """Thiết lập ánh sáng tối ưu cho không gian 3D."""
        sun = DirectionalLight(y=2, z=3, shadows=True)
        sun.shadow_map_resolution = (2048, 2048)  # Tùy chỉnh để bóng mượt hơn
        sun.look_at(Vec3(1, -5, -2))

        # AmbientLight: Màu nhẹ để giữ độ tương phản, tạo độ sâu
        AmbientLight(color=color.rgba(80, 80, 80, 255))
        self.entities.append(sun)

    def _setup_spawn_points(self):
        """Định nghĩa các điểm spawn zombie."""
        self.spawn_points = [
            Vec3(46, 0, -32),
            Vec3(-69, 0, -30),
            Vec3(63, 0, -9)
        ]

    # ==============================================================
    # RESET LEVEL (tái sử dụng map, chỉ reset wave)
    # ==============================================================

    def reset_level(self, player):
        """
        Khởi tạo lại trạng thái wave mà KHÔNG load lại Map 3D.
        Gọi hàm này thay vì cleanup() + Level01() khi chơi lại.
        """
        self.clear_zombies()
        self.player = player
        self.wave = 1
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = self.zombies_per_wave
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.is_wave_transitioning = False
        self.wave_transition_timer = 0
        self.is_running = True
        self.boss_spawned_this_wave = False
        self._spawn_ammo_boxes()

    def stop_waves(self):
        """Dừng hệ thống wave."""
        self.is_running = False
        self.clear_zombies()
        self.clear_ammo_boxes()

    # ==============================================================
    # HỆ THỐNG WAVE (Level tự xử lý)
    # ==============================================================

    def update_waves(self):
        """Cập nhật wave/spawn mỗi frame. Gọi bởi GameManager."""
        if not self.is_running or not self.player:
            return
        self._update_spawn()
        self._check_wave_complete()

    def _update_spawn(self):
        """Logic spawn zombie."""
        if self.is_wave_transitioning:
            self.wave_transition_timer -= time.dt
            if self.wave_transition_timer <= 0:
                self._next_wave()
            return

        if self.zombies_spawned_this_wave >= self.zombies_to_spawn:
            return

        self.spawn_timer -= time.dt
        if self.spawn_timer <= 0:
            self._spawn_zombie()
            self.spawn_timer = self.spawn_interval

    def _spawn_zombie(self):
        """Spawn zombie từ Object Pool thay vì khởi tạo mới từ đĩa."""
        if not self.player:
            return

        spawn_pos = random.choice(self.spawn_points)
        spawn_pos = Vec3(
            spawn_pos.x + random.uniform(-2, 2 ), 1,
            spawn_pos.z + random.uniform(-2, 2)
        )

        # Xác định loại zombie cần gọi
        want_boss = False
        if self.wave % 2 == 0 and not getattr(self, 'boss_spawned_this_wave', False):
            want_boss = True
            self.boss_spawned_this_wave = True
            
        want_fast = False
        if not want_boss:
            want_fast = (self.wave >= 1 and random.random() < 0.5)

        # Lấy quái từ pool RAM
        zombie = self._get_zombie_from_pool(is_fast=want_fast, is_boss=want_boss)

        # Nếu pool hết quái dự trữ, đúc khẩn cấp (fallback)
        if not zombie:
            from entities.enemies.zombie_base import ZombieBase
            from entities.enemies.zombie_fast import ZombieFast
            from entities.enemies.zombie_boss import ZombieBoss
            if want_boss:
                zombie = ZombieBoss(position=spawn_pos, player=self.player)
            elif want_fast:
                zombie = ZombieFast(position=spawn_pos, player=self.player)
            else:
                zombie = ZombieBase(position=spawn_pos, player=self.player)
            self.zombie_pool.append(zombie)

        # Thiết lập callback và kích hoạt từ pool
        zombie.on_death = self._on_zombie_death
        zombie.spawn_from_pool(spawn_pos, self.player)

        self.active_zombies.append(zombie)
        self.zombies_spawned_this_wave += 1

    def _on_zombie_death(self, zombie):
        """Callback khi zombie chết → thông báo lên GameManager."""
        from entities.enemies.zombie_fast import ZombieFast
        from entities.enemies.zombie_boss import ZombieBoss
        if isinstance(zombie, ZombieBoss):
            points = 500
        elif isinstance(zombie, ZombieFast):
            points = 150
        else:
            points = 100

        if zombie in self.active_zombies:
            self.active_zombies.remove(zombie)

        if self.on_zombie_killed:
            self.on_zombie_killed(points)

    def _check_wave_complete(self):
        """Kiểm tra wave đã hoàn thành chưa."""
        if self.is_wave_transitioning:
            return
        if (self.zombies_spawned_this_wave >= self.zombies_to_spawn
                and len(self.active_zombies) == 0
                and self.zombies_to_spawn > 0):
            self.is_wave_transitioning = True
            self.wave_transition_timer = 5.0
            self.congratulations_sound.play()
            if self.on_wave_complete:
                self.on_wave_complete(self.wave)

    def _next_wave(self):
        """Chuyển sang wave tiếp theo."""
        self.wave += 1
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = self.zombies_per_wave + (self.wave - 1) * 3
        self.spawn_timer = 0
        self.spawn_interval = max(1.0, 3.0 - (self.wave - 1) * 0.3)
        self.is_wave_transitioning = False
        self.boss_spawned_this_wave = False
        if self.on_wave_start:
            self.on_wave_start(self.wave)
        self._spawn_ammo_boxes()

    def clear_zombies(self):
        """Trả tất cả zombie về pool (despawn) thay vì destroy."""
        for zombie in self.active_zombies[:]:
            if zombie:
                zombie.despawn()
        self.active_zombies.clear()

    def clear_ammo_boxes(self):
        """Xóa tất cả hộp đạn."""
        for box in self.ammo_boxes:
            if box:
                destroy(box)
        self.ammo_boxes.clear()

    def _spawn_ammo_boxes(self):
        """Spawn hộp đạn ở đầu mỗi wave."""
        self.clear_ammo_boxes()
        from entities.items.ammo_box import AmmoBox

        positions = [
            Vec3(36, 1, -11),
            Vec3(36, 1, 31),
            Vec3(-18, 1, -21),
            Vec3(-37, 1, 16)
        ]

        for pos in positions:
            box = AmmoBox(position=pos, player=self.player)
            self.ammo_boxes.append(box)
            if box not in self.entities:
                self.entities.append(box)

    def cleanup(self):
        """Hủy diệt thật sự khi thoát màn game - destroy cả pool."""
        self.clear_zombies()
        self.clear_ammo_boxes()
        # Destroy toàn bộ pool khi thoát game thật sự
        for zombie in self.zombie_pool:
            destroy(zombie)
        self.zombie_pool.clear()
        for entity in self.entities:
            destroy(entity)
        self.entities.clear()
        self.is_running = False
