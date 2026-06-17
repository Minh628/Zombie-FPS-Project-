# pistol.py - Súng lục (Phím 2) - Vũ khí phụ
from ursina import *
from entities.weapon import WeaponBase
from core.config import (
    PISTOL_NAME, PISTOL_DAMAGE, PISTOL_FIRE_RATE,
    PISTOL_RELOAD_TIME, PISTOL_MAX_AMMO, PISTOL_TOTAL_AMMO, PISTOL_RANGE,
    MODELS_DIR, SOUNDS_DIR
)


class Pistol(WeaponBase):
    """
    Súng lục Pistol.
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
            model_scale=(1, 1, 1),         
            model_pos=(0.4, -0.4, 1.2),   
            **kwargs
        )
        # Xóa khối hình hộp chữ nhật mặc định
        self.model = None
        
        # Trục Pivot (bản lề) dùng để bọc model 3D lại, cho phép xoay nòng súng hướng về phía trước
        # mà không làm ảnh hưởng đến code quản lý vị trí chung của WeaponBase.
        self.pivot = Entity(
            parent=self,
            rotation=(0, 80, 10) 
        )
        self.shoot_sound = Audio(f'{SOUNDS_DIR}/pistol_shoot.mp3', autoplay=False, loop=False)
        self.shoot_sound.volume = 0.9
        
        # Tâm vật lý thực tế của file 3D tải trên mạng thường bị lệch
        raw_center = Vec3(-3.75, -1.89, 2.91)
        scale_factor = 0.04  # Căn chỉnh thu nhỏ để súng vừa vặn với tay người chơi
        
        self.gun_model = Entity(
            parent=self.pivot,
            model=f'{MODELS_DIR}/pistol/scene.gltf',
            color=color.white,
            scale=scale_factor,
            position=-raw_center * scale_factor # Bù lại tọa độ lệch
        )

        # Cập nhật vị trí gốc (dùng cho hiệu ứng giật súng)
        self._base_pos = Vec3(0.4, -0.4, 1.2)
    def on_shoot(self, automatic):
        """Hook phát âm thanh khi bắn thành công."""
        try:
            self.shoot_sound.play()
        except Exception:
            pass
    def _recoil(self):
        """
        Hiệu ứng giật súng (Recoil).
        Súng lục có khối lượng nhẹ nên độ giật lùi (trục Z âm) và thời gian phản hồi (duration) sẽ ngắn và nhanh hơn AK47.
        """
        # 1. Súng nảy nhẹ về phía sau
        self.animate_position(
            self._base_pos + Vec3(0, 0.03, -0.06), duration=0.03
        )
        invoke(
            lambda: self.animate_position(self._base_pos, duration=0.1),
            delay=0.03
        )

        # Giật camera lên (ít hơn AK47)
        if hasattr(self.player, 'camera_pivot'):
            self.player.camera_pivot.rotation_x -= 0.8
            # Phục hồi một phần độ giật
            invoke(lambda: setattr(self.player.camera_pivot, 'rotation_x', self.player.camera_pivot.rotation_x + 0.3), delay=0.06)
            
        # Hiệu ứng lửa đạn (Muzzle flash)
        self.create_muzzle_flash(position=Vec3(0, 0.15, 0.6), scale=0.05, flash_color=color.orange)