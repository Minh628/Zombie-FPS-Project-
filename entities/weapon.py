# weapon.py - Class gốc (Base) cho tất cả vũ khí.
# Vũ khí KHÔNG tự xử lý input. Player sẽ gọi shoot()/reload().
from ursina import *


class WeaponBase(Entity):
    """
    Class gốc cho tất cả vũ khí.
    Chỉ chứa logic: bắn, reload, recoil, ammo.
    Player sẽ gọi shoot()/reload() thông qua input của mình.
    """

    def __init__(self, player, weapon_name='Weapon', damage=25,
                 fire_rate=0.15, reload_time=2.0, max_ammo=30,
                 total_ammo=120, attack_range=100, is_melee=False,
                 model_scale=(0.15, 0.15, 0.5),
                 model_color=None,
                 model_pos=(0.5, -0.3, 0.5), **kwargs):
        if model_color is None:
            model_color = color.dark_gray

        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=model_scale,
            position=model_pos,
            color=model_color,
            **kwargs
        )
        self.player = player
        self.weapon_name = weapon_name
        self.damage = damage
        self.fire_rate = fire_rate
        self.reload_time = reload_time
        self.max_ammo = max_ammo
        self.current_ammo = max_ammo
        self.total_ammo = total_ammo
        self.max_total_ammo = total_ammo
        self.attack_range = attack_range
        self.is_melee = is_melee
        self.can_shoot = True
        self.is_reloading = False

        # Vị trí gốc (reset sau recoil)
        self._base_pos = Vec3(*model_pos)

        # Callback → HUD
        self.on_ammo_changed = None

    # KHÔNG có input() - Player sẽ gọi trực tiếp

    def shoot(self, automatic=False):
        """Bắn / tấn công. Có thể override ở class con."""
        if not self.can_shoot or self.is_reloading:
            return

        if not self.is_melee:
            if self.current_ammo <= 0:
                print(f'[{self.weapon_name}] Out of ammo! Press R to reload.')
                return
            self.current_ammo -= 1

        self.can_shoot = False

        # Raycast từ camera
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.attack_range,
            ignore=[self.player, ]
        )

        if hit_info.hit:
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(self.damage)
                print(f'[{self.weapon_name}] Hit for {self.damage} damage!')
            else:
                impact = Entity(
                    model='sphere', scale=0.05,
                    position=hit_info.world_point, color=color.yellow
                )
                destroy(impact, delay=0.5)

        self._notify_ammo()
        self._recoil()
        invoke(self._reset_shoot, delay=self.fire_rate)

        if not self.is_melee and self.current_ammo <= 0 and self.total_ammo > 0:
            invoke(self.reload, delay=0.5)

    def _recoil(self):
        """Hiệu ứng giật."""
        self.animate_position(
            self._base_pos + Vec3(0, 0.02, -0.05), duration=0.05
        )
        invoke(
            lambda: self.animate_position(self._base_pos, duration=0.1),
            delay=0.05
        )

    def _reset_shoot(self):
        self.can_shoot = True

    def reload(self):
        """Nạp đạn."""
        if self.is_melee:
            return
        if self.is_reloading or self.current_ammo == self.max_ammo or self.total_ammo <= 0:
            return
        self.is_reloading = True
        print(f'[{self.weapon_name}] Reloading...')
        invoke(self._finish_reload, delay=self.reload_time)

    def _finish_reload(self):
        ammo_needed = self.max_ammo - self.current_ammo
        ammo_to_load = min(ammo_needed, self.total_ammo)
        self.current_ammo += ammo_to_load
        self.total_ammo -= ammo_to_load
        self.is_reloading = False
        print(f'[{self.weapon_name}] Reloaded! {self.current_ammo}/{self.total_ammo}')
        self._notify_ammo()

    def _notify_ammo(self):
        if self.on_ammo_changed:
            if self.is_melee:
                self.on_ammo_changed(-1, -1)
            else:
                self.on_ammo_changed(self.current_ammo, self.total_ammo)

    def refill_ammo(self):
        """Nạp đầy đạn (cả băng đạn và đạn dự trữ)."""
        if self.is_melee:
            return
        self.current_ammo = self.max_ammo
        self.total_ammo = self.max_total_ammo
        self.is_reloading = False
        self.can_shoot = True
        print(f'[{self.weapon_name}] Ammo fully refilled!')
        self._notify_ammo()

    def reset_ammo(self):
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.can_shoot = True


Weapon = WeaponBase
