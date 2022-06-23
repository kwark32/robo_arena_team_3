from util import s_to_ns
from enum import IntEnum


class Scene(IntEnum):
    MAIN_MENU = 0
    SP_WORLD = 1
    ONLINE_WORLD = 2
    SERVER_WORLD = 3


class Menus(IntEnum):
    MAIN_MENU = 0
    ONLINE_OPTIONS = 1
    SETTINGS = 2


class GameInfo:
    is_headless = False

    placeholder_name = "Player"
    local_player_name = placeholder_name

    default_ip = "202.61.239.116"  # "127.0.0.1"
    server_ip = default_ip
    port = 54345
    buffer_size = 4096


class Fonts:
    fps_font = None
    text_field_font = None


WINDOW_SIZE = 1000
ARENA_SIZE = 1000
MAP_FORMAT_VERSION = 1

FIXED_FPS = 60
FIXED_DELTA_TIME = 1 / FIXED_FPS
FIXED_DELTA_TIME_NS = s_to_ns(FIXED_DELTA_TIME)
MAX_FIXED_TIMESTEPS = 3
MAX_EXTRAPOLATION_STEPS = round((1 / 4) * FIXED_FPS)

ROBOT_HEALTH = 1000

CLIENT_DISCONNECT_TIMEOUT_NS = s_to_ns(10)

MAX_PLAYER_NAME_LENGTH = 462
MAX_SERVER_IP_LENGTH = 462
CARET_BLINK_RATE_NS = s_to_ns(0.5)

DEBUG_MODE = False
