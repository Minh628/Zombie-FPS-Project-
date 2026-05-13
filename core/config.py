# config.py - Lưu hằng số (Tốc độ game, độ phân giải, âm lượng,...)

# --- Cài đặt cửa sổ ---
WINDOW_TITLE = 'Zombie FPS'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_BORDERLESS = False
WINDOW_FULLSCREEN = False

# --- Cài đặt Gameplay ---
PLAYER_MAX_HEALTH = 100
PLAYER_MOVE_SPEED = 5
PLAYER_SPRINT_SPEED = 8
PLAYER_JUMP_HEIGHT = 2
MOUSE_SENSITIVITY = 40

# --- Cài đặt vũ khí: Rifle (Phím 1) ---
RIFLE_NAME = 'RIFLE'
RIFLE_DAMAGE = 25
RIFLE_FIRE_RATE = 0.15          # Giây giữa mỗi lần bắn
RIFLE_RELOAD_TIME = 2.0         # Giây để nạp đạn
RIFLE_MAX_AMMO = 30             # Đạn tối đa trong băng
RIFLE_TOTAL_AMMO = 120          # Tổng đạn dự trữ
RIFLE_RANGE = 100               # Tầm bắn

# --- Cài đặt vũ khí: Pistol (Phím 2) ---
PISTOL_NAME = 'PISTOL'
PISTOL_DAMAGE = 15
PISTOL_FIRE_RATE = 0.35
PISTOL_RELOAD_TIME = 1.5
PISTOL_MAX_AMMO = 12
PISTOL_TOTAL_AMMO = 60
PISTOL_RANGE = 50

# --- Cài đặt vũ khí: Knife (Phím 3) ---
KNIFE_NAME = 'KNIFE'
KNIFE_DAMAGE = 50
KNIFE_ATTACK_RATE = 0.5
KNIFE_RANGE = 3.0

# --- (Dự phòng tương lai) ---
# WEAPON_DAMAGE, WEAPON_FIRE_RATE... giữ lại cho backward compat
WEAPON_DAMAGE = RIFLE_DAMAGE
WEAPON_FIRE_RATE = RIFLE_FIRE_RATE
WEAPON_RELOAD_TIME = RIFLE_RELOAD_TIME
WEAPON_MAX_AMMO = RIFLE_MAX_AMMO
WEAPON_TOTAL_AMMO = RIFLE_TOTAL_AMMO

# --- Cài đặt Zombie ---
ZOMBIE_BASE_HEALTH = 50
ZOMBIE_BASE_SPEED = 2
ZOMBIE_BASE_DAMAGE = 10
ZOMBIE_FAST_SPEED = 5
ZOMBIE_FAST_HEALTH = 30
ZOMBIE_SPAWN_INTERVAL = 3.0     # Giây giữa mỗi lần spawn

# --- Cài đặt âm thanh ---
MASTER_VOLUME = 0.8
SFX_VOLUME = 0.7
MUSIC_VOLUME = 0.5

# --- Đường dẫn tài nguyên ---
ASSETS_DIR = 'assets'
MODELS_DIR = f'{ASSETS_DIR}/models'
TEXTURES_DIR = f'{ASSETS_DIR}/textures'
SOUNDS_DIR = f'{ASSETS_DIR}/sounds'
FONTS_DIR = f'{ASSETS_DIR}/fonts'

# --- Database ---
DATABASE_PATH = 'data/save_data.db'
