# rifle.py - Súng trường (Phím 1) - Vũ khí chính
from ursina import *
from entities.weapon import WeaponBase
from core.config import (
    RIFLE_NAME, RIFLE_DAMAGE, RIFLE_FIRE_RATE,
    RIFLE_RELOAD_TIME, RIFLE_MAX_AMMO, RIFLE_TOTAL_AMMO, RIFLE_RANGE
)


class Rifle(WeaponBase):
    """
    Súng trường - vũ khí chính.
    Sát thương cao, tốc độ bắn nhanh, băng đạn lớn.
    Tương lai có thể tạo AK47, M4A1,... kế thừa từ class này.
    """

    def __init__(self, player, **kwargs):
        super().__init__(
            player=player,
            weapon_name=RIFLE_NAME,
            damage=RIFLE_DAMAGE,
            fire_rate=RIFLE_FIRE_RATE,
            reload_time=RIFLE_RELOAD_TIME,
            max_ammo=RIFLE_MAX_AMMO,
            total_ammo=RIFLE_TOTAL_AMMO,
            attack_range=RIFLE_RANGE,
            is_melee=False,
            model_scale=(0.08, 0.08, 0.6),
            model_color=color.rgb(60, 60, 60),
            model_pos=(0.5, -0.25, 0.5),
            **kwargs
        )
