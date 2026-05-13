# pause_menu.py - Màn hình tạm dừng game
from ursina import *


class PauseMenu(Entity):
    """
    Màn hình Pause - hiển thị khi nhấn ESC.
    Có 3 nút: Resume, Restart, Main Menu.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, enabled=False, **kwargs)

        # Nền tối bán trong suốt
        Entity(
            parent=self, model='quad',
            scale=5, color=Color(0, 0, 0, 0.8), z=0.5
        )

        # Tiêu đề
        Text(
            text='GAME PAUSED',
            parent=self, scale=4, y=0.25,
            origin=(0, 0), color=color.white
        )

        # Nút Resume
        self.resume_btn = Button(
            text='RESUME', parent=self,
            scale=(0.3, 0.07), y=0.06,
            color=color.dark_gray,
            highlight_color=color.lime,
        )

        # Nút Restart
        self.restart_btn = Button(
            text='RESTART', parent=self,
            scale=(0.3, 0.07), y=-0.04,
            color=color.dark_gray,
            highlight_color=color.yellow,
        )

        # Nút Main Menu
        self.menu_btn = Button(
            text='MAIN MENU', parent=self,
            scale=(0.3, 0.07), y=-0.14,
            color=color.dark_gray,
            highlight_color=color.red,
        )

        # Callbacks (GameManager sẽ gán)
        self.on_resume = None
        self.on_restart = None
        self.on_menu = None

        self.resume_btn.on_click = lambda: self.on_resume() if self.on_resume else None
        self.restart_btn.on_click = lambda: self.on_restart() if self.on_restart else None
        self.menu_btn.on_click = lambda: self.on_menu() if self.on_menu else None

    def show(self):
        self.enabled = True

    def hide(self):
        self.enabled = False
