# hud.py - Overlay trong game (thanh máu người chơi, số đạn)
from ursina import *
from core.utils import format_time


class HUD(Entity):
    """
    Heads-Up Display - Hiển thị thông tin trong game.
    Bao gồm: thanh máu, số đạn, điểm, crosshair, pause menu, game over screen.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        # --- Crosshair (Tâm ngắm) ---
        self.crosshair = Entity(
            parent=self,
            model='quad',
            scale=0.008,
            color=color.white,
            position=(0, 0)
        )

        # --- Thanh máu ---
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            scale=(0.3, 0.02),
            position=(-0.55, -0.45),
            color=color.dark_gray,
            origin=(-0.5, 0)
        )
        self.health_bar = Entity(
            parent=self.health_bar_bg,
            model='quad',
            scale=(1, 1),
            color=color.red,
            origin=(-0.5, 0),
            z=-0.01
        )
        self.health_text = Text(
            parent=self,
            text='HP: 100/100',
            position=(-0.55, -0.42),
            scale=0.8,
            color=color.white
        )

        # --- Thông tin đạn ---
        self.ammo_text = Text(
            parent=self,
            text='30 / 120',
            position=(0.55, -0.45),
            scale=1.2,
            origin=(0.5, 0),
            color=color.white
        )
        self.ammo_label = Text(
            parent=self,
            text='AMMO',
            position=(0.55, -0.42),
            scale=0.7,
            origin=(0.5, 0),
            color=color.light_gray
        )

        # --- Điểm ---
        self.score_text = Text(
            parent=self,
            text='Score: 0',
            position=(0, 0.45),
            scale=1.2,
            origin=(0, 0),
            color=color.gold
        )

        # --- Wave ---
        self.wave_text = Text(
            parent=self,
            text='Wave: 1',
            position=(0, 0.40),
            scale=0.9,
            origin=(0, 0),
            color=color.light_gray
        )

        # --- Thông báo Wave (ở giữa màn hình, tạm thời) ---
        self.wave_notification = Text(
            parent=self,
            text='',
            position=(0, 0.1),
            scale=3,
            origin=(0, 0),
            color=color.rgb(255, 50, 50),
            enabled=False
        )

        # === PAUSE MENU ===
        self.pause_panel = Entity(parent=camera.ui, enabled=False)
        self.pause_bg = Entity(
            parent=self.pause_panel,
            model='quad',
            scale=(2, 2),
            color=color.rgba(0, 0, 0, 180),
            z=1
        )
        self.pause_title = Text(
            text='PAUSED',
            parent=self.pause_panel,
            scale=4,
            position=(0, 0.25),
            origin=(0, 0),
            color=color.white
        )
        self.resume_btn = Button(
            text='RESUME',
            parent=self.pause_panel,
            scale=(0.3, 0.06),
            position=(0, 0.05),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(0, 150, 0),
            text_color=color.white,
        )
        self.pause_restart_btn = Button(
            text='RESTART',
            parent=self.pause_panel,
            scale=(0.3, 0.06),
            position=(0, -0.05),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(200, 200, 0),
            text_color=color.white,
        )
        self.pause_menu_btn = Button(
            text='MAIN MENU',
            parent=self.pause_panel,
            scale=(0.3, 0.06),
            position=(0, -0.15),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(200, 30, 30),
            text_color=color.white,
        )

        # === GAME OVER SCREEN ===
        self.gameover_panel = Entity(parent=camera.ui, enabled=False)
        self.gameover_bg = Entity(
            parent=self.gameover_panel,
            model='quad',
            scale=(2, 2),
            color=color.rgba(100, 0, 0, 200),
            z=1
        )
        self.gameover_title = Text(
            text='GAME OVER',
            parent=self.gameover_panel,
            scale=5,
            position=(0, 0.30),
            origin=(0, 0),
            color=color.rgb(255, 30, 30)
        )
        self.gameover_score = Text(
            text='Score: 0',
            parent=self.gameover_panel,
            scale=2,
            position=(0, 0.18),
            origin=(0, 0),
            color=color.gold
        )
        self.gameover_stats = Text(
            text='',
            parent=self.gameover_panel,
            scale=1.2,
            position=(0, 0.08),
            origin=(0, 0),
            color=color.white
        )
        self.gameover_restart_btn = Button(
            text='PLAY AGAIN',
            parent=self.gameover_panel,
            scale=(0.3, 0.06),
            position=(0, -0.08),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(0, 150, 0),
            text_color=color.white,
        )
        self.gameover_menu_btn = Button(
            text='MAIN MENU',
            parent=self.gameover_panel,
            scale=(0.3, 0.06),
            position=(0, -0.18),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(200, 30, 30),
            text_color=color.white,
        )

        # Bắt đầu ở trạng thái ẩn
        self.enabled = False

    def update_health(self, current_health, max_health):
        """Cập nhật thanh máu."""
        ratio = current_health / max_health
        self.health_bar.scale_x = ratio
        self.health_text.text = f'HP: {current_health}/{max_health}'

        # Đổi màu theo mức máu
        if ratio > 0.5:
            self.health_bar.color = color.green
        elif ratio > 0.25:
            self.health_bar.color = color.yellow
        else:
            self.health_bar.color = color.red

    def update_ammo(self, current_ammo, total_ammo):
        """Cập nhật số đạn."""
        self.ammo_text.text = f'{current_ammo} / {total_ammo}'

    def update_score(self, score):
        """Cập nhật điểm."""
        self.score_text.text = f'Score: {score}'

    def update_wave(self, wave):
        """Cập nhật wave hiện tại."""
        self.wave_text.text = f'Wave: {wave}'

    def show_wave_notification(self, wave):
        """Hiển thị thông báo wave mới ở giữa màn hình."""
        self.wave_notification.text = f'WAVE {wave}'
        self.wave_notification.enabled = True
        self.wave_notification.color = color.rgb(255, 50, 50)
        self.wave_notification.animate('color', color.rgba(255, 50, 50, 0), duration=2)
        invoke(lambda: setattr(self.wave_notification, 'enabled', False), delay=2.5)

    def show_wave_complete(self, wave):
        """Hiển thị thông báo wave hoàn thành."""
        self.wave_notification.text = f'WAVE {wave} COMPLETE!'
        self.wave_notification.enabled = True
        self.wave_notification.color = color.rgb(50, 255, 50)
        self.wave_notification.animate('color', color.rgba(50, 255, 50, 0), duration=3)
        invoke(lambda: setattr(self.wave_notification, 'enabled', False), delay=3.5)

    # --- Pause Menu ---
    def show_pause_menu(self):
        """Hiện menu pause."""
        self.pause_panel.enabled = True

    def hide_pause_menu(self):
        """Ẩn menu pause."""
        self.pause_panel.enabled = False

    # --- Game Over Screen ---
    def show_game_over(self, score, wave, kills, play_time):
        """Hiện màn hình Game Over với thống kê."""
        self.gameover_score.text = f'Score: {score}'
        self.gameover_stats.text = (
            f'Wave Reached: {wave}  |  Zombies Killed: {kills}  |  '
            f'Time: {format_time(play_time)}'
        )
        self.gameover_panel.enabled = True

    def hide_game_over(self):
        """Ẩn màn hình Game Over."""
        self.gameover_panel.enabled = False

    def show(self):
        """Hiện HUD."""
        self.enabled = True

    def hide(self):
        """Ẩn HUD."""
        self.enabled = False
