# zombie_fast.py - Biến thể zombie chạy nhanh
from ursina import *
from entities.enemies.zombie_base import ZombieBase

class ZombieFast(ZombieBase):
    """
    Biến thể zombie chạy nhanh.
    Máu ít hơn, tốc độ cao hơn zombie thường.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(zombie_type='fast', position=position, player=player, **kwargs)

        self.attack_cooldown = 1.0  # Tấn công nhanh hơn

