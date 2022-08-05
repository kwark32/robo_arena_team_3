from util import s_to_ns, Vector
from globals import GameInfo

# Time
FIXED_FPS = 60
FIXED_DELTA_TIME = 1 / FIXED_FPS
FIXED_DELTA_TIME_NS = s_to_ns(FIXED_DELTA_TIME)
MAX_FIXED_TIMESTEPS = 3
MAX_EXTRAPOLATION_STEPS = round((1 / 2) * FIXED_FPS)

# Arena
MAP_FORMAT_VERSION = 1
MAX_POWER_UP_ITER = 10
TILES_PER_POWER_UP = 100
POWER_UPS_PER_S = round(FIXED_FPS / 5)
TILE_ANIM_GROUP_SIZE = 10

# Robot
MAX_ROBOT_HEALTH = 1000
PLAYER_NAME_OFFSET = Vector(0, -40)
HEALTH_BAR_OFFSET = Vector(0, -30)
ROBOT_COLLISION_SOUND_SPEED_FACTOR = 0.5
MIN_SOUND_DELAY_FRAMES = 15
RESPAWN_DELAY = round(3 / FIXED_DELTA_TIME)  # 3s in fixed frames

# AI
MAX_ASTART_ITER = 320

# Networking
CLIENT_DISCONNECT_TIMEOUT_NS = s_to_ns(5)
SIMULATED_PING = 0  # 800  # ms
SIMULATED_PING_NS = SIMULATED_PING * 1000000
TIME_SYNC_LERP_AMOUNT = 0.01

# Text/Font
MAX_PLAYER_NAME_LENGTH = 728
MAX_SERVER_IP_LENGTH = 728
CARET_BLINK_RATE_NS = s_to_ns(0.5)

# Audio
HALF_FALLOFF_DIST = 5 * GameInfo.arena_tile_size
MAX_AUDIO_DIST = 1000
SFX_AUDIO_SOURCES = 8

# Debug
DEBUG_MODE = False