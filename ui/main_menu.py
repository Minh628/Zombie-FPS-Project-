# main_menu.py - Màn hình bắt đầu game, bảng xếp hạng
from ursina import *


class MainMenu(Entity):
    """
    Màn hình menu chính.
    Bao gồm: nút Start Game, Leaderboard, Quit.
    """

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)

        # --- Nền tối ---
        self.background = Entity(
            parent=self,
            model='quad',
            scale=(2, 2),
            color=color.rgba(0, 0, 0, 200),
            z=1
        )

        # Tiêu đề game
        self.title = Text(
            text='ZOMBIE FPS',
            parent=self,
            scale=4,
            position=(0, 0.35),
            origin=(0, 0),
            color=color.rgb(200, 30, 30)
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
            text='START GAME',
            parent=self,
            scale=(0.3, 0.07),
            position=(0, 0.05),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(0, 150, 0),
            text_color=color.white,
            on_click=self._on_start_click
        )

        # Nút Leaderboard
        self.leaderboard_btn = Button(
            text='LEADERBOARD',
            parent=self,
            scale=(0.3, 0.07),
            position=(0, -0.05),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(0, 100, 200),
            text_color=color.white,
            on_click=self.toggle_leaderboard
        )

        # Nút Quit
        self.quit_btn = Button(
            text='QUIT',
            parent=self,
            scale=(0.3, 0.07),
            position=(0, -0.15),
            color=color.rgb(40, 40, 40),
            highlight_color=color.rgb(200, 30, 30),
            text_color=color.white,
            on_click=application.quit
        )

        # --- Hướng dẫn ---
        self.controls_text = Text(
            text='WASD: Move | SHIFT: Sprint | MOUSE: Shoot | R: Reload | ESC: Pause',
            parent=self,
            scale=0.7,
            position=(0, -0.30),
            origin=(0, 0),
            color=color.rgb(150, 150, 150)
        )

        # --- Bảng xếp hạng (ẩn mặc định) ---
        self.leaderboard_panel = Entity(parent=self, enabled=False)
        self.leaderboard_bg = Entity(
            parent=self.leaderboard_panel,
            model='quad',
            scale=(0.6, 0.7),
            color=color.rgba(20, 20, 20, 240),
            position=(0, 0.05),
            z=-0.1
        )
        self.leaderboard_title = Text(
            text='LEADERBOARD',
            parent=self.leaderboard_panel,
            scale=2,
            position=(0, 0.35),
            origin=(0, 0),
            color=color.gold
        )
        self.leaderboard_entries = []
        self.leaderboard_close_btn = Button(
            text='CLOSE',
            parent=self.leaderboard_panel,
            scale=(0.2, 0.05),
            position=(0, -0.28),
            color=color.rgb(60, 60, 60),
            highlight_color=color.rgb(200, 30, 30),
            text_color=color.white,
            on_click=self.toggle_leaderboard
        )

        # Header bảng xếp hạng
        self.lb_header = Text(
            text='#   Name          Score   Wave  Kills',
            parent=self.leaderboard_panel,
            scale=0.7,
            position=(-0.25, 0.27),
            color=color.rgb(200, 200, 100)
        )

        # Callback - GameManager sẽ gán hàm start_game vào đây
        self.on_start_game = None

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
        """Cập nhật dữ liệu bảng xếp hạng."""
        # Xóa entries cũ
        for entry in self.leaderboard_entries:
            destroy(entry)
        self.leaderboard_entries.clear()

        if not scores:
            no_data = Text(
                text='No scores yet!',
                parent=self.leaderboard_panel,
                scale=0.8,
                position=(0, 0.10),
                origin=(0, 0),
                color=color.light_gray
            )
            self.leaderboard_entries.append(no_data)
            return

        for i, row in enumerate(scores):
            rank = i + 1
            name = row['player_name'][:12]
            score_val = row['score']
            wave_val = row['wave_reached']
            kills_val = row['zombies_killed']

            # Chọn màu cho top 3
            if rank == 1:
                entry_color = color.gold
            elif rank == 2:
                entry_color = color.rgb(192, 192, 192)
            elif rank == 3:
                entry_color = color.rgb(205, 127, 50)
            else:
                entry_color = color.white

            entry_text = Text(
                text=f'{rank}.  {name:<12}  {score_val:<7} {wave_val:<5} {kills_val}',
                parent=self.leaderboard_panel,
                scale=0.65,
                position=(-0.25, 0.21 - i * 0.05),
                color=entry_color
            )
            self.leaderboard_entries.append(entry_text)

    def show(self):
        """Hiện menu."""
        self.enabled = True
        mouse.locked = False

    def hide(self):
        """Ẩn menu."""
        self.enabled = False
