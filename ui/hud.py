# hud.py - Overlay trong game (thanh máu người chơi, số đạn)
from ursina import *


class HUD(Entity):
    """
    Heads-Up Display - Hiển thị thông tin trong game.
    Bao gồm: thanh máu, số đạn, điểm, crosshair.
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

    def show(self):
        """Hiện HUD."""
        self.enabled = True

    def hide(self):
        """Ẩn HUD."""
        self.enabled = False
