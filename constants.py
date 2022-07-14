from util import s_to_ns, Vector


# Window/Arena
WINDOW_SIZE = 1000
ARENA_SIZE = 1000
MAP_FORMAT_VERSION = 1

# Time
FIXED_FPS = 60
FIXED_DELTA_TIME = 1 / FIXED_FPS
FIXED_DELTA_TIME_NS = s_to_ns(FIXED_DELTA_TIME)
MAX_FIXED_TIMESTEPS = 4
MAX_EXTRAPOLATION_STEPS = round((1 / 2) * FIXED_FPS)

# Robot
MAX_ROBOT_HEALTH = 1000
PLAYER_NAME_OFFSET = Vector(0, -40)
HEALTH_BAR_OFFSET = Vector(0, -30)

# AI
MAX_ASTART_ITER = 100

# Networking
CLIENT_DISCONNECT_TIMEOUT_NS = s_to_ns(10)
SIMULATED_PING = 400  # 400  # ms
SIMULATED_PING_NS = SIMULATED_PING * 1000000
TIME_SYNC_LERP_AMOUNT = 0.01
DEL_OVERTIME_FRAMES = 2

# Text/Font
MAX_PLAYER_NAME_LENGTH = 462
MAX_SERVER_IP_LENGTH = 462
CARET_BLINK_RATE_NS = s_to_ns(0.5)

# Debug
DEBUG_MODE = True
SIMULATE_PING = False
