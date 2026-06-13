# main_menu.py - Màn hình bắt đầu game, bảng xếp hạng
from ursina import *
from core.config import SOUNDS_DIR
from core import config


class MainMenu(Entity):
    """
    Màn hình menu chính.
    Bao gồm: nút Start Game, Leaderboard, Quit.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.background_sound = Audio(f'{SOUNDS_DIR}/background_welcome.mp3', autoplay=False, loop=True, volume=0.8)

        # Nền menu (dùng ảnh trong config, fallback nền đen)
        bg_texture = load_texture(config.MAIN_MENU_BG)
        if bg_texture:
            self.background = Entity(
                parent=self, model='quad',
                scale=(2,1,1), texture=bg_texture,
                color=color.white, z=0.5
            )
        else:
            self.background = Entity(
                parent=self, model='quad',
                scale=5, color=color.black, z=0.5
            )

        # Tiêu đề
        self.title = Text(
            text='ZOMBIE FPS',
            parent=self, scale=5, y=0.35,
            origin=(0, 0), color=color.red
        )

        # Phụ đề
        self.subtitle = Text(
            text='~ Survive the Horde ~',
            parent=self, scale=1.8, y=0.24,
            origin=(0, 0), color=color.light_gray
        )

        # Các nút Menu
        self.start_btn = self._create_menu_button('START GAME', 0.06, color.lime, self._on_start_click)
        self.leaderboard_btn = self._create_menu_button('LEADERBOARD', -0.05, color.azure, self.toggle_leaderboard)
        self.quit_btn = self._create_menu_button('QUIT', -0.16, color.red, application.quit)

        # Hướng dẫn phím
        self.controls_text = Text(
            text='[WASD] Move  [SHIFT] Sprint  [LMB] Shoot  [R] Reload  [1/2/3] Weapon  [ESC] Pause',
            parent=self, scale=0.8, y=-0.32,
            origin=(0, 0), color=color.red
        )

        # Khởi tạo bảng xếp hạng
        self._setup_leaderboard()

        # Callback
        self.on_start_game = None

    def _create_menu_button(self, text, y_pos, highlight_color, on_click):
        """Helper tạo nút menu tránh lặp code."""
        return Button(
            text=text, parent=self,
            scale=(0.35, 0.08), y=y_pos,
            color=color.dark_gray,
            highlight_color=highlight_color,
            on_click=on_click
        )

    def _setup_leaderboard(self):
        """Khởi tạo panel bảng xếp hạng (ẩn mặc định)."""
        self.leaderboard_panel = Entity(parent=self, enabled=False, z=-10)

        Entity(
            parent=self.leaderboard_panel, model='quad',
            scale=(0.65, 0.75), y=0.03,
            color=color.black, z=0.1
        )
        Text(
            text='LEADERBOARD',
            parent=self.leaderboard_panel,
            scale=2.5, y=0.36, origin=(0, 0),
            color=color.gold
        )
        Text(
            text='#   Name          Score   Wave  Kills',
            parent=self.leaderboard_panel,
            scale=0.8, y=0.28, x=-0.27,
            color=color.yellow
        )
        Entity(
            parent=self.leaderboard_panel, model='quad',
            scale=(0.55, 0.002), y=0.26, color=color.yellow
        )
        Button(
            text='CLOSE', parent=self.leaderboard_panel,
            scale=(0.2, 0.06), y=-0.32,
            color=color.dark_gray, highlight_color=color.red,
            on_click=self.toggle_leaderboard
        )
        self.leaderboard_entries = []

    def _on_start_click(self):
        """Xử lý khi nhấn Start Game."""
        print('[MainMenu] Starting game...')
        self.hide()
        if self.on_start_game:
            self.on_start_game()

    def toggle_leaderboard(self):
        """Bật/tắt bảng xếp hạng."""
        self.leaderboard_panel.enabled = not self.leaderboard_panel.enabled

    def update_leaderboard(self, scores):
        """Cập nhật dữ liệu bảng xếp hạng từ database."""
        for entry in self.leaderboard_entries:
            destroy(entry)
        self.leaderboard_entries.clear()

        if not scores:
            t = Text(
                text='No scores yet!',
                parent=self.leaderboard_panel,
                scale=1.0, y=0.10, origin=(0, 0),
                color=color.light_gray
            )
            self.leaderboard_entries.append(t)
            return

        for i, row in enumerate(scores):
            rank = i + 1
            name = row['player_name'][:12]
            s = row['score']
            w = row['wave_reached']
            k = row['zombies_killed']

            if rank == 1:
                c = color.gold
            elif rank == 2:
                c = color.light_gray
            elif rank == 3:
                c = color.orange
            else:
                c = color.white

            t = Text(
                text=f'{rank}.  {name:<12}  {s:<7} {w:<5} {k}',
                parent=self.leaderboard_panel,
                scale=0.7, y=0.22 - i * 0.05, x=-0.27,
                color=c
            )
            self.leaderboard_entries.append(t)

    def show(self):
        """Hiện menu."""
        self.enabled = True
        mouse.locked = False
        self.background_sound.play()

    def hide(self):
        """Ẩn menu."""
        self.enabled = False
        self.background_sound.stop()
