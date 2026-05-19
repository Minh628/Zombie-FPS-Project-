# ak47.py - Súng AK47 Dragon (Phím 4)
from ursina import *
from entities.weapon import WeaponBase
from core.config import (
    AK47_NAME, AK47_DAMAGE, AK47_FIRE_RATE,
    AK47_RELOAD_TIME, AK47_MAX_AMMO, AK47_TOTAL_AMMO, AK47_RANGE,
    MODELS_DIR, TEXTURES_DIR
)


class AK47(WeaponBase):
    """
    Súng AK47 Dragon.
    """

    def __init__(self, player, **kwargs):
        # Scale gốc của entity là 1, ta sẽ dùng entity con để chứa model
        super().__init__(
            player=player,
            weapon_name=AK47_NAME,
            damage=AK47_DAMAGE,
            fire_rate=AK47_FIRE_RATE,
            reload_time=AK47_RELOAD_TIME,
            max_ammo=AK47_MAX_AMMO,
            total_ammo=AK47_TOTAL_AMMO,
            attack_range=AK47_RANGE,
            is_melee=False,
            model_scale=(1, 1, 1),
            model_pos=(0.400, -0.500, 1.200), # Vị trí súng dời vào giữa hơn
            **kwargs
        )
        # Xóa khối vuông mặc định
        self.model = None
        
        # Tạo Pivot (trục quay) để xoay súng cho nòng hướng về phía trước
        self.pivot = Entity(
            parent=self,
            rotation=(0.468,75.711,10.480) # Xoay súng (thử -90 hoặc 90 nếu bị ngược)
        )
        
        # Tạo Mesh Entity và dời nó để tâm súng trùng với Pivot
        # Dựa trên test, model gốc to gấp hàng trăm lần (X=130) và bị lệch tâm
        raw_center = Vec3(-26.0, 20.8, 6.8)
        scale_factor = 0.02 # Tăng kích thước lên to gấp 3 lần cũ (0.02)
        
        self.gun_model = Entity(
            parent=self.pivot,
            model=f'{MODELS_DIR}/ak47_dragon.obj',
            texture=f'{TEXTURES_DIR}/ak47_dragon.tga.png',
            color=color.white,
            scale=scale_factor,
            position=-raw_center * scale_factor # Bù lại khoảng lệch tâm
        )

        # Cập nhật vị trí gốc (dùng cho _recoil)
        self._base_pos = Vec3(0.400, -0.500, 1.200)

    def _recoil(self):
        """Hiệu ứng giật"""
        # Súng giật lùi
        self.animate_position(
            self._base_pos + Vec3(0, 0.05, -0.1), duration=0.05
        )
        invoke(
            lambda: self.animate_position(self._base_pos, duration=0.15),
            delay=0.05
        )
        
        # Giật camera lên
        if hasattr(self.player, 'camera_pivot'):
            self.player.camera_pivot.rotation_x -= 1.5
            # Phục hồi một phần độ giật để camera không bị lệch lên quá nhanh
            invoke(lambda: setattr(self.player.camera_pivot, 'rotation_x', self.player.camera_pivot.rotation_x + 0.5), delay=0.08)
            
        # Hiệu ứng lửa đạn (Muzzle flash)
        muzzle_flash = Entity(
            parent=self,
            model='sphere',
            color=color.yellow,
            scale=0.08,
            position=Vec3(-0.05, 0.1, 0.8), # Vị trí đầu nòng súng (khoảng chừng)
            unlit=True
        )
        destroy(muzzle_flash, delay=0.05)
