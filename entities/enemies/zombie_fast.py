# zombie_fast.py - Biến thể zombie chạy nhanh
from ursina import *
from entities.enemies.zombie_base import ZombieBase
from core.config import ZOMBIE_FAST_SPEED, ZOMBIE_FAST_HEALTH


class ZombieFast(ZombieBase):
    """
    Biến thể zombie chạy nhanh.
    Máu ít hơn, tốc độ cao hơn zombie thường.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(position=position, player=player, **kwargs)

        # Override stats
        self.max_health = ZOMBIE_FAST_HEALTH
        self.health = self.max_health
        self.speed = ZOMBIE_FAST_SPEED
        self.attack_cooldown = 1.0  # Tấn công nhanh hơn

        # Ngoại hình khác biệt
        self.color = color.lime
