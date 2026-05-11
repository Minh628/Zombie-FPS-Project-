# main_menu.py - Màn hình bắt đầu game, bảng xếp hạng
from ursina import *


class MainMenu(Entity):
    """
    Màn hình menu chính.
    Bao gồm: nút Start Game, Leaderboard, Quit.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.is_visible = True

        # Tiêu đề game
        self.title = Text(
            text='🧟 ZOMBIE FPS',
            parent=self,
            scale=3,
            position=(0, 0.35),
            origin=(0, 0),
            color=color.red
        )

        # Phụ đề
        self.subtitle = Text(
            text='Survive the Horde',
            parent=self,
            scale=1.5,
            position=(0, 0.25),
            origin=(0, 0),
            color=color.light_gray
        )

        # Nút Start Game
        self.start_btn = Button(
            text='Start Game',
            parent=self,
            scale=(0.3, 0.06),
            position=(0, 0.05),
            color=color.dark_gray,
            highlight_color=color.green,
            on_click=self.start_game
        )

        # Nút Leaderboard
        self.leaderboard_btn = Button(
            text='Leaderboard',
            parent=self,
            scale=(0.3, 0.06),
            position=(0, -0.05),
            color=color.dark_gray,
            highlight_color=color.azure
        )

        # Nút Quit
        self.quit_btn = Button(
            text='Quit',
            parent=self,
            scale=(0.3, 0.06),
            position=(0, -0.15),
            color=color.dark_gray,
            highlight_color=color.red,
            on_click=application.quit
        )

        # Callbacks
        self.on_start_game = None

    def start_game(self):
        """Xử lý khi nhấn Start Game."""
        print('[MainMenu] Starting game...')
        self.hide()
        if self.on_start_game:
            self.on_start_game()

    def show(self):
        """Hiện menu."""
        self.enabled = True
        mouse.locked = False

    def hide(self):
        """Ẩn menu."""
        self.enabled = False
        mouse.locked = True
