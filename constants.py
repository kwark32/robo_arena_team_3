from util import s_to_ns
from enum import IntEnum


class Scene(IntEnum):
    MAIN_MENU = 0
    SP_WORLD = 1
    ONLINE_WORLD = 2


class GameInfo:
    is_headless = False


WINDOW_SIZE = 1000
ARENA_SIZE = 1000
MAP_FORMAT_VERSION = 1

FIXED_DELTA_TIME = 1 / 60
FIXED_DELTA_TIME_NS = s_to_ns(FIXED_DELTA_TIME)
MAX_FIXED_TIMESTEPS = 3

DEBUG_MODE = False
