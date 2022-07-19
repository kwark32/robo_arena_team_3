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

    window_reference_size = None
    window_size = None
    arena_tile_size = 40

    # empty_test_map.json
    # test_map.json
    # arena_1.png
    # arena_1_big-100.png
    active_arena = "arena_1_big-100.png"

    current_frame_seed = 0

    placeholder_name = "Player"
    local_player_name = placeholder_name

    local_player_id = 0
    next_player_id = local_player_id + 1

    default_ip = "127.0.0.1"  # "202.61.239.116"
    server_ip = default_ip
    port = 54345
    buffer_size = 4096


class Settings:
    instance = None

    def __init__(self):
        Settings.instance = self
        self.master_volume = 0.25

    def load(self):
        pass

    def save(self):
        pass


class Fonts:
    fps_font = None
    fps_color = None

    text_field_font = None
    text_field_color = None
    text_field_default_color = None

    name_tag_font = None
    name_tag_color = None
