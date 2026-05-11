# main.py - Entry point: Nơi khởi tạo game và nối các module lại
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# --- Import các module của dự án ---
# from core.config import *
# from core.game_manager import GameManager
# from entities.player import Player
# from entities.weapon import Weapon
# from entities.enemies.zombie_base import ZombieBase
# from ui.main_menu import MainMenu
# from ui.hud import HUD
# from levels.level_01 import Level01
# from database.db_manager import DBManager


def main():
    """Hàm chính khởi tạo và chạy game."""
    app = Ursina(title='Zombie FPS', borderless=False)

    # TODO: Khởi tạo các module
    # game_manager = GameManager()
    # player = Player()
    # weapon = Weapon()
    # hud = HUD(player)
    # main_menu = MainMenu()
    # level = Level01()

    # Tạm thời: Thiết lập cơ bản để test
    ground = Entity(
        model='plane',
        scale=(100, 1, 100),
        color=color.gray,
        texture='white_cube',
        texture_scale=(100, 100),
        collider='box'
    )

    player = FirstPersonController()

    Sky()

    app.run()


if __name__ == '__main__':
    main()
