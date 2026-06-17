# models.py - Định nghĩa cấu trúc bảng/Object (VD: Leaderboard, PlayerSave)


class LeaderboardEntry:
    """
    Đại diện cho một bản ghi trong bảng Leaderboard (Bảng xếp hạng).
    Dữ liệu này được dùng để hiển thị top 10 người chơi có điểm số cao nhất trên màn hình Main Menu.
    """

    def __init__(self, player_name, score, wave_reached=1, zombies_killed=0, play_time=0):
        self.player_name = player_name
        self.score = score
        self.wave_reached = wave_reached
        self.zombies_killed = zombies_killed
        self.play_time = play_time

    def __repr__(self):
        return (f'LeaderboardEntry(player={self.player_name}, score={self.score}, '
                f'wave={self.wave_reached}, kills={self.zombies_killed})')


class PlayerSave:
    """
    Đại diện cho một bản ghi lưu trạng thái game của người chơi (Save Game).
    Lưu trữ đầy đủ máu, đạn và wave hiện tại để có thể tiếp tục chơi vào lần sau.
    """

    def __init__(self, player_name, health=100, current_ammo=30, total_ammo=120,
                 current_wave=1, score=0):
        self.player_name = player_name
        self.health = health
        self.current_ammo = current_ammo
        self.total_ammo = total_ammo
        self.current_wave = current_wave
        self.score = score

    def __repr__(self):
        return (f'PlayerSave(player={self.player_name}, health={self.health}, '
                f'ammo={self.current_ammo}/{self.total_ammo}, wave={self.current_wave})')
