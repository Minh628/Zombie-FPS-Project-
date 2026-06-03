# zombie_base.py - Class gốc của zombie
from ursina import *
from direct.actor.Actor import Actor
from ursina.shaders import lit_with_shadows_shader
from core.config import (
    ZOMBIE_BASE_HEALTH, ZOMBIE_BASE_SPEED, ZOMBIE_BASE_DAMAGE,
    SOUNDS_DIR, MODELS_DIR
)
from core.utils import distance_between, direction_to


class ZombieBase(Entity):
    """
    Class gốc cho tất cả zombie.
    Xử lý: di chuyển về phía player (có collision), tấn công, nhận damage, chết.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(
            model=None,
            position=position,
            collider=None,
            **kwargs
        )

        self.actor = None
        self._anim_names = []
        self._current_anim = None
        self._walk_anim = None
        self._attack_anim = None
        self.facing_offset_y = 180
        self._setup_actor()
        self.player = player
        self.max_health = ZOMBIE_BASE_HEALTH
        self.health = self.max_health
        self.speed = ZOMBIE_BASE_SPEED
        self.damage = ZOMBIE_BASE_DAMAGE
        self.attack_range = 2.0
        self.attack_cooldown = 1.5
        self.can_attack = True
        self.is_alive = True
        self.vertical_velocity = 0.0
        self.gravity = 25.0
        self.ground_snap_distance = 0.6
        self.ground_check_distance = 6.0
        self.moan_interval = 4.5
        self._moan_timer = 0.0

        # Âm thanh zombie
        self.moan_sound = Audio(f'{SOUNDS_DIR}/zombie_moan.ogg', autoplay=False, loop=False)
        self.death_sound = Audio(f'{SOUNDS_DIR}/zombie_death.ogg', autoplay=False, loop=False)
        self.take_damage_sound = Audio(f'{SOUNDS_DIR}/zombie_take_damage.ogg', autoplay=False, loop=False)
        self.moan_sound.volume = 0.65
        self.death_sound.volume = 0.75
        self.take_damage_sound.volume = 0.85

        # Callbacks
        self.on_death = None

    def _setup_actor(self):
        model_path = f'{MODELS_DIR}/zombie/zombie26.glb'
        self.actor = Actor(model_path)
        self.model = self.actor
        try:
            self.actor.setColorScale(4,4,4,1)
            self.actor.set_shader_input('roughness', 0.8)
            self.actor.set_shader_input('metallic', 0.2)
        except Exception:
            pass


        try:
            self.actor.loadAnims({'anim': model_path})
            self._anim_names = list(self.actor.getAnimNames())
        except Exception:
            self._anim_names = []

        self._walk_anim = self._pick_anim(['Walk_InPlace', 'Walk', 'Run', 'Idle'])
        self._attack_anim = self._pick_anim(['Attack.001', 'Bite', 'Hit'])
        if self._walk_anim:
            self._play_anim(self._walk_anim)
        elif self._attack_anim:
            self._play_anim(self._attack_anim)
        self._print_anim_info()

        self.collider = 'box'

    def _pick_anim(self, keywords):
        if not self._anim_names:
            return None
        for keyword in keywords:
            for name in self._anim_names:
                if keyword.lower() in name.lower():
                    return name
        return self._anim_names[0]

    def _play_anim(self, name):
        if not name or name == self._current_anim:
            return
        try:
            self.actor.loop(name)
            self._current_anim = name
        except Exception:
            pass

    def _print_anim_info(self):
        print(f'[Zombie] Animations ({len(self._anim_names)}): {self._anim_names}')
        print(f'[Zombie] Current animation: {self._current_anim}')

    def update(self):
        """Di chuyển về phía player mỗi frame (có collision check)."""
        if not self.is_alive or not self.player:
            return

        # Tính hướng đến player
        direction = direction_to(self, self.player)
        direction.y = 0

        if direction.length() > 0:
            direction = direction.normalized()

        move_amount = direction * self.speed * time.dt

        # === COLLISION CHECK VÀ PATHFINDING CẢI TIẾN ===
        step_height = 0.6  # Chiều cao bậc thang tối đa
        ray_dist = self.speed * time.dt + 0.8

        low_origin = self.position + Vec3(0, 0.2, 0) # Tia gót chân
        high_origin = self.position + Vec3(0, 1.2, 0) # Tia ngực

        low_hit = raycast(origin=low_origin, direction=direction, distance=ray_dist, ignore=[self, self.player])
        high_hit = raycast(origin=high_origin, direction=direction, distance=ray_dist, ignore=[self, self.player])

        # Kiểm tra chướng ngại vật (bỏ qua entity sống như zombie khác)
        low_blocked = low_hit.hit and not hasattr(low_hit.entity, 'is_alive')
        high_blocked = high_hit.hit and not hasattr(high_hit.entity, 'is_alive')

        moved = False

        if not low_blocked and not high_blocked:
            # Đường trống hoàn toàn -> Di chuyển bình thường
            self.position += move_amount
            moved = True
        elif low_blocked and not high_blocked:
            # 1. Khả năng leo bậc thang (Step Climbing)
            # Tia dưới chạm, tia trên không chạm -> Bục thấp / Gờ đất
            self.y += step_height
            self.position += move_amount
            moved = True
        else:
            # 2. Né tường thông minh (Obstacle Avoidance / Steering)
            # Tia trên bị chặn -> Gặp tường cao
            import math
            angles = [45, -45, 90, -90]
            
            for angle in angles:
                rad = math.radians(angle)
                # Xoay vector direction đi 1 góc rad quanh trục Y
                new_dx = direction.x * math.cos(rad) - direction.z * math.sin(rad)
                new_dz = direction.x * math.sin(rad) + direction.z * math.cos(rad)
                test_dir = Vec3(new_dx, 0, new_dz).normalized()
                
                test_high = raycast(origin=high_origin, direction=test_dir, distance=ray_dist, ignore=[self, self.player])
                test_low = raycast(origin=low_origin, direction=test_dir, distance=ray_dist, ignore=[self, self.player])
                
                t_high_blocked = test_high.hit and not hasattr(test_high.entity, 'is_alive')
                t_low_blocked = test_low.hit and not hasattr(test_low.entity, 'is_alive')
                
                if not t_high_blocked:
                    # Nếu hướng mới có phía trên trống
                    if t_low_blocked:
                        # Có bậc thấp cản hướng này -> Leo lên
                        self.y += step_height
                    self.position += test_dir * self.speed * time.dt
                    moved = True
                    break

        self._apply_gravity_and_ground()

        # Quay mặt về phía player
        self.look_at_2d(self.player.position, axis='y')
        self.rotation_y += self.facing_offset_y



        # Rên rỉ định kỳ khi còn sống
        self._moan_timer += time.dt
        if self._moan_timer >= self.moan_interval:
            self._moan_timer = 0.0
            self._play_moan()

        # Kiểm tra tấn công
        dist = distance_between(self, self.player)
        if dist <= self.attack_range and self.can_attack:
            self.attack()
        elif dist > self.attack_range:
            self._play_anim(self._walk_anim)

    def _half_height(self):
        if hasattr(self, 'scale_y'):
            return self.scale_y * 0.5
        if isinstance(self.scale, Vec3):
            return self.scale.y * 0.5
        if isinstance(self.scale, (tuple, list)) and len(self.scale) >= 2:
            return self.scale[1] * 0.5
        return 1.0

    def _hit_world_y(self, hit):
        if hasattr(hit, 'world_point') and hit.world_point is not None:
            return hit.world_point.y
        if hasattr(hit, 'point') and hit.point is not None:
            return hit.point.y
        return None

    def _apply_gravity_and_ground(self):
        half_height = self._half_height()
        ray_origin = self.position + Vec3(0, half_height + 0.05, 0)
        hit_down = raycast(
            origin=ray_origin,
            direction=Vec3(0, -1, 0),
            distance=half_height + self.ground_check_distance,
            ignore=[self, self.player],
        )

        if hit_down.hit and not getattr(hit_down.entity, 'is_alive', False):
            ground_y = self._hit_world_y(hit_down)
            if ground_y is not None:
                target_y = ground_y + half_height
                if self.y <= target_y + self.ground_snap_distance and self.vertical_velocity <= 0:
                    self.y = target_y
                    self.vertical_velocity = 0.0
                    return

        self.vertical_velocity -= self.gravity * time.dt
        self.y += self.vertical_velocity * time.dt

    def attack(self):
        """Tấn công player khi đủ gần."""
        if not self.can_attack or not self.player:
            return

        self.can_attack = False
        self._play_moan()
        self._play_anim(self._attack_anim or "Attack")
        self.player.take_damage(self.damage)
        print(f'[Zombie] Attacked player for {self.damage} damage!')

        invoke(self._reset_attack, delay=self.attack_cooldown)

    def _reset_attack(self):
        """Reset cooldown tấn công."""
        self.can_attack = True

    def take_damage(self, damage):
        """Nhận sát thương từ vũ khí."""
        if not self.is_alive:
            return

        self.health -= damage
        self.health = max(0, self.health)
        self.take_damage_sound.play()

        # Hiệu ứng nhấp nháy đỏ khi trúng đạn
        if self.actor:
            self.actor.setColorScale(2, 0.5, 0.5, 1)
            invoke(self.actor.setColorScale, 4, 4, 4, 1, delay=0.15)
        else:
            self.blink(color.red, duration=0.15)

        print(f'[Zombie] Took {damage} damage! Health: {self.health}/{self.max_health}')

        if self.health <= 0:
            self.die()

    def die(self):
        """Xử lý khi zombie chết."""
        self.is_alive = False
        print('[Zombie] Zombie died!')

        
        invoke(self.death_sound.play, delay=0.18)

        if self.on_death:
            self.on_death(self)

        # Animation chết: thu nhỏ rồi destroy
        self.animate_scale(Vec3(0, 0, 0), duration=0.3)
        destroy(self, delay=0.5)

    def _play_moan(self):
        if not self.is_alive:
            return
        self.moan_sound.play()
