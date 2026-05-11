# zombie_base.py - Class gốc của zombie
from ursina import *
from core.config import ZOMBIE_BASE_HEALTH, ZOMBIE_BASE_SPEED, ZOMBIE_BASE_DAMAGE
from core.utils import distance_between, direction_to


class ZombieBase(Entity):
    """
    Class gốc cho tất cả zombie.
    Xử lý: di chuyển về phía player, tấn công, nhận damage, chết.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(
            model='cube',
            scale=(1, 2, 1),
            color=color.green,
            position=position,
            collider='box',
            **kwargs
        )
        self.player = player
        self.max_health = ZOMBIE_BASE_HEALTH
        self.health = self.max_health
        self.speed = ZOMBIE_BASE_SPEED
        self.damage = ZOMBIE_BASE_DAMAGE
        self.attack_range = 2.0
        self.attack_cooldown = 1.5
        self.can_attack = True
        self.is_alive = True

        # Callbacks
        self.on_death = None

    def update(self):
        """Di chuyển về phía player mỗi frame."""
        if not self.is_alive or not self.player:
            return

        # Tính hướng đến player
        direction = direction_to(self, self.player)
        direction.y = 0  # Không di chuyển theo trục Y

        # Di chuyển
        self.position += direction * self.speed * time.dt

        # Quay mặt về phía player
        self.look_at_2d(self.player.position, axis='y')

        # Kiểm tra tấn công
        dist = distance_between(self, self.player)
        if dist <= self.attack_range and self.can_attack:
            self.attack()

    def attack(self):
        """Tấn công player khi đủ gần."""
        if not self.can_attack or not self.player:
            return

        self.can_attack = False
        self.player.take_damage(self.damage)
        print(f'[Zombie] Attacked player for {self.damage} damage!')

        invoke(self._reset_attack, delay=self.attack_cooldown)

    def _reset_attack(self):
        """Reset cooldown tấn công."""
        self.can_attack = True

    def take_damage(self, damage):
        """Nhận sát thương từ vũ khí."""
        if not self.is_alive:
            return

        self.health -= damage
        self.health = max(0, self.health)

        # Hiệu ứng nhấp nháy đỏ khi trúng đạn
        self.blink(color.red, duration=0.15)

        print(f'[Zombie] Took {damage} damage! Health: {self.health}/{self.max_health}')

        if self.health <= 0:
            self.die()

    def die(self):
        """Xử lý khi zombie chết."""
        self.is_alive = False
        print('[Zombie] Zombie died!')

        if self.on_death:
            self.on_death(self)

        # Animation chết: thu nhỏ rồi destroy
        self.animate_scale(Vec3(0, 0, 0), duration=0.3)
        destroy(self, delay=0.5)
