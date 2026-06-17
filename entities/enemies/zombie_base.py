# zombie_base.py - Class gốc của zombie (Tối ưu: Object Pooling + Distance Culling)
from ursina import *
from direct.actor.Actor import Actor
from core.config import (
    ZOMBIE_CONFIG,
    SOUNDS_DIR, MODELS_DIR
)
from core.utils import distance_between, direction_to
from core.pathfinding import NavGraph


class ZombieBase(Entity):
    """
    Class gốc cho tất cả zombie.
    Xử lý: di chuyển về phía player (có collision), tấn công, nhận damage, chết.
    Tối ưu: Object Pooling (spawn/despawn) + Distance Culling (ẩn render khi xa).
    """

    def __init__(self, zombie_type='normal', position=Vec3(0, 0, 0), player=None, **kwargs):
        self.zombie_type = zombie_type  # Lưu lại loại zombie để quản lý pool
        self.cfg = ZOMBIE_CONFIG[zombie_type]
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
        self._setup_sounds()
        self._setup_ui()

        self.player = player
        self.max_health = self.cfg['health']
        self.health = self.max_health
        self.speed = self.cfg['speed']
        self.damage = self.cfg['damage']
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

        # --- Pathfinding (A* Cache) ---
        self.current_path = []
        self.path_recalc_timer = 0.0
        self._los_timer = 0.0
        
        # --- Physics Caching ---
        self._physics_timer = 0.0
        self._cached_low_blocked = False
        self._cached_high_blocked = False
        self._cached_slide_dir = None
        self._cached_los_hit = True # Mặc định là bị block
        
        self._was_visible = True

        # Callbacks
        self.on_death = None

    def _setup_sounds(self):
        """Khởi tạo âm thanh"""
        self.moan_sound = Audio(f'{SOUNDS_DIR}/zombie_moan.ogg', autoplay=False, loop=False)
        self.death_sound = Audio(f'{SOUNDS_DIR}/zombie_death.ogg', autoplay=False, loop=False)
        self.take_damage_sound = Audio(f'{SOUNDS_DIR}/zombie_take_damage.ogg', autoplay=False, loop=False)
        self.moan_sound.volume = 0.65
        self.death_sound.volume = 0.75
        self.take_damage_sound.volume = 0.85

    def _setup_ui(self):
        """Khởi tạo giao diện thanh máu 3D"""
        self.health_bar_bg = Entity(
            parent=self,
            y=2.5, # Độ cao trên đầu
            model='quad',
            color=color.black,
            scale=(1.2, 0.15),
            billboard=True
        )
        self.health_bar = Entity(
            parent=self.health_bar_bg,
            model='quad',
            color=color.red,
            scale=(0.95, 0.8), # Tỉ lệ so với nền
            origin=(-0.5, 0),  # Gốc bên trái để thu nhỏ dần từ phải sang trái
            x=-0.475,
            z=-0.01 # Đẩy nhẹ lên trước để không bị z-fighting
        )

    def _setup_actor(self):
        model_path = self.cfg['model']
        self.actor = Actor(model_path)
        self.model = self.actor
        try:
            self.actor.setColorScale(4, 4, 4, 1)
            self.actor.set_shader_input('roughness', 0.8)
            self.actor.set_shader_input('metallic', 0.2)
        except Exception:
            pass

        try:
            self.actor.loadAnims({'anim': model_path})
            self._anim_names = list(self.actor.getAnimNames())
        except Exception:
            self._anim_names = []

        self._walk_anim = self._pick_anim([self.cfg['anims']['walk'], 'Walk_InPlace', 'Walk', 'Run', 'Idle'])
        self._attack_anim = self._pick_anim([self.cfg['anims']['attack'], 'Attack.001', 'Bite', 'Hit'])
        self._die_anim = self._pick_anim(['dying', 'die', 'death'], fallback=False)

        if self._walk_anim:
            self._play_anim(self._walk_anim)
        self._print_anim_info()

        self.collider = 'box'

    def _pick_anim(self, keywords, fallback=True):
        if not self._anim_names:
            return None
        for keyword in keywords:
            for name in self._anim_names:
                if keyword.lower() in name.lower():
                    return name
        if fallback:
            return self._anim_names[0]
        return None

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
    # ==============================================================
    # OBJECT POOLING: Cơ chế vòng đời spawn/despawn
    # ==============================================================

    def spawn_from_pool(self, position, player):
        """Kích hoạt lại zombie từ pool mà không cần nạp lại Model/Actor."""
        self.position = position
        self.player = player
        self.health = self.max_health
        self.is_alive = True
        self.enabled = True
        self.visible = True
        self.scale = Vec3(1, 1, 1)  # Reset lại scale sau khi bị thu nhỏ lúc chết
        self._moan_timer = 0.0
        self.can_attack = True
        self.vertical_velocity = 0.0
        if hasattr(self, 'health_bar_bg') and self.health_bar_bg:
            self.health_bar_bg.enabled = True
            health_ratio = self.health / self.max_health
            self.health_bar.scale_x = 0.95 * health_ratio
        self._current_anim = None  # Reset để cho phép play lại anim walk
        self._was_visible = True
        self._raycast_timer = 0.0
        if self._walk_anim:
            self._play_anim(self._walk_anim)

    def despawn(self):
        """Đưa zombie vào trạng thái ngủ đông - ẩn khỏi game nhưng giữ trong RAM."""
        self.is_alive = False
        self.enabled = False
        self.visible = False
        self.position = Vec3(0, -999, 0)  # Đẩy sâu xuống đất cách xa camera
        self._current_anim = None
        if hasattr(self, 'actor') and self.actor:
            self.actor.stop() # Culling Animation

    # ==============================================================
    # UPDATE LOOP: Distance Culling + Logic di chuyển
    # ==============================================================

    def update(self):
        """
        Logic vòng đời chính của Zombie, được Ursina gọi liên tục mỗi frame.
        Hàm này hoạt động như một bộ điều khiển trung tâm, gọi tuần tự các module chức năng:
        - Culling: Ẩn/hiện mô hình theo góc camera để tối ưu FPS.
        - Movement/AI: Tìm đường theo Player bằng Raycast/A* và xử lý trượt tường.
        - Gravity: Áp dụng lực hút trái đất và dính chặt xuống sàn nhà.
        - Attack: Tính toán cự ly để tung đòn đánh cận chiến.
        """
        if not self.is_alive or not self.player:
            return

        dist = distance_between(self, self.player)
        self._handle_culling(dist)

        stopping_distance = self.attack_range * 0.75 

        self._handle_movement(dist, stopping_distance)
        self._apply_gravity_and_ground()
        
        self.look_at_2d(self.player.position, axis='y')
        self.rotation_y += self.facing_offset_y

        self._moan_timer += time.dt
        if self._moan_timer >= self.moan_interval:
            self._moan_timer = 0.0
            self._play_moan()

        self._handle_attack(dist, stopping_distance)

    def _handle_culling(self, dist):
        """
        Tối ưu hóa sức mạnh phần cứng (Frustum & Distance Culling).
        - Distance Culling: Zombie ở quá xa (dist > 55m) sẽ bị ẩn hoàn toàn mô hình 3D.
        - Frustum Culling: Sử dụng Tích Vô Hướng (Dot Product) giữa hướng nhìn của camera và 
          vị trí zombie. Nếu dot_product âm (< -0.2 tức zombie nằm sau lưng) thì tạm ẩn zombie.
        Kỹ thuật này giúp Game có thể xử lý hàng trăm con zombie mà không bị sụt giảm FPS.
        """
        from ursina import camera
        
        should_cull = False
        
        if dist > 55:
            should_cull = True
        else:
            # Góc nhìn: Vector từ camera đến zombie
            cam_to_zombie = self.position - camera.world_position
            cam_to_zombie.y = 0
            if cam_to_zombie.length() > 0:
                cam_to_zombie = cam_to_zombie.normalized()
                cam_forward = camera.forward
                cam_forward.y = 0
                if cam_forward.length() > 0:
                    cam_forward = cam_forward.normalized()
                    dot_product = cam_to_zombie.dot(cam_forward)
                    
                    # Nếu dot_product < -0.2 (nằm sau lưng camera) và ở xa hơn 3.5m (tránh giấu lầm khi lại gần)
                    if dot_product < -0.2 and dist > 3.5:
                        should_cull = True

        if should_cull:
            if self.visible:
                self.visible = False
                self._was_visible = False
                if hasattr(self, 'actor') and self.actor:
                    self.actor.stop() # Dừng hẳn tính toán xương
                    self._current_anim = None # Reset cờ animation để không bị đơ T-Pose khi quay lại
        else:
            if not self.visible:
                self.visible = True
                if not self._was_visible:
                    # Kích hoạt lại animation nếu vừa từ trạng thái ẩn trở lại
                    self._was_visible = True
                    if self._walk_anim and self.can_attack:
                         self._play_anim(self._walk_anim)

    def _handle_movement(self, dist, stopping_distance):
        """Hàm chính điều phối di chuyển (Đã Refactor SRP)"""
        # Cập nhật timer chung
        self.path_recalc_timer += time.dt
        self._los_timer += time.dt
        self._physics_timer += time.dt
        
        if dist <= stopping_distance:
            self.current_path = [] # Tới nơi thì xóa đường
            return
            
        # 1. Tìm mục tiêu (AI)
        target_pos = self._update_ai_target()
        
        if target_pos is None:
            target_pos = self.position

        # Tính toán hướng tới mục tiêu
        target_dir = target_pos - self.position
        target_dir.y = 0
        if target_dir.length() > 0:
            target_dir = target_dir.normalized()

        move_amount = target_dir * self.speed * time.dt
        step_height = 0.6
        
        # 2. Áp dụng Vật lý và Trượt tường
        self._apply_physics_movement(target_dir, move_amount, step_height)

    def _update_ai_target(self):
        """
        Trí tuệ nhân tạo (AI): Quyết định điểm đến tiếp theo của Zombie.
        - Quét tia (Raycast) Line of Sight (LOS): Kiểm tra xem có tường chắn giữa zombie và người chơi không.
        - Nếu LOS trống (không có vách ngăn): Chạy đường chim bay thẳng về phía người chơi.
        - Nếu bị ngăn cách bởi tường: Truy vấn đồ thị đường đi (NavGraph) lấy lộ trình A* (các waypoint),
          sau đó zombie sẽ tự động dò dẫm đi theo từng hạt bánh mì (waypoint) một để vòng qua vật cản.
        """
        from core.utils import get_map_entity
        map_ent = get_map_entity()
        
        target_pos = None

        # Nếu chưa có đường (hoặc mất mục tiêu), chạy A* để tìm đường tới Player
        if not self.current_path:
            # KIỂM TRA THỊ GIÁC (THROTTLED LOS CHECK)
            player_dir = self.player.position - self.position
            player_dir.y = 0
            player_dist = player_dir.length()
            
            if self._los_timer > 0.2:
                self._los_timer = 0.0
                if player_dist > 0:
                    pd = player_dir.normalized()
                    hit = raycast(origin=self.position + Vec3(0, 1.0, 0), direction=pd, distance=player_dist, traverse_target=map_ent if map_ent else scene)
                    self._cached_los_hit = hit.hit

            if player_dist > 0 and not self._cached_los_hit:
                self.current_path = [] # Vứt bỏ đường bánh mì, đuổi thẳng!
                target_pos = self.player.position
            else:
                # Nếu bị khuất tầm nhìn, tìm đường theo bánh mì NavGraph (CÓ THỜI GIAN DELAY)
                if self.path_recalc_timer > 0.2:
                    self.path_recalc_timer = 0.0
                    self.current_path = NavGraph.get_instance().find_path(self.position, self.player.position)
                
                if self.current_path:
                    target_pos = self.current_path[0] # Không pop để giữ đường
                else:
                    target_pos = self.position # Đứng im nếu chưa tìm được đường

        # NẾU ĐANG CÓ ĐƯỜNG A* -> Ưu tiên đi theo các hạt bánh mì
        else:
            # KIỂM TRA THỊ GIÁC PHẢN XẢ (THROTTLED LOS OVERRIDE)
            player_dir = self.player.position - self.position
            player_dir.y = 0
            player_dist = player_dir.length()
            
            if self._los_timer > 0.5:
                self._los_timer = 0.0
                if player_dist > 0:
                    pd = player_dir.normalized()
                    hit = raycast(origin=self.position + Vec3(0, 1.0, 0), direction=pd, distance=player_dist, traverse_target=map_ent if map_ent else scene)
                    self._cached_los_hit = hit.hit
                    
                    if not self._cached_los_hit:
                        self.current_path = []
                        target_pos = self.player.position

            # NẾU VẪN CÒN ĐƯỜNG SAU KHI QUÉT LOS
            if self.current_path:
                next_wp = self.current_path[0]
                # Nếu đã đến đủ gần điểm waypoint (0.8m), xóa điểm đó đi
                if distance(Vec3(self.position.x, 0, self.position.z), Vec3(next_wp.x, 0, next_wp.z)) < 0.8:
                    self.current_path.pop(0)
                    if self.current_path:
                        target_pos = self.current_path[0]
                    else:
                        target_pos = self.player.position
                else:
                    target_pos = next_wp
                    
        return target_pos

    def _apply_physics_movement(self, target_dir, move_amount, step_height):
        """
        Hệ thống vật lý và trượt tường (Wall Sliding).
        - Bắn 2 tia Raycast (Thấp - chân và Cao - thân) về phía trước để dò vật cản.
        - Dùng kỹ thuật Throttling (chỉ quét tia mỗi 0.2s) rồi lưu kết quả (Caching) để đỡ lag.
        - Nếu bị kẹt tường (tia đụng tường): Dùng pháp tuyến của bề mặt tường (world_normal) kết hợp
          toán học vector (Cross Product/Dot Product) để bẻ cong hướng di chuyển, giúp zombie 
          có thể "trượt" dọc theo bờ tường thay vì bị kẹt cứng lại một góc.
        """
        from core.utils import get_map_entity
        map_ent = get_map_entity()
        
        # --- PHYSICS CACHING (THROTTLED RAYCASTS 5 FPS) ---
        if self._physics_timer > 0.2:
            self._physics_timer = 0.0
            
            low_origin = self.position + Vec3(0, 0.2, 0)
            high_origin = self.position + Vec3(0, 1.2, 0)
            ray_dist = self.speed * 0.2 + 0.8 # Nhìn trước khoảng cách trong 0.2s tới
            
            low_hit = raycast(origin=low_origin, direction=target_dir, distance=ray_dist, traverse_target=map_ent if map_ent else scene)
            high_hit = raycast(origin=high_origin, direction=target_dir, distance=ray_dist, traverse_target=map_ent if map_ent else scene)

            self._cached_low_blocked = low_hit.hit
            self._cached_high_blocked = high_hit.hit
            
            normal = high_hit.world_normal if self._cached_high_blocked else low_hit.world_normal
            self._cached_slide_dir = None
            
            if (self._cached_low_blocked or self._cached_high_blocked) and normal and normal.length() > 0:
                normal.y = 0
                if normal.length() > 0:
                    n = normal.normalized()
                    dot_product = target_dir.x * n.x + target_dir.z * n.z
                    s_dir = Vec3(
                        target_dir.x - dot_product * n.x,
                        0,
                        target_dir.z - dot_product * n.z
                    )
                    
                    if s_dir.length() < 0.1:
                        s_dir = n.cross(Vec3(0, 1, 0))
                    
                    if s_dir.length() > 0.01:
                        s_dir = s_dir.normalized()
                        slide_hit = raycast(origin=self.position + Vec3(0, 0.5, 0), direction=s_dir, distance=self.speed * 0.2 + 0.5, traverse_target=map_ent if map_ent else scene)
                        if not slide_hit.hit:
                            self._cached_slide_dir = s_dir

        # ÁP DỤNG DI CHUYỂN TỪ CACHE (MƯỢT 60 FPS)
        if not self._cached_low_blocked and not self._cached_high_blocked:
            self.position += move_amount
        elif self._cached_low_blocked and not self._cached_high_blocked:
            # Leo dốc / bước lên bậc
            self.y += step_height
            self.position += move_amount
        else:
            # KẸT TƯỜNG -> Dùng slide_dir đã cache
            if self._cached_slide_dir:
                self.position += self._cached_slide_dir * self.speed * time.dt

    def _handle_attack(self, dist, stopping_distance):
        """
        Bộ kiểm soát tấn công và hoạt ảnh (Animation Controller).
        - Nếu ở trong tầm đánh (attack_range) và delay xong: Thực thi hàm attack() gây sát thương.
        - Nếu ở ngoài tầm đánh: Đảm bảo hoạt ảnh chạy/đi bộ (_walk_anim) được phát mượt mà.
        """
        if dist <= self.attack_range and self.can_attack:
            self.attack()
        elif dist > stopping_distance and self.visible:
            self._play_anim(self._walk_anim)

    # ==============================================================
    # CÁC HÀM PHỤ TRỢ
    # ==============================================================

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
        """
        Mô phỏng trọng lực (Gravity) và giữ zombie bám đất.
        - Liên tục bắn một tia Raycast thẳng đứng xuống dưới gót chân để quét tìm địa hình (mặt đất/sàn).
        - Nếu chạm đất: Gắn cứng trục Y của zombie theo độ dốc của sàn (Snap to ground).
        - Nếu lơ lửng: Cộng dồn gia tốc rơi (vertical_velocity) tạo cảm giác rơi tự do vật lý.
        """
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
        """Tấn công player khi đủ gần (Sát thương tính theo % animation)."""
        if not self.can_attack or not self.player:
            return

        self.can_attack = False
        self._play_anim(self._attack_anim or "Attack")
        
        # --- CẢI TIẾN: Lấy thời gian thực của hoạt ảnh tấn công ---
        hit_delay = 0.8 # Default fallback
        try:
            if hasattr(self, 'actor') and self.actor:
                anim_len = self.actor.getDuration(self._attack_anim or "Attack")
                if anim_len is not None and anim_len > 0:
                    hit_delay = anim_len * 0.85 # Sát thương nổ ra ở cuối đòn đánh (khi tay vung tới sát người)
        except Exception:
            pass

        # Giới hạn an toàn: không được quá dài hoặc quá ngắn
        hit_delay = max(0.4, min(hit_delay, self.attack_cooldown * 0.95))
        
        invoke(self._apply_damage_delayed, delay=hit_delay)
        
        # Cooldown tổng của đòn đánh
        invoke(self._reset_attack, delay=self.attack_cooldown)

    def _apply_damage_delayed(self):
        """Gây sát thương sau khi animation đã thực hiện xong cú vung tay."""
        # Kiểm tra điều kiện: Zombie phải còn sống và player vẫn ở trong tầm đánh
        if not self.is_alive or not self.player:
            return
            
        # Tính lại khoảng cách tại ĐÚNG thời điểm ra đòn (tránh việc player đã chạy mất vẫn dính damage)
        dist = distance_between(self, self.player)
        
        # Cho phép nới rộng tầm đánh ra một chút (ví dụ + 0.5) vì player có thể đang di chuyển lùi
        if dist <= (self.attack_range + 0.5):
            self.player.take_damage(self.damage)
            print(f'[Zombie] Đã cào trúng player, gây {self.damage} damage!')
        else:
            print('[Zombie] Cào hụt vì player đã né kịp!')

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

        # Cập nhật health bar
        if hasattr(self, 'health_bar') and self.health_bar:
            health_ratio = self.health / self.max_health
            self.health_bar.scale_x = max(0.001, 0.95 * health_ratio)

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
        """Xử lý khi zombie chết: gọi despawn thay vì destroy để tái sử dụng qua pool."""
        self.is_alive = False
        print('[Zombie] Zombie died!')

        # Ẩn health bar khi chết
        if hasattr(self, 'health_bar_bg') and self.health_bar_bg:
            self.health_bar_bg.enabled = False
        
        invoke(self.death_sound.play, delay=0.18)

        if self.on_death:
            self.on_death(self)

        # Phát animation chết (nếu có), ngược lại chờ 0.5s rồi biến mất
        if getattr(self, '_die_anim', None):
            self._play_anim(self._die_anim)
            invoke(self.despawn, delay=2.0)
        else:
            # Animation chết: thu nhỏ rồi despawn (trả về pool)
            self.animate_scale(Vec3(0, 0, 0), duration=0.3)
            invoke(self.despawn, delay=0.5)

    def _play_moan(self):
        if not self.is_alive or not self.visible:
            return  # Không visible thì không phát tiếng rên (tiết kiệm audio channel)
        self.moan_sound.play()
