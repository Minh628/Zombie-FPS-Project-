# knife.py - Dao (Phím 3) - Vũ khí cận chiến
from ursina import *
from entities.weapon import WeaponBase
from core.config import (
    KNIFE_NAME, KNIFE_DAMAGE, KNIFE_ATTACK_RATE, KNIFE_RANGE,
    MODELS_DIR
)


class Knife(WeaponBase):
    """
    Dao - vũ khí cận chiến.
    Tầm đánh ngắn, sát thương cao, không cần đạn.
    """

    def __init__(self, player, **kwargs):
        super().__init__(
            player=player,
            weapon_name=KNIFE_NAME,
            damage=KNIFE_DAMAGE,
            fire_rate=KNIFE_ATTACK_RATE,
            reload_time=0,             # Cận chiến không cần nạp đạn
            max_ammo=0,
            total_ammo=0,
            attack_range=KNIFE_RANGE,
            is_melee=True,
            model_scale=(1, 1, 1),
            model_pos=(0.397, -0.319,1.613), # Vị trí dao bên phải màn hình
            **kwargs
        )
        
       
        self.model = None
        self.color = color.white

       
        self.pivot = Entity(
            parent=self,
            rotation=(3.262,50.688 ,-287.966) 
        )
        
        # Tâm model đã khá chuẩn (~0), scale factor 0.02 để thu nhỏ dao lại theo yêu cầu
        scale_factor = 0.02
        
        # Load model 3D thực tế (gltf sẽ tự động load texture và material đi kèm)
        self.knife_model = Entity(
            parent=self.pivot,
            model=f'{MODELS_DIR}/knife/knife.gltf',
            scale=scale_factor,
            position=(0, 0, 0)
        )

        # Lưu lại điểm gốc để làm animation trở về vị trí cũ sau khi chém
        self._base_pos = Vec3(0.397, -0.319, 1.613) # Đã đồng bộ với model_pos bạn tự tune
        self._base_rot = Vec3(0, 0, 0)

    def shoot(self, automatic=False):
        """Override: Hành động chém dao."""
        if automatic:
            return  # Dao không chém liên tục khi giữ chuột
            
        if not self.can_shoot:
            return

        self.can_shoot = False

        # Raycast từ camera để check trúng mục tiêu
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.attack_range,
            ignore=[self.player, ]
        )

        if hit_info.hit:
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(self.damage)
                print(f'[{self.weapon_name}] Slashed for {self.damage} damage!')
            else:
                impact = Entity(
                    model='sphere', scale=0.05,
                    position=hit_info.world_point, color=color.gray
                )
                destroy(impact, delay=0.5)

        self._notify_ammo()
        
        # Gọi hoạt ảnh chém
        self._slash_effect()
        
        invoke(self._reset_shoot, delay=self.fire_rate)

    def _slash_effect(self):
        """Hiệu ứng vung dao đâm/chém về phía trước chân thật."""
        
        self.animate_position(self._base_pos + Vec3(-0.1, -0.1, 0.4), duration=0.1)
        self.animate_rotation(self._base_rot + Vec3(40, -10, 0), duration=0.1)
        
        # 2. Sau 0.1s, đưa dao quay trở lại vị trí và góc quay ban đầu một cách mượt mà
        invoke(lambda: self.animate_position(self._base_pos, duration=0.2), delay=0.1)
        invoke(lambda: self.animate_rotation(self._base_rot, duration=0.2), delay=0.1)


         