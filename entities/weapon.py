# weapon.py - Xử lý súng (raycast, cooldown, nạp đạn)
from ursina import *
from core.config import (
    WEAPON_DAMAGE, WEAPON_FIRE_RATE, WEAPON_RELOAD_TIME,
    WEAPON_MAX_AMMO, WEAPON_TOTAL_AMMO
)


class Weapon(Entity):
    """
    Xử lý vũ khí của người chơi.
    Bao gồm: bắn (raycast), cooldown, nạp đạn, hiệu ứng.
    """

    def __init__(self, player, **kwargs):
        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=(0.15, 0.15, 0.5),
            position=(0.5, -0.3, 0.5),
            color=color.dark_gray,
            **kwargs
        )
        self.player = player
        self.damage = WEAPON_DAMAGE
        self.fire_rate = WEAPON_FIRE_RATE
        self.reload_time = WEAPON_RELOAD_TIME
        self.max_ammo = WEAPON_MAX_AMMO
        self.current_ammo = self.max_ammo
        self.total_ammo = WEAPON_TOTAL_AMMO
        self.can_shoot = True
        self.is_reloading = False

        # Callbacks để thông báo cho HUD
        self.on_ammo_changed = None

    def input(self, key):
        """Xử lý input bắn và nạp đạn."""
        if key == 'left mouse down':
            self.shoot()
        elif key == 'r':
            self.reload()

    def shoot(self):
        """Bắn một viên đạn bằng raycast."""
        if not self.can_shoot or self.is_reloading or self.current_ammo <= 0:
            if self.current_ammo <= 0:
                print('[Weapon] Out of ammo! Press R to reload.')
            return

        self.can_shoot = False
        self.current_ammo -= 1

        # Raycast từ camera về phía trước
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=100,
            ignore=[self.player, ]
        )

        if hit_info.hit:
            # Kiểm tra nếu trúng zombie
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(self.damage)
                print(f'[Weapon] Hit {hit_info.entity} for {self.damage} damage!')
            else:
                # Hiệu ứng đạn trúng tường/sàn
                impact = Entity(
                    model='sphere',
                    scale=0.05,
                    position=hit_info.world_point,
                    color=color.yellow
                )
                destroy(impact, delay=0.5)

        # Cập nhật HUD
        if self.on_ammo_changed:
            self.on_ammo_changed(self.current_ammo, self.total_ammo)

        # Hiệu ứng giật súng
        self._recoil()

        # Cooldown
        invoke(self._reset_shoot, delay=self.fire_rate)

        # Tự động nạp đạn khi hết
        if self.current_ammo <= 0 and self.total_ammo > 0:
            invoke(self.reload, delay=0.5)

    def _recoil(self):
        """Hiệu ứng giật súng khi bắn."""
        original_pos = self.position
        self.animate_position(
            self.position + Vec3(0, 0.02, -0.05),
            duration=0.05
        )
        invoke(
            lambda: self.animate_position(original_pos, duration=0.1),
            delay=0.05
        )

    def _reset_shoot(self):
        """Reset trạng thái cho phép bắn tiếp."""
        self.can_shoot = True

    def reload(self):
        """Nạp đạn."""
        if self.is_reloading or self.current_ammo == self.max_ammo or self.total_ammo <= 0:
            return

        self.is_reloading = True
        print(f'[Weapon] Reloading... ({self.reload_time}s)')

        invoke(self._finish_reload, delay=self.reload_time)

    def _finish_reload(self):
        """Hoàn tất nạp đạn."""
        ammo_needed = self.max_ammo - self.current_ammo
        ammo_to_load = min(ammo_needed, self.total_ammo)

        self.current_ammo += ammo_to_load
        self.total_ammo -= ammo_to_load
        self.is_reloading = False

        print(f'[Weapon] Reloaded! Ammo: {self.current_ammo}/{self.total_ammo}')

        if self.on_ammo_changed:
            self.on_ammo_changed(self.current_ammo, self.total_ammo)
