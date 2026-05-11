# player.py - Kế thừa FirstPersonController, xử lý máu, di chuyển
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from core.config import (
    PLAYER_MAX_HEALTH, PLAYER_MOVE_SPEED, PLAYER_SPRINT_SPEED,
    PLAYER_JUMP_HEIGHT, MOUSE_SENSITIVITY
)


class Player(FirstPersonController):
    """
    Nhân vật người chơi - kế thừa FirstPersonController của Ursina.
    Xử lý: di chuyển, nhảy, chạy nhanh, nhận sát thương, chết.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.speed = PLAYER_MOVE_SPEED
        self.sprint_speed = PLAYER_SPRINT_SPEED
        self.jump_height = PLAYER_JUMP_HEIGHT
        self.mouse_sensitivity = Vec2(MOUSE_SENSITIVITY, MOUSE_SENSITIVITY)
        self.is_alive = True
        self.is_sprinting = False

        # Callbacks để thông báo cho HUD
        self.on_health_changed = None
        self.on_death = None

    def update(self):
        """Cập nhật mỗi frame."""
        if not self.is_alive:
            return

        super().update()

        # Sprint khi giữ Shift
        if held_keys['left shift']:
            self.speed = self.sprint_speed
            self.is_sprinting = True
        else:
            self.speed = PLAYER_MOVE_SPEED
            self.is_sprinting = False

    def take_damage(self, damage):
        """Nhận sát thương từ zombie."""
        if not self.is_alive:
            return

        self.health -= damage
        self.health = max(0, self.health)

        print(f'[Player] Took {damage} damage! Health: {self.health}/{self.max_health}')

        # Gọi callback cập nhật HUD
        if self.on_health_changed:
            self.on_health_changed(self.health, self.max_health)

        if self.health <= 0:
            self.die()

    def heal(self, amount):
        """Hồi máu."""
        self.health = min(self.max_health, self.health + amount)
        if self.on_health_changed:
            self.on_health_changed(self.health, self.max_health)

    def die(self):
        """Xử lý khi người chơi chết."""
        self.is_alive = False
        print('[Player] Player died!')
        if self.on_death:
            self.on_death()

    def respawn(self, position=Vec3(0, 1, 0)):
        """Hồi sinh người chơi."""
        self.health = self.max_health
        self.is_alive = True
        self.position = position
        if self.on_health_changed:
            self.on_health_changed(self.health, self.max_health)
        print('[Player] Player respawned!')
