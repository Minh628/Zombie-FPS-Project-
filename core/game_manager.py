# game_manager.py - Quản lý state của game (Play, Pause, Game Over)
# GameManager kế thừa Entity để Ursina tự gọi update() và input() mỗi frame.
# Đây là nơi DUY NHẤT khởi tạo và điều phối tất cả module trong game.
from enum import Enum
from ursina import *
import random
import time as _time

from core.config import *
from entities.player import Player
from entities.weapon import Weapon
from ui.main_menu import MainMenu
from ui.hud import HUD
from levels.level_01 import Level01
from database.db_manager import DBManager


class GameState(Enum):
    """Các trạng thái của game."""
    MAIN_MENU = 'main_menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'


class GameManager(Entity):
    """
    Quản lý trạng thái tổng thể của game.
    Kế thừa Entity để Ursina tự động gọi update() và input().
    Tự khởi tạo TẤT CẢ module: Player, Weapon, HUD, Menu, Level, Database.
    """

    def __init__(self):
        super().__init__()

        # --- Trạng thái game ---
        self.state = GameState.MAIN_MENU
        self.score = 0
        self.wave = 1
        self.zombies_killed = 0
        self.player_name = 'Player'
        self.play_start_time = 0
        self.play_time = 0

        # --- Hệ thống spawn zombie ---
        self.active_zombies = []
        self.zombies_per_wave = 5
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = 0
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.wave_transition_timer = 0
        self.is_wave_transitioning = False

        # ============================
        # KHỞI TẠO TẤT CẢ MODULE
        # ============================

        # 1. Database
        self.db = DBManager()
        self.db.connect()

        # 2. Level (map, ánh sáng, spawn points)
        self.level = Level01()

        # 3. Player (ẩn cho đến khi bắt đầu game)
        self.player = Player()
        self.player.position = Vec3(0, 1, 0)
        self.player.enabled = False

        # 4. Weapon (ẩn cho đến khi bắt đầu game)
        self.weapon = Weapon(self.player)
        self.weapon.enabled = False

        # 5. HUD (ẩn cho đến khi bắt đầu game)
        self.hud = HUD()

        # 6. Main Menu (hiện ngay)
        self.menu = MainMenu()

        # ============================
        # KẾT NỐI CALLBACKS
        # ============================
        self._setup_callbacks()

        # Load bảng xếp hạng ban đầu
        self._load_leaderboard()

        # Hiển thị menu, mở khóa chuột
        self.menu.show()
        mouse.locked = False

        print('[GameManager] Initialized all modules.')

    def _setup_callbacks(self):
        """Kết nối tất cả callbacks giữa các module."""
        # Player -> HUD
        self.player.on_health_changed = self.hud.update_health
        self.player.on_death = self._on_player_death

        # Weapon -> HUD
        self.weapon.on_ammo_changed = self.hud.update_ammo

        # Menu -> Start Game
        self.menu.on_start_game = self.start_game

        # Pause Menu buttons
        self.hud.resume_btn.on_click = self.resume_game
        self.hud.pause_restart_btn.on_click = self.restart_game
        self.hud.pause_menu_btn.on_click = self.return_to_menu

        # Game Over buttons
        self.hud.gameover_restart_btn.on_click = self.restart_game
        self.hud.gameover_menu_btn.on_click = self.return_to_menu

    def _load_leaderboard(self):
        """Load bảng xếp hạng từ database."""
        try:
            scores = self.db.get_top_scores(10)
            self.menu.update_leaderboard(scores)
        except Exception as e:
            print(f'[GameManager] Error loading leaderboard: {e}')

    # ==============================================================
    # CÁC HÀNH ĐỘNG CHUYỂN TRẠNG THÁI
    # ==============================================================

    def start_game(self):
        """Bắt đầu game mới, reset các giá trị."""
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.zombies_killed = 0
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = self.zombies_per_wave
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.is_wave_transitioning = False
        self.play_start_time = _time.time()

        # Xóa zombie cũ (nếu có)
        self._clear_all_zombies()

        # Tạo lại level
        self._recreate_level()

        # Reset player
        self.player.respawn(Vec3(0, 1, 0))
        self.player.enabled = True

        # Reset weapon
        self.weapon.current_ammo = self.weapon.max_ammo
        self.weapon.total_ammo = WEAPON_TOTAL_AMMO
        self.weapon.is_reloading = False
        self.weapon.can_shoot = True
        self.weapon.enabled = True

        # Ẩn menu, hiện HUD
        self.menu.hide()
        self.hud.show()
        self.hud.update_health(self.player.health, self.player.max_health)
        self.hud.update_ammo(self.weapon.current_ammo, self.weapon.total_ammo)
        self.hud.update_score(self.score)
        self.hud.update_wave(self.wave)

        # Lock chuột để chơi
        mouse.locked = True
        application.paused = False

        print('[GameManager] Game started!')

    def pause_game(self):
        """Tạm dừng game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            mouse.locked = False
            application.paused = True
            self.hud.show_pause_menu()
            print('[GameManager] Game paused.')

    def resume_game(self):
        """Tiếp tục game sau khi tạm dừng."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            mouse.locked = True
            application.paused = False
            self.hud.hide_pause_menu()
            print('[GameManager] Game resumed.')

    def game_over(self):
        """Kết thúc game khi người chơi thua."""
        self.state = GameState.GAME_OVER
        self.play_time = _time.time() - self.play_start_time
        mouse.locked = False
        application.paused = False

        # Xóa tất cả zombie
        self._clear_all_zombies()

        # Disable player & weapon
        self.player.enabled = False
        self.weapon.enabled = False

        # Lưu điểm vào database
        try:
            self.db.save_score(
                self.player_name,
                self.score,
                self.wave,
                self.zombies_killed,
                self.play_time
            )
        except Exception as e:
            print(f'[GameManager] Error saving score: {e}')

        # Hiển thị màn hình Game Over
        self.hud.show_game_over(self.score, self.wave, self.zombies_killed, self.play_time)
        print(f'[GameManager] Game Over! Score: {self.score} | Kills: {self.zombies_killed}')

    def return_to_menu(self):
        """Quay lại menu chính."""
        self.state = GameState.MAIN_MENU
        application.paused = False

        # Xóa zombie
        self._clear_all_zombies()

        # Ẩn tất cả overlay
        self.hud.hide()
        self.hud.hide_game_over()
        self.hud.hide_pause_menu()

        # Disable player & weapon
        self.player.enabled = False
        self.weapon.enabled = False

        # Cleanup level
        if self.level:
            self.level.cleanup()

        # Cập nhật leaderboard rồi hiện menu
        self._load_leaderboard()
        self.menu.show()
        mouse.locked = False

    def restart_game(self):
        """Chơi lại từ đầu."""
        self.hud.hide_game_over()
        self.hud.hide_pause_menu()
        application.paused = False
        self.start_game()

    # ==============================================================
    # HỆ THỐNG WAVE & SPAWN
    # ==============================================================

    def add_score(self, points):
        """Cộng điểm khi tiêu diệt zombie."""
        self.score += points
        self.zombies_killed += 1
        self.hud.update_score(self.score)

    def next_wave(self):
        """Chuyển sang wave tiếp theo."""
        self.wave += 1
        self.zombies_spawned_this_wave = 0
        self.zombies_to_spawn = self.zombies_per_wave + (self.wave - 1) * 3
        self.spawn_timer = 0
        self.is_wave_transitioning = False
        self.hud.update_wave(self.wave)
        self.hud.show_wave_notification(self.wave)
        print(f'[GameManager] Wave {self.wave} started! Zombies: {self.zombies_to_spawn}')

    def update(self):
        """Cập nhật game logic mỗi frame (Ursina tự gọi)."""
        if self.state != GameState.PLAYING:
            return

        self._update_spawn()
        self._check_wave_complete()

    def input(self, key):
        """Xử lý input (Ursina tự gọi)."""
        if key == 'escape':
            if self.state == GameState.PLAYING:
                self.pause_game()
            elif self.state == GameState.PAUSED:
                self.resume_game()

    # ==============================================================
    # PRIVATE METHODS
    # ==============================================================

    def _recreate_level(self):
        """Dọn dẹp level cũ và tạo level mới."""
        if self.level:
            self.level.cleanup()
        self.level = Level01()

    def _update_spawn(self):
        """Cập nhật logic spawn zombie."""
        if self.is_wave_transitioning:
            self.wave_transition_timer -= time.dt
            if self.wave_transition_timer <= 0:
                self.next_wave()
            return

        if self.zombies_spawned_this_wave >= self.zombies_to_spawn:
            return

        self.spawn_timer -= time.dt
        if self.spawn_timer <= 0:
            self._spawn_zombie()
            self.spawn_timer = self.spawn_interval
            self.spawn_interval = max(1.0, 3.0 - (self.wave - 1) * 0.3)

    def _spawn_zombie(self):
        """Spawn một zombie tại vị trí ngẫu nhiên."""
        from entities.enemies.zombie_base import ZombieBase
        from entities.enemies.zombie_fast import ZombieFast

        if not self.level or not self.player:
            return

        spawn_pos = self.level.get_random_spawn_point()
        spawn_pos = Vec3(
            spawn_pos.x + random.uniform(-5, 5),
            1,
            spawn_pos.z + random.uniform(-5, 5)
        )

        # Wave 3 trở đi có zombie nhanh (30% cơ hội)
        if self.wave >= 3 and random.random() < 0.3:
            zombie = ZombieFast(position=spawn_pos, player=self.player)
        else:
            zombie = ZombieBase(position=spawn_pos, player=self.player)

        zombie.on_death = self._on_zombie_death
        self.active_zombies.append(zombie)
        self.zombies_spawned_this_wave += 1

    def _on_zombie_death(self, zombie):
        """Callback khi zombie chết."""
        from entities.enemies.zombie_fast import ZombieFast
        points = 150 if isinstance(zombie, ZombieFast) else 100
        self.add_score(points)

        if zombie in self.active_zombies:
            self.active_zombies.remove(zombie)

    def _check_wave_complete(self):
        """Kiểm tra nếu wave hiện tại đã hoàn thành."""
        if self.is_wave_transitioning:
            return

        if (self.zombies_spawned_this_wave >= self.zombies_to_spawn
                and len(self.active_zombies) == 0
                and self.zombies_to_spawn > 0):
            self.is_wave_transitioning = True
            self.wave_transition_timer = 5.0
            self.hud.show_wave_complete(self.wave)
            print(f'[GameManager] Wave {self.wave} complete!')

    def _on_player_death(self):
        """Callback khi player chết."""
        invoke(self.game_over, delay=1.0)

    def _clear_all_zombies(self):
        """Xóa tất cả zombie đang tồn tại."""
        for zombie in self.active_zombies[:]:
            if zombie:
                destroy(zombie)
        self.active_zombies.clear()
