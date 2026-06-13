# main.py - Entry point: Nơi khởi tạo game và nối các module lại
# Cấu hình engine trước khi khởi tạo game
from core.engine_setup import setup_engine_configs
setup_engine_configs()

from ursina import *
from core.game_manager import GameManager

app = Ursina(title='Zombie FPS', borderless=False)

game = GameManager()
app.run()
