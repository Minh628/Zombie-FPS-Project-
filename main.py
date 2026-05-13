# main.py - Entry point: Nơi khởi tạo game và nối các module lại
from ursina import *
from core.game_manager import GameManager

app = Ursina(title='Zombie FPS', borderless=False)
game = GameManager()
app.run()
