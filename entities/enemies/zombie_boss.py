# zombie_boss.py - Biến thể zombie boss
from ursina import *
from entities.enemies.zombie_base import ZombieBase

class ZombieBoss(ZombieBase):
    """
    Biến thể zombie boss.
    Máu trâu, dame to, đi chậm. Kích thước lớn hơn.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(zombie_type='boss', position=position, player=player, **kwargs)

        self.scale = Vec3(1.5, 1.5, 1.5)  # To hơn bình thường
        self.attack_cooldown = 2.0  # Tấn công chậm hơn
        self.attack_range = 3.0 # Tầm đánh xa hơn
        
        # Health bar bg cần scale lại xíu hoặc vị trí y cao hơn
        if hasattr(self, 'health_bar_bg'):
            self.health_bar_bg.y = 3.5

    def spawn_from_pool(self, position, player):
        super().spawn_from_pool(position, player)
        self.scale = Vec3(1.5, 1.5, 1.5) # Reset lại scale to
