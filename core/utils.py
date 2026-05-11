# utils.py - Các hàm tính toán dùng chung
import math
from ursina import Vec3


def distance_between(entity_a, entity_b):
    """Tính khoảng cách giữa 2 entity."""
    return (entity_a.position - entity_b.position).length()


def direction_to(from_entity, to_entity):
    """Tính hướng (vector đơn vị) từ entity A đến entity B."""
    diff = to_entity.position - from_entity.position
    if diff.length() == 0:
        return Vec3(0, 0, 0)
    return diff.normalized()


def clamp(value, min_val, max_val):
    """Giới hạn giá trị trong khoảng [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def lerp(start, end, t):
    """Nội suy tuyến tính (Linear Interpolation)."""
    return start + (end - start) * clamp(t, 0, 1)


def format_time(seconds):
    """Chuyển đổi giây thành định dạng MM:SS."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f'{minutes:02d}:{secs:02d}'
