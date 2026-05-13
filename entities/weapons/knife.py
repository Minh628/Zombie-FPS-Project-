# knife.py - Dao (Phím 3) - Vũ khí cận chiến
from ursina import *
from entities.weapon import WeaponBase
from core.config import KNIFE_NAME, KNIFE_DAMAGE, KNIFE_ATTACK_RATE, KNIFE_RANGE


class Knife(WeaponBase):
    """
    Dao - vũ khí cận chiến.
    Sát thương rất cao, tầm đánh ngắn, không cần đạn.
    """

    def __init__(self, player, **kwargs):
        super().__init__(
            player=player,
            weapon_name=KNIFE_NAME,
            damage=KNIFE_DAMAGE,
            fire_rate=KNIFE_ATTACK_RATE,
            reload_time=0,
            max_ammo=0,
            total_ammo=0,
            attack_range=KNIFE_RANGE,
            is_melee=True,
            model_scale=(0.03, 0.2, 0.4),
            model_color=color.light_gray,
            model_pos=(0.45, -0.2, 0.4),
            **kwargs
        )

    def shoot(self):
        """Override: tấn công cận chiến."""
        if not self.can_shoot:
            return

        self.can_shoot = False

        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.attack_range,
            ignore=[self.player, ]
        )

        if hit_info.hit:
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(self.damage)
                print(f'[Knife] Slashed for {self.damage} damage!')

        self._notify_ammo()
        self._slash_effect()
        invoke(self._reset_shoot, delay=self.fire_rate)

    def _slash_effect(self):
        """Hiệu ứng chém dao."""
        self.animate_rotation(Vec3(0, 0, -45), duration=0.1)
        invoke(
            lambda: self.animate_rotation(Vec3(0, 0, 0), duration=0.15),
            delay=0.1
        )
