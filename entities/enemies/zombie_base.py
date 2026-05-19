# zombie_base.py - Class gốc của zombie
from ursina import *
from core.config import ZOMBIE_BASE_HEALTH, ZOMBIE_BASE_SPEED, ZOMBIE_BASE_DAMAGE
from core.config import SOUNDS_DIR
from core.utils import distance_between, direction_to


class ZombieBase(Entity):
    """
    Class gốc cho tất cả zombie.
    Xử lý: di chuyển về phía player (có collision), tấn công, nhận damage, chết.
    """

    def __init__(self, position=Vec3(0, 0, 0), player=None, **kwargs):
        super().__init__(
            model='assets/models/zombie/zombie.gltf',
            scale=(1, 2, 1),
            color=color.white,
            position=position,
            collider='box',
            **kwargs
        )
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

        # === COLLISION CHECK: kiểm tra trước khi di chuyển ===
        # Raycast phía trước để tránh xuyên tường
        forward_origin = self.position + Vec3(0, max(0.2, self._half_height()), 0)
        hit = raycast(
            origin=forward_origin,
            direction=direction,
            distance=self.speed * time.dt + 0.8,
            ignore=[self, self.player],
        )

        if not hit.hit or (hasattr(hit.entity, 'is_alive')):
            # Không có vật cản hoặc đó là zombie khác → di chuyển
            self.position += move_amount
        else:
            # Có tường/vật cản → thử trượt sang bên
            # Thử di chuyển theo trục X
            side_dir = Vec3(direction.z, 0, -direction.x).normalized()
            side_hit = raycast(
                origin=forward_origin,
                direction=side_dir,
                distance=self.speed * time.dt + 0.8,
                ignore=[self, self.player],
            )
            if not side_hit.hit:
                self.position += side_dir * self.speed * time.dt * 0.5

        self._apply_gravity_and_ground()

        # Quay mặt về phía player
        self.look_at_2d(self.player.position, axis='y')

        # Rên rỉ định kỳ khi còn sống
        self._moan_timer += time.dt
        if self._moan_timer >= self.moan_interval:
            self._moan_timer = 0.0
            self._play_moan()

        # Kiểm tra tấn công
        dist = distance_between(self, self.player)
        if dist <= self.attack_range and self.can_attack:
            self.attack()

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
