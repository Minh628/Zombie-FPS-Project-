# game_over_screen.py - Màn hình kết thúc game
from ursina import *
from core.utils import format_time


class GameOverScreen(Entity):
    """
    Màn hình Game Over - hiển thị khi người chơi thua.
    Hiện thống kê (score, wave, kills, time) và nút chơi lại / về menu.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, enabled=False, **kwargs)

        # Nền đỏ tối
        Entity(
            parent=self, model='quad',
            scale=5, color=Color(0.3, 0, 0, 0.85), z=0.5
        )

        # Tiêu đề GAME OVER
        Text(
            text='GAME OVER',
            parent=self, scale=6, y=0.30,
            origin=(0, 0), color=color.red
        )

        # Điểm số
        self.score_text = Text(
            text='Score: 0',
            parent=self, scale=2.5, y=0.16,
            origin=(0, 0), color=color.gold
        )

        # Thống kê
        self.stats_text = Text(
            text='',
            parent=self, scale=1.2, y=0.06,
            origin=(0, 0), color=color.white
        )

        # Nút Play Again
        self.restart_btn = Button(
            text='PLAY AGAIN', parent=self,
            scale=(0.3, 0.07), y=-0.10,
            color=color.dark_gray,
            highlight_color=color.lime,
        )

        # Nút Main Menu
        self.menu_btn = Button(
            text='MAIN MENU', parent=self,
            scale=(0.3, 0.07), y=-0.20,
            color=color.dark_gray,
            highlight_color=color.red,
        )

        # Callbacks (GameManager sẽ gán)
        self.on_restart = None
        self.on_menu = None

        self.restart_btn.on_click = lambda: self.on_restart() if self.on_restart else None
        self.menu_btn.on_click = lambda: self.on_menu() if self.on_menu else None

    def show_result(self, score, wave, kills, play_time):
        """Hiện màn hình Game Over với thống kê."""
        self.score_text.text = f'Score: {score}'
        self.stats_text.text = (
            f'Wave: {wave}   |   Kills: {kills}   |   '
            f'Time: {format_time(play_time)}'
        )
        self.enabled = True

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False
