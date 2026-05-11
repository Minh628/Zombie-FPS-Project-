# db_manager.py - Các hàm kết nối, thêm/sửa/xóa (CRUD) dữ liệu
import sqlite3
import os
from core.config import DATABASE_PATH


class DBManager:
    """
    Quản lý kết nối và thao tác CRUD với SQLite database.
    Dùng cho Leaderboard, PlayerSave,...
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
        self._ensure_data_dir()
        self.connection = None

    def _ensure_data_dir(self):
        """Tạo thư mục data/ nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self):
        """Kết nối tới database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()
        print(f'[DBManager] Connected to {self.db_path}')

    def _create_tables(self):
        """Tạo các bảng nếu chưa tồn tại."""
        cursor = self.connection.cursor()

        # Bảng Leaderboard
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                wave_reached INTEGER DEFAULT 1,
                zombies_killed INTEGER DEFAULT 0,
                play_time REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Bảng Player Save
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_save (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                health INTEGER DEFAULT 100,
                current_ammo INTEGER DEFAULT 30,
                total_ammo INTEGER DEFAULT 120,
                current_wave INTEGER DEFAULT 1,
                score INTEGER DEFAULT 0,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.connection.commit()

    def save_score(self, player_name, score, wave, zombies_killed, play_time):
        """Lưu điểm vào bảng leaderboard."""
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO leaderboard (player_name, score, wave_reached, zombies_killed, play_time) '
            'VALUES (?, ?, ?, ?, ?)',
            (player_name, score, wave, zombies_killed, play_time)
        )
        self.connection.commit()

    def get_top_scores(self, limit=10):
        """Lấy bảng xếp hạng top scores."""
        cursor = self.connection.cursor()
        cursor.execute(
            'SELECT * FROM leaderboard ORDER BY score DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

    def save_game(self, player_name, health, current_ammo, total_ammo, wave, score):
        """Lưu trạng thái game hiện tại."""
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO player_save (player_name, health, current_ammo, total_ammo, current_wave, score) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (player_name, health, current_ammo, total_ammo, wave, score)
        )
        self.connection.commit()

    def load_game(self, player_name):
        """Load save game gần nhất."""
        cursor = self.connection.cursor()
        cursor.execute(
            'SELECT * FROM player_save WHERE player_name = ? ORDER BY saved_at DESC LIMIT 1',
            (player_name,)
        )
        return cursor.fetchone()

    def close(self):
        """Đóng kết nối database."""
        if self.connection:
            self.connection.close()
            print('[DBManager] Connection closed.')
