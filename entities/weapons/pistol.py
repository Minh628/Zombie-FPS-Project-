# pistol.py - Súng lục (Phím 2) - Vũ khí phụ
from ursina import *
from entities.weapon import WeaponBase
from core.config import (
    PISTOL_NAME, PISTOL_DAMAGE, PISTOL_FIRE_RATE,
    PISTOL_RELOAD_TIME, PISTOL_MAX_AMMO, PISTOL_TOTAL_AMMO, PISTOL_RANGE
)


class Pistol(WeaponBase):
    """
    Súng lục - vũ khí phụ.
    Sát thương thấp hơn, băng đạn nhỏ, nạp đạn nhanh.
    """

    def __init__(self, player, **kwargs):
        super().__init__(
            player=player,
            weapon_name=PISTOL_NAME,
            damage=PISTOL_DAMAGE,
            fire_rate=PISTOL_FIRE_RATE,
            reload_time=PISTOL_RELOAD_TIME,
            max_ammo=PISTOL_MAX_AMMO,
            total_ammo=PISTOL_TOTAL_AMMO,
            attack_range=PISTOL_RANGE,
            is_melee=False,
            model_scale=(0.06, 0.1, 0.3),
            model_color=color.rgb(80, 80, 80),
            model_pos=(0.45, -0.28, 0.4),
            **kwargs
        )
