# ui_manager.py - Gom nhóm tất cả giao diện, chuyển đổi chế độ hiển thị
from ursina import *
from ui.main_menu import MainMenu
from ui.hud import HUD
from ui.pause_menu import PauseMenu
from ui.game_over_screen import GameOverScreen


class UIManager:
    """
    Quản lý tất cả màn hình UI.
    GameManager chỉ cần gọi 1 lệnh để chuyển giao diện.
    """

    def __init__(self):
        self.hud = HUD()
        self.menu = MainMenu()
        self.pause = PauseMenu()
        self.game_over = GameOverScreen()

    # ==============================================================
    # CHUYỂN CHẾ ĐỘ HIỂN THỊ
    # ==============================================================

    def _hide_all_except(self, active_screen):
        """Tắt tất cả các màn hình, chỉ bật màn hình được chỉ định."""
        screens = [self.hud, self.menu, self.pause, self.game_over]
        for screen in screens:
            if screen != active_screen:
                screen.hide()
        if active_screen:
            active_screen.show()

    def switch_to_menu_mode(self):
        """Hiển thị menu chính, ẩn mọi thứ khác."""
        self._hide_all_except(self.menu)
        mouse.locked = False

    def switch_to_play_mode(self):
        """Hiển thị HUD gameplay, ẩn menu."""
        self._hide_all_except(self.hud)
        mouse.locked = True

    def switch_to_pause_mode(self):
        """Hiển thị menu pause (hiển thị đè lên HUD)."""
        self.pause.show()
        mouse.locked = False

    def switch_to_game_over_mode(self, score, wave, kills, play_time):
        """Hiển thị màn hình game over với thống kê."""
        self._hide_all_except(self.game_over)
        self.game_over.show_result(score, wave, kills, play_time)
        mouse.locked = False

    def hide_pause(self):
        """Ẩn menu pause (khi resume)."""
        self.pause.hide()
        mouse.locked = True

    # ==============================================================
    # CẬP NHẬT HUD (proxy methods)
    # ==============================================================

    def update_health(self, current, maximum):
        self.hud.update_health(current, maximum)

    def update_ammo(self, current, total):
        self.hud.update_ammo(current, total)

    def update_score(self, score):
        self.hud.update_score(score)

    def update_wave(self, wave):
        self.hud.update_wave(wave)

    def update_weapon_name(self, name):
        self.hud.update_weapon_name(name)

    def show_wave_notification(self, wave):
        self.hud.show_wave_notification(wave)

    def show_wave_complete(self, wave):
        self.hud.show_wave_complete(wave)

    def update_leaderboard(self, scores):
        self.menu.update_leaderboard(scores)
