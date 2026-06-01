# game_manager.py - Đạo diễn game: CHỈ gọi và điều phối, KHÔNG xử lý chi tiết.
# - Vũ khí → Player tự lo
# - Wave/Spawn → Level tự lo
# - UI → UIManager tự lo
# - GameManager chỉ hô: BẮT ĐẦU! TẠM DỪNG! KẾT THÚC!
from enum import Enum
from ursina import *
import time as _time

from entities.player import Player
from ui.ui_manager import UIManager
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
    Đạo diễn game - chỉ điều phối, không xử lý logic chi tiết.
    Mỗi module tự lo việc của mình, GameManager chỉ hô và nối dây.
    """

    def __init__(self):
        super().__init__()

        self.state = GameState.MAIN_MENU
        self.score = 0
        self.zombies_killed = 0
        self.player_name = 'Player'
        self.play_start_time = 0
        self.play_time = 0

        # === Khởi tạo các "diễn viên" ===
        self.db = DBManager()
        self.db.connect()

        self.level = Level01()

        self.player = Player()
        self.player.position = Vec3(0, 1, 0)
        self.player.enabled = False

        self.ui = UIManager()

        # === Nối dây callbacks ===
        self._connect_callbacks()

        # === Load dữ liệu ban đầu ===
        self._load_leaderboard()

        # === Hiển thị menu ===
        self.ui.switch_to_menu_mode()

        print('[GameManager] Ready.')

    # ==============================================================
    # NỐI DÂY (callbacks giữa các module)
    # ==============================================================

    def _connect_callbacks(self):
        """Nối dây sự kiện giữa các module."""
        # Player → UI (máu)
        self.player.on_health_changed = self.ui.update_health
        self.player.on_death = self._on_player_death

        # Player → UI (vũ khí thay đổi)
        self.player.on_weapon_changed = self._on_weapon_changed

        # Level → GameManager (wave events)
        self.level.on_zombie_killed = self._on_zombie_killed
        self.level.on_wave_start = self._on_wave_start
        self.level.on_wave_complete = self._on_wave_complete

        # Menu → start game
        self.ui.menu.on_start_game = self.start_game

        # Pause Menu → actions
        self.ui.pause.on_resume = self.resume_game
        self.ui.pause.on_restart = self.restart_game
        self.ui.pause.on_menu = self.return_to_menu

        # Game Over → actions
        self.ui.game_over.on_restart = self.restart_game
        self.ui.game_over.on_menu = self.return_to_menu

    def _load_leaderboard(self):
        """Load bảng xếp hạng từ database."""
        try:
            scores = self.db.get_top_scores(10)
            self.ui.update_leaderboard(scores)
        except Exception as e:
            print(f'[GameManager] Leaderboard error: {e}')

    # ==============================================================
    # HÀNH ĐỘNG ĐẠO DIỄN (ngắn gọn, chỉ gọi)
    # ==============================================================

    def start_game(self):
        """Đạo diễn hô: BẮT ĐẦU!"""
        self.state = GameState.PLAYING
        self.score = 0
        self.zombies_killed = 0
        self.play_time = 0
        self.play_start_time = _time.time()

        # Player tự lo: hồi sinh + reset vũ khí
        self.player.respawn(Vec3(50, 1, 0))
        self.player.enabled = True
        self.player.reset_weapons()

        # Level tự lo: dọn quái + reset wave (KHÔNG load lại map)
        self.level.reset_level(self.player)

        # UI tự lo: chuyển sang chế độ chơi
        self.ui.switch_to_play_mode()
        self.ui.update_score(0)
        self.ui.update_wave(1)

        application.paused = False
        print('[GameManager] Game started!')

    def pause_game(self):
        """Đạo diễn hô: TẠM DỪNG!"""
        if self.state != GameState.PLAYING:
            return
        self.state = GameState.PAUSED
        application.paused = True
        self.ui.switch_to_pause_mode()

    def resume_game(self):
        """Đạo diễn hô: TIẾP TỤC!"""
        if self.state != GameState.PAUSED:
            return
        self.state = GameState.PLAYING
        application.paused = False
        self.ui.hide_pause()

    def game_over(self):
        """Đạo diễn hô: KẾT THÚC!"""
        if self.state != GameState.PLAYING:
            return
        self.state = GameState.GAME_OVER
        application.paused = False

        # Dừng level
        self.level.stop_waves()

        # Disable player
        self.player.enabled = False
        self.player.disable_weapons()

        # Lưu điểm vào database
        self._save_score()

        # Hiện Game Over
        self.ui.switch_to_game_over_mode(
            self.score, self.level.wave,
            self.zombies_killed, self.play_time
        )

    def return_to_menu(self):
        """Đạo diễn hô: VỀ MENU!"""
        self.state = GameState.MAIN_MENU
        application.paused = False

        self.level.stop_waves()
        self.player.enabled = False
        self.player.disable_weapons()

        self._load_leaderboard()
        self.ui.switch_to_menu_mode()

    def restart_game(self):
        """Đạo diễn hô: CHƠI LẠI!"""
        self.ui.pause.hide()
        self.ui.game_over.hide()
        application.paused = False
        self.start_game()

    # ==============================================================
    # CALLBACKS (nhận tin từ các module)
    # ==============================================================

    def _on_zombie_killed(self, points):
        """Level báo: zombie chết."""
        self.score += points
        self.zombies_killed += 1
        self.ui.update_score(self.score)

    def _on_wave_start(self, wave):
        """Level báo: wave mới."""
        self.ui.update_wave(wave)
        self.ui.show_wave_notification(wave)

    def _on_wave_complete(self, wave):
        """Level báo: wave xong."""
        self.ui.show_wave_complete(wave)

    def _on_player_death(self):
        """Player báo: chết."""
        invoke(self.game_over, delay=1.0)

    def _on_weapon_changed(self, weapon):
        """Player báo: đổi vũ khí."""
        self.ui.update_weapon_name(weapon.weapon_name)
        weapon.on_ammo_changed = self.ui.update_ammo
        weapon._notify_ammo()

    def _save_score(self):
        """Lưu điểm vào database."""
        try:
            self.db.save_score(
                self.player_name, self.score,
                self.level.wave, self.zombies_killed, self.play_time
            )
            print(f'[DB] Saved: {self.score}pts')
        except Exception as e:
            print(f'[DB] Error: {e}')

    # ==============================================================
    # UPDATE & INPUT (Ursina tự gọi)
    # ==============================================================

    def update(self):
        """Mỗi frame: chỉ gọi level."""
        if self.state == GameState.PLAYING:
            self.play_time += time.dt
            self.level.update_waves()

    def input(self, key):
        """ESC: pause/resume. Vũ khí: Player tự lo."""
        if key == 'escape':
            if self.state == GameState.PLAYING:
                self.pause_game()
            elif self.state == GameState.PAUSED:
                self.resume_game()
