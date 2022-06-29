from util import s_to_ns, Vector


# Window/Arena
WINDOW_SIZE = 1000
ARENA_SIZE = 1000
MAP_FORMAT_VERSION = 1

# Time
FIXED_FPS = 60
FIXED_DELTA_TIME = 1 / FIXED_FPS
FIXED_DELTA_TIME_NS = s_to_ns(FIXED_DELTA_TIME)
MAX_FIXED_TIMESTEPS = 3
MAX_EXTRAPOLATION_STEPS = round((1 / 4) * FIXED_FPS)

# Robot
MAX_ROBOT_HEALTH = 1000
PLAYER_NAME_OFFSET = Vector(0, -40)
HEALTH_BAR_OFFSET = Vector(0, -30)

# Networking
CLIENT_DISCONNECT_TIMEOUT_NS = s_to_ns(10)
SIMULATED_PING = 400  # ms
SIMULATED_PING_STEPS = (SIMULATED_PING / 2000) / FIXED_DELTA_TIME

# Text/Font
MAX_PLAYER_NAME_LENGTH = 462
MAX_SERVER_IP_LENGTH = 462
CARET_BLINK_RATE_NS = s_to_ns(0.5)

# Debug
DEBUG_MODE = False
SIMULATE_PING = True
