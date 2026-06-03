# level_01.py - Set up map, vị trí spawn quái, ánh sáng, hệ thống wave cho Level 1
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
    """

    def __init__(self):
        self.spawn_points = []
        self.entities = []

        # --- Hệ thống Wave ---
        self.active_zombies = []
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

    # ==============================================================
    # MAP SETUP (chỉ gọi 1 lần trong __init__)
    # ==============================================================


    def _setup_environment(self):
        """Tạo môi trường map Level 1."""

        # ===============================================================
        # ===============================================================

        mapOBJ = Entity(
            model='assets/models/map/obj/map.obj', collider='mesh',
            position=Vec3(0, 0, 0), scale=0.6,
        )
        mapOBJ.visible = False      # Set AFTER creation so it applies once the model is loaded
        mapOBJ.color = color.rgba(0, 0, 0, 0)  # Fully transparent fallback (keeps collider active)

        mapGLTF = Entity(
            model='assets/models/map/gltf/map.gltf',
            rotation = Vec3(0, 180, 0),
            scale=0.6,
            shader=lit_with_shadows_shader,
            metallic=0.2,
            roughness=0.8,
        )
        mapGLTF.position=Vec3(0, 0, 0)

        # ===============================================================
        # ===============================================================

        self.sky = Sky()
        self.entities.append(self.sky)

    def _setup_lighting(self):
        """Thiết lập ánh sáng tối ưu cho không gian 3D."""
        # 1. Tăng độ phân giải bóng để sắc nét hơn (mặc định của Ursina đôi khi hơi thấp)
        sun = DirectionalLight(y=2, z=3, shadows=True)
        sun.shadow_map_resolution = (2048, 2048) # Tùy chỉnh để bóng mượt hơn
        
        # 2. Điều chỉnh hướng nhìn (LookAt)
        # Vec3(1, -1, -1) là ổn, nhưng hãy thử điều chỉnh để bóng đổ dài hơn nếu muốn cảm giác chiều tà/u ám
        sun.look_at(Vec3(1, -5, -2)) 

        # 3. AmbientLight: Để màu nhẹ hơn một chút để giữ độ tương phản
        # Màu (80, 80, 80) sẽ giúp bóng đổ đậm hơn, tạo độ sâu hơn là (100, 100, 100)
        AmbientLight(color=color.rgba(80, 80, 80, 255))
        self.entities.append(sun)
    def _setup_spawn_points(self):
        """Định nghĩa các điểm spawn zombie."""
        self.spawn_points = [
            Vec3(37,0,-39),
            Vec3(-60,0,35),
            Vec3(-71,0,-34)
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

    def stop_waves(self):
        """Dừng hệ thống wave."""
        self.is_running = False
        self.clear_zombies()

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
        """Spawn một zombie."""
        from entities.enemies.zombie_base import ZombieBase
        from entities.enemies.zombie_fast import ZombieFast

        if not self.player:
            return

        spawn_pos = random.choice(self.spawn_points)
        spawn_pos = Vec3(
            spawn_pos.x + random.uniform(-5, 5), 1,
            spawn_pos.z + random.uniform(-5, 5)
        )

        if self.wave >= 1 and random.random() < 0.3:
            zombie = ZombieFast(position=spawn_pos, player=self.player)
        else:
            zombie = ZombieBase(position=spawn_pos, player=self.player)

        zombie.on_death = self._on_zombie_death
        self.active_zombies.append(zombie)
        self.zombies_spawned_this_wave += 1

    def _on_zombie_death(self, zombie):
        """Callback khi zombie chết → thông báo lên."""
        from entities.enemies.zombie_fast import ZombieFast
        points = 150 if isinstance(zombie, ZombieFast) else 100

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
        if self.on_wave_start:
            self.on_wave_start(self.wave)

    def clear_zombies(self):
        """Xóa tất cả zombie."""
        for zombie in self.active_zombies[:]:
            if zombie:
                destroy(zombie)
        self.active_zombies.clear()

    def cleanup(self):
        """Dọn dẹp toàn bộ (chỉ gọi khi thoát game thật sự)."""
        self.clear_zombies()
        for entity in self.entities:
            destroy(entity)
        self.entities.clear()
        self.is_running = False
