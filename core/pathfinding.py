# core/pathfinding.py
from ursina import Vec3, raycast, distance
import heapq

class NavGraph:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = NavGraph()
        return cls._instance

    def __init__(self):
        self.nodes = [] # List of Vec3
        self.edges = {} # dict mapping node index to list of (neighbor_index, cost)
        self.last_player_pos = None
        self.node_spacing = 1.0
        self.max_connection_dist = 3.0

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.last_player_pos = None

    def update_player_pos(self, pos):
        # Rải bánh mì mỗi 3 mét
        if not self.last_player_pos or distance(self.last_player_pos, pos) > self.node_spacing:
            new_pos = Vec3(pos.x, 0, pos.z)
            self._add_node(new_pos)
            self.last_player_pos = new_pos

    def _add_node(self, pos):
        new_idx = len(self.nodes)
        self.nodes.append(pos)
        self.edges[new_idx] = []
        
        # Nối node mới với các node cũ (nếu khoảng cách < max_connection_dist và không bị che)
        for i, old_pos in enumerate(self.nodes[:-1]):
            dist = distance(pos, old_pos)
            if dist < self.max_connection_dist:
                # Raycast kiểm tra line of sight ở tầm ngang ngực (cách đất 1.0m)
                dir_vec = (old_pos - pos).normalized()
                hit = raycast(origin=pos + Vec3(0, 1.0, 0), direction=dir_vec, distance=dist, ignore=[])
                if not hit.hit or hasattr(hit.entity, 'is_alive'): # Nếu không đụng tường (tường không có is_alive)
                    self.edges[new_idx].append((i, dist))
                    self.edges[i].append((new_idx, dist))

    def get_nearest_visible_node(self, pos):
        if not self.nodes: return -1
        
        # Lấy danh sách sắp xếp theo khoảng cách
        sorted_nodes = []
        for i, node in enumerate(self.nodes):
            sorted_nodes.append((distance(pos, node), i))
        sorted_nodes.sort()
        
        # Bắn tia kiểm tra điểm nào KHÔNG bị che bởi tường
        for dist_val, i in sorted_nodes:
            if dist_val < 0.1: return i # Quá gần thì lấy luôn
            dir_vec = (self.nodes[i] - pos).normalized()
            hit = raycast(origin=pos + Vec3(0, 1.0, 0), direction=dir_vec, distance=dist_val, ignore=[])
            if not hit.hit or hasattr(hit.entity, 'is_alive'):
                return i
                
        # Nếu mọi điểm đều bị che, đành bốc đại điểm gần nhất
        return sorted_nodes[0][1] if sorted_nodes else -1

    def find_path(self, start_pos, end_pos):
        start_idx = self.get_nearest_visible_node(start_pos)
        end_idx = self.get_nearest_visible_node(end_pos)
        
        if start_idx == -1 or end_idx == -1:
            return []
            
        # A* algorithm
        pq = []
        heapq.heappush(pq, (0, start_idx))
        came_from = {}
        cost_so_far = {}
        
        came_from[start_idx] = None
        cost_so_far[start_idx] = 0
        
        while pq:
            current_cost, current_node = heapq.heappop(pq)
            
            if current_node == end_idx:
                break
                
            for next_node, weight in self.edges.get(current_node, []):
                new_cost = cost_so_far[current_node] + weight
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + distance(self.nodes[next_node], self.nodes[end_idx])
                    heapq.heappush(pq, (priority, next_node))
                    came_from[next_node] = current_node
                    
        # Reconstruct path
        path = []
        curr = end_idx
        if curr not in came_from:
            return [] # Không tìm thấy đường
            
        while curr is not None:
            path.append(self.nodes[curr])
            curr = came_from[curr]
            
        path.reverse()
        return path
