# level_01.py - Set up map, vị trí spawn quái, ánh sáng, hệ thống wave cho Level 1
from ursina import *
import random


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
        ground = Entity(
            model='plane', scale=(100, 1, 100),
            color=color.gray, texture='white_cube',
            texture_scale=(50, 50), collider='box'
        )
        self.entities.append(ground)

        walls_data = [
            (Vec3(0, 2, 50), Vec3(100, 4, 1)),
            (Vec3(0, 2, -50), Vec3(100, 4, 1)),
            (Vec3(50, 2, 0), Vec3(1, 4, 100)),
            (Vec3(-50, 2, 0), Vec3(1, 4, 100)),
        ]
        for pos, scale in walls_data:
            wall = Entity(
                model='cube', position=pos, scale=scale,
                color=color.dark_gray, collider='box'
            )
            self.entities.append(wall)

        for i in range(15):
            obstacle = Entity(
                model='cube',
                position=(random.uniform(-40, 40), 1, random.uniform(-40, 40)),
                scale=(random.uniform(1, 3), 2, random.uniform(1, 3)),
                color=color.brown, collider='box'
            )
            self.entities.append(obstacle)

        self.sky = Sky()
        self.entities.append(self.sky)

    def _setup_lighting(self):
        """Thiết lập ánh sáng cho level."""
        sun = DirectionalLight()
        sun.look_at(Vec3(1, -1, -1))
        self.entities.append(sun)

    def _setup_spawn_points(self):
        """Định nghĩa các điểm spawn zombie."""
        self.spawn_points = [
            Vec3(30, 0, 30), Vec3(-30, 0, 30),
            Vec3(30, 0, -30), Vec3(-30, 0, -30),
            Vec3(40, 0, 0), Vec3(-40, 0, 0),
            Vec3(0, 0, 40), Vec3(0, 0, -40),
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

        if self.wave >= 3 and random.random() < 0.3:
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
