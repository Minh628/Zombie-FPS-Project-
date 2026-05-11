# game_manager.py - Quản lý state của game (Play, Pause, Game Over)
from enum import Enum


class GameState(Enum):
    """Các trạng thái của game."""
    MAIN_MENU = 'main_menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'


class GameManager:
    """
    Quản lý trạng thái tổng thể của game.
    Điều phối giữa các module: Player, UI, Level, Database.
    """

    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.score = 0
        self.wave = 1
        self.zombies_killed = 0
        self.is_running = True

    def start_game(self):
        """Bắt đầu game mới, reset các giá trị."""
        self.state = GameState.PLAYING
        self.score = 0
        self.wave = 1
        self.zombies_killed = 0
        print('[GameManager] Game started!')

    def pause_game(self):
        """Tạm dừng game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            print('[GameManager] Game paused.')

    def resume_game(self):
        """Tiếp tục game sau khi tạm dừng."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            print('[GameManager] Game resumed.')

    def game_over(self):
        """Kết thúc game khi người chơi thua."""
        self.state = GameState.GAME_OVER
        print(f'[GameManager] Game Over! Score: {self.score} | Zombies Killed: {self.zombies_killed}')

    def add_score(self, points):
        """Cộng điểm khi tiêu diệt zombie."""
        self.score += points
        self.zombies_killed += 1

    def next_wave(self):
        """Chuyển sang wave tiếp theo."""
        self.wave += 1
        print(f'[GameManager] Wave {self.wave} started!')

    def get_state(self):
        """Trả về trạng thái hiện tại."""
        return self.state
