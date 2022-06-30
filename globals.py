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
