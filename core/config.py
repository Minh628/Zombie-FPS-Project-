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
MOUSE_SENSITIVITY = 100

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
KNIFE_DAMAGE = 10
KNIFE_ATTACK_RATE = 0.5
KNIFE_RANGE = 3.0

# --- Cài đặt vũ khí: AK47 (Phím 4) ---
AK47_NAME = 'AK47 DRAGON'
AK47_DAMAGE = 25
AK47_FIRE_RATE = 0.1
AK47_RELOAD_TIME = 2.5
AK47_MAX_AMMO = 30
AK47_TOTAL_AMMO = 90
AK47_RANGE = 120

# --- (Dự phòng tương lai) ---
# WEAPON_DAMAGE, WEAPON_FIRE_RATE... giữ lại cho backward compat
WEAPON_DAMAGE = RIFLE_DAMAGE
WEAPON_FIRE_RATE = RIFLE_FIRE_RATE
WEAPON_RELOAD_TIME = RIFLE_RELOAD_TIME
WEAPON_MAX_AMMO = RIFLE_MAX_AMMO
WEAPON_TOTAL_AMMO = RIFLE_TOTAL_AMMO

# --- Cài đặt Zombie ---
ZOMBIE_BASE_HEALTH = 100
ZOMBIE_BASE_SPEED = 2
ZOMBIE_BASE_DAMAGE = 10
ZOMBIE_FAST_SPEED = 5
ZOMBIE_FAST_HEALTH = 75
ZOMBIE_FAST_DAMAGE = 10
ZOMBIE_BOSS_SPEED = 1.5
ZOMBIE_BOSS_HEALTH = 500
ZOMBIE_BOSS_DAMAGE = 30
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
IMAGES_DIR = f'{ASSETS_DIR}/images'
MAIN_MENU_BG = f'{IMAGES_DIR}/welcome_background.jpg'

# --- Database ---
DATABASE_PATH = 'data/save_data.db'

# --- Cấu hình mở rộng cho Zombie (Gộp vào config.py) ---
ZOMBIE_CONFIG = {
    'normal': {
        'model': f'{MODELS_DIR}/zombie/zombiebase.glb',
        'health': ZOMBIE_BASE_HEALTH,
        'speed': ZOMBIE_BASE_SPEED,
        'damage': ZOMBIE_BASE_DAMAGE,
        'anims': {'walk': 'Walk_InPlace', 'attack': 'Attack.001'}
    },
    'fast': {
        'model': f'{MODELS_DIR}/zombie/zombie_fast.glb', # Đường dẫn model mới
        'health': ZOMBIE_FAST_HEALTH,
        'speed': ZOMBIE_FAST_SPEED,
        'damage': ZOMBIE_FAST_DAMAGE,
        'anims': {'walk': 'Run', 'attack': 'attack'}
    },
    'boss': {
        'model': f'{MODELS_DIR}/zombie/zombie_boss.glb',
        'health': ZOMBIE_BOSS_HEALTH,
        'speed': ZOMBIE_BOSS_SPEED,
        'damage': ZOMBIE_BOSS_DAMAGE,
        'anims': {'walk': 'Walk', 'attack': 'Attack'}
    }
}
