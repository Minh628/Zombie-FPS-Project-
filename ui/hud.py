# hud.py - Overlay trong game (thanh máu, số đạn, vũ khí, điểm, wave)
# Chỉ chứa HUD gameplay, không chứa pause hay game over.
from ursina import *


class HUD(Entity):
    """
    Heads-Up Display - Hiển thị thông tin gameplay.
    Bao gồm: crosshair, thanh máu, đạn, vũ khí, điểm, wave.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        # --- Crosshair (dấu +) ---
        Entity(parent=self, model='quad', scale=(0.02, 0.002), color=color.lime)
        Entity(parent=self, model='quad', scale=(0.002, 0.02), color=color.lime)

        # --- Thanh máu (góc dưới trái) ---
        self.health_bar_bg = Entity(
            parent=self, model='quad',
            scale=(0.3, 0.025), position=(-0.55, -0.44),
            color=color.dark_gray, origin=(-0.5, 0)
        )
        self.health_bar = Entity(
            parent=self.health_bar_bg, model='quad',
            scale=(1, 0.8), color=color.green,
            origin=(-0.5, 0), z=-0.01
        )
        self.health_text = Text(
            parent=self, text='100 / 100',
            position=(-0.55, -0.41), scale=0.9, color=color.white
        )

        # --- Đạn (góc dưới phải) ---
        self.ammo_text = Text(
            parent=self, text='30 / 120',
            position=(0.72, -0.44), scale=1.5,
            origin=(1, 0), color=color.white
        )
        self.ammo_label = Text(
            parent=self, text='AMMO',
            position=(0.72, -0.41), scale=0.7,
            origin=(1, 0), color=color.light_gray
        )

        # --- Tên vũ khí ---
        self.weapon_name_text = Text(
            parent=self, text='RIFLE',
            position=(0.72, -0.37), scale=1.0,
            origin=(1, 0), color=color.yellow
        )

        # --- Điểm (góc trên giữa) ---
        self.score_text = Text(
            parent=self, text='Score: 0',
            position=(0, 0.45), scale=1.5,
            origin=(0, 0), color=color.gold
        )

        # --- Wave ---
        self.wave_text = Text(
            parent=self, text='Wave: 1',
            position=(0, 0.40), scale=1.0,
            origin=(0, 0), color=color.light_gray
        )

        # --- Thông báo wave (giữa màn hình, tạm thời) ---
        self.wave_notification = Text(
            parent=self, text='', position=(0, 0.1),
            scale=4, origin=(0, 0),
            color=color.red, enabled=False
        )

        # Bắt đầu ẩn
        self.enabled = False

    def update_health(self, current_health, max_health):
        """Cập nhật thanh máu."""
        ratio = current_health / max_health if max_health > 0 else 0
        self.health_bar.scale_x = max(ratio, 0)
        self.health_text.text = f'{int(current_health)} / {int(max_health)}'

        if ratio > 0.5:
            self.health_bar.color = color.green
        elif ratio > 0.25:
            self.health_bar.color = color.yellow
        else:
            self.health_bar.color = color.red

    def update_ammo(self, current_ammo, total_ammo):
        """Cập nhật số đạn. current_ammo < 0 = vũ khí cận chiến."""
        if current_ammo < 0:
            self.ammo_text.text = 'INF'
            self.ammo_label.text = 'MELEE'
        else:
            self.ammo_text.text = f'{current_ammo} / {total_ammo}'
            self.ammo_label.text = 'AMMO'

    def update_score(self, score):
        self.score_text.text = f'Score: {score}'

    def update_wave(self, wave):
        self.wave_text.text = f'Wave: {wave}'

    def update_weapon_name(self, name):
        self.weapon_name_text.text = name

    def show_wave_notification(self, wave):
        """Hiển thị thông báo wave mới."""
        self.wave_notification.text = f'WAVE {wave}'
        self.wave_notification.color = color.red
        self.wave_notification.enabled = True
        invoke(lambda: setattr(self.wave_notification, 'enabled', False), delay=2.5)

    def show_wave_complete(self, wave):
        """Hiển thị thông báo hoàn thành wave."""
        self.wave_notification.text = f'WAVE {wave} COMPLETE!'
        self.wave_notification.color = color.lime
        self.wave_notification.enabled = True
        invoke(lambda: setattr(self.wave_notification, 'enabled', False), delay=3.5)

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False
