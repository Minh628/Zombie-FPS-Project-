# level_01.py - Set up map, vị trí spawn quái, ánh sáng cho Level 1
from ursina import *
import random


class Level01:
    """
    Level 1 - Thiết lập map, ánh sáng, vị trí spawn zombie.
    """

    def __init__(self):
        self.spawn_points = []
        self.entities = []
        self._setup_environment()
        self._setup_lighting()
        self._setup_spawn_points()

    def _setup_environment(self):
        """Tạo môi trường map Level 1."""
        # Sàn
        ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.gray,
            texture='white_cube',
            texture_scale=(50, 50),
            collider='box'
        )
        self.entities.append(ground)

        # Tường bao quanh
        walls_data = [
            (Vec3(0, 2, 50), Vec3(100, 4, 1)),    # Tường Bắc
            (Vec3(0, 2, -50), Vec3(100, 4, 1)),   # Tường Nam
            (Vec3(50, 2, 0), Vec3(1, 4, 100)),    # Tường Đông
            (Vec3(-50, 2, 0), Vec3(1, 4, 100)),   # Tường Tây
        ]
        for pos, scale in walls_data:
            wall = Entity(
                model='cube',
                position=pos,
                scale=scale,
                color=color.dark_gray,
                collider='box'
            )
            self.entities.append(wall)

        # Vật cản ngẫu nhiên (hộp, thùng)
        for i in range(15):
            obstacle = Entity(
                model='cube',
                position=(random.uniform(-40, 40), 1, random.uniform(-40, 40)),
                scale=(random.uniform(1, 3), 2, random.uniform(1, 3)),
                color=color.brown,
                collider='box'
            )
            self.entities.append(obstacle)

        # Bầu trời
        Sky()

    def _setup_lighting(self):
        """Thiết lập ánh sáng cho level."""
        # Ánh sáng chính (mặt trời)
        sun = DirectionalLight()
        sun.look_at(Vec3(1, -1, -1))

        # Ambient light
        scene.ambient_light = color.rgb(100, 100, 120)

    def _setup_spawn_points(self):
        """Định nghĩa các điểm spawn zombie."""
        self.spawn_points = [
            Vec3(30, 0, 30),
            Vec3(-30, 0, 30),
            Vec3(30, 0, -30),
            Vec3(-30, 0, -30),
            Vec3(40, 0, 0),
            Vec3(-40, 0, 0),
            Vec3(0, 0, 40),
            Vec3(0, 0, -40),
        ]

    def get_random_spawn_point(self):
        """Trả về một điểm spawn ngẫu nhiên."""
        return random.choice(self.spawn_points)

    def cleanup(self):
        """Dọn dẹp tất cả entity của level."""
        for entity in self.entities:
            destroy(entity)
        self.entities.clear()
