from ursina import *
from core.config import MODELS_DIR
class AmmoBox(Entity):
    """
    Hộp đạn spawn ở các wave. Khi player chạm vào sẽ nạp đầy băng đạn hiện tại.
    """
    def __init__(self, position, player, **kwargs):
        super().__init__(
            model=f'{MODELS_DIR}/items/ammoBox.gltf',
            position=position,
            scale=0.3,
            collider='box',
            **kwargs
        )
        self.player = player
        self.is_active = True

    def update(self):
        if not self.is_active or not self.player:
            return
            
        # Rotate for visual effect
        self.rotation_y += 50 * time.dt
        
        # Check collision with player
        if distance(self.position, self.player.position) < 2.0:
            self.pickup()
            
    def pickup(self):
        self.is_active = False
        
        # Trigger full ammo refill
        if hasattr(self.player, 'current_weapon'):
            wpn = self.player.current_weapon
            if wpn:
                wpn.refill_ammo()
                
        # Optional: play a sound if you want (uncomment and adjust if needed)
        # from core.config import SOUNDS_DIR
        # Audio(f'{SOUNDS_DIR}/reload_sound_of_an_AK47_chambering_a_round.mp3', autoplay=True, volume=0.8)
        
        destroy(self)
