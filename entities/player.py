# player.py - Kế thừa FirstPersonController, xử lý máu, di chuyển, vũ khí (inventory)
# Player tự chứa danh sách vũ khí, tự bắn/reload/switch khi nhấn phím.
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from core.config import (
    PLAYER_MAX_HEALTH, PLAYER_MOVE_SPEED, PLAYER_SPRINT_SPEED,
    PLAYER_JUMP_HEIGHT, MOUSE_SENSITIVITY,
    
    PISTOL_TOTAL_AMMO, AK47_TOTAL_AMMO
)
from entities.weapons.ak47 import AK47
from entities.weapons.pistol import Pistol
from entities.weapons.knife import Knife


class Player(FirstPersonController):
    """
    Nhân vật người chơi - kế thừa FirstPersonController của Ursina.
    Xử lý: di chuyển, nhảy, chạy nhanh, nhận sát thương, chết.
    Chứa inventory vũ khí: tự bắn, reload, switch khi nhấn phím.
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

        # === VŨ KHÍ (Player tự chứa) ===
        # 1: AK47, 2: Pistol, 3: Knife
        self.weapons = [AK47(self), Pistol(self), Knife(self)]
        self.current_weapon_index = 0
        for w in self.weapons:
            w.enabled = False

        # Callbacks
        self.on_health_changed = None   # → UIManager (máu)
        self.on_death = None            # → GameManager
        self.on_weapon_changed = None   # → UIManager (tên vũ khí + đạn)

    @property
    def current_weapon(self):
        """Vũ khí đang cầm."""
        return self.weapons[self.current_weapon_index]

    # ==============================================================
    # VŨ KHÍ
    # ==============================================================

    def _set_active_weapon(self, index):
        """Helper quản lý việc chuyển đổi vũ khí: tắt tất cả, bật vũ khí được chọn."""
        if index < 0 or index >= len(self.weapons):
            return
            
        for w in self.weapons:
            w.enabled = False
            w.on_ammo_changed = None
            
        self.current_weapon_index = index
        self.current_weapon.enabled = True
        if self.on_weapon_changed:
            self.on_weapon_changed(self.current_weapon)

    def switch_weapon(self, index):
        """Chuyển vũ khí (dùng phím)."""
        if index == self.current_weapon_index:
            return
        self._set_active_weapon(index)
        print(f'[Player] Switched to {self.current_weapon.weapon_name}')

    def equip_default_weapon(self):
        """Trang bị AK47 (vũ khí mặc định)."""
        self._set_active_weapon(0)

    def reset_weapons(self):
        """Reset tất cả vũ khí về đạn đầy (sử dụng logic nạp lại của từng súng)."""
        for w in self.weapons:
            if hasattr(w, 'refill_ammo'):
                w.refill_ammo()
            else:
                w.reset_ammo()
        self.equip_default_weapon()

    def disable_weapons(self):
        """Ẩn tất cả vũ khí (khi chết hoặc game over)."""
        for w in self.weapons:
            w.enabled = False
            w.on_ammo_changed = None

    # ==============================================================
    # UPDATE
    # ==============================================================

    def update(self):
        """Cập nhật mỗi frame."""
        if not self.is_alive:
            return
        super().update()

        if held_keys['left mouse']:
            self.attack(automatic=True)
        # Sprint khi giữ Shift
        if held_keys['left shift']:
            self.speed = self.sprint_speed
            self.is_sprinting = True
        else:
            self.speed = PLAYER_MOVE_SPEED
            self.is_sprinting = False

    # ==============================================================
    # INPUT - Player tự bắn, reload, switch
    # ==============================================================

    def input(self, key):
        """Xử lý tất cả input của player."""
        if not self.is_alive:
            return

        # Gọi FirstPersonController.input() để xử lý nhảy (SPACE) và các phím mặc định
        super().input(key)

        # Bắn
        if key == 'left mouse down':
            self.attack(automatic=False)

        # Nạp đạn
        elif key == 'r':
            self.current_weapon.reload()

        # Chuyển vũ khí
        elif key == '1':
            self.switch_weapon(0) # AK47
        elif key == '2':
            self.switch_weapon(1) # Pistol
        elif key == '3':
            self.switch_weapon(2) # Knife

    # ==============================================================
    # MÁU & CHẾT
    # ==============================================================

    def attack(self,automatic=False):
        self.current_weapon.shoot(automatic=automatic)

    def take_damage(self, damage):
        """Nhận sát thương."""
        if not self.is_alive:
            return
        self.health -= damage
        self.health = max(0, self.health)
        print(f'[Player] Took {damage} damage! Health: {self.health}/{self.max_health}')
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
        """Xử lý khi chết."""
        self.is_alive = False
        print('[Player] Player died!')
        if self.on_death:
            self.on_death()

    def respawn(self, position=Vec3(60, 1, 0)):
        """Hồi sinh."""
        self.health = self.max_health
        self.is_alive = True
        self.rotation = Vec3(0, -90, 0)  # Quay mặt về phía trước
        self.position = position
        if self.on_health_changed:
            self.on_health_changed(self.health, self.max_health)
        print('[Player] Player respawned!')
