try:
    import simplejson as json
except ImportError:
    import json

from enum import IntEnum
from codecs import encode, decode


class Scene(IntEnum):
    MAIN_MENU = 0
    SP_WORLD = 1
    ONLINE_WORLD = 2
    SERVER_WORLD = 3


class Menus:
    menus = {}


class GameInfo:
    is_headless = False

    main_path = ""

    window_reference_size = None
    window_size = None
    arena_tile_size = 40

    # empty_test_map.json
    # test_map.json
    # arena_1.png
    # arena_1_big-100.png
    # LuftigeKwarkschafeMitUIDisigner.png
    # semi_divided_arena.png
    # arena_for_better_pathfinding.png
    active_arena = "arena_for_better_pathfinding.png"

    current_frame_seed = 0

    placeholder_name = "Player"
    local_player_name = placeholder_name

    local_player_id = 0
    next_player_id = local_player_id + 1

    default_ip = "127.0.0.1"  # "202.61.239.116"
    server_ip = default_ip
    port = 54345
    buffer_size = 4096

    score_per_kill = 600  # = 10s survival
    local_player_score = 0
    local_player_score_is_highscore = False


class Settings:
    instance = None
    protocol_version = "1.4"

    def __init__(self):
        self.master_volume = 0.1
        self.sfx_volume = 1
        self.music_volume = 1
        self.fullscreen = True
        self.player_name = ""
        self.ip_address = ""

        self.highscore = 0

        self.filename = GameInfo.main_path + "/settings.json"

        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                settings_text = f.read()
        except FileNotFoundError:
            print("INFO: No settings file existing")
            self.save()
            return

        settings = json.loads(settings_text)
        if settings.get("version") != Settings.protocol_version or settings.get("version") is None:
            print("WARN: Deleting settings with older protocol version!")
            self.save()
            return

        hs_key = scramble_int(6942069)
        hs = unscramble_int(settings[hs_key])

        self.master_volume = settings["master_volume"]
        self.sfx_volume = settings["sfx_volume"]
        self.music_volume = settings["music_volume"]
        self.player_name = settings["player_name"]
        self.ip_address = settings["ip_address"]
        self.fullscreen = settings["fullscreen"]
        self.highscore = hs

    def save(self):
        hs = scramble_int(self.highscore)
        hs_key = scramble_int(6942069)

        settings = {
            "version": Settings.protocol_version,
            "master_volume": self.master_volume,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "player_name": self.player_name,
            "ip_address": self.ip_address,
            "fullscreen": self.fullscreen,
            hs_key: hs
        }

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)


class Fonts:
    fps_font = None
    fps_color = None

    text_field_font = None
    text_field_color = None
    text_field_default_color = None

    name_tag_font = None
    name_tag_color = None

    ui_text_font = None

    score_color = None
    highscore_color = None

    score_board_font = None
    score_board_color = None


def scramble_int(num):
    s = str(num)
    b = [(int(c) * 11) + 169 for c in s]
    s = ""
    for i in b:
        s += chr(i)
    s = encode(s, "rot13")
    b = s.encode("raw_unicode_escape")
    s = ""
    for i in b:
        s += chr(i)
    return s


def unscramble_int(string):
    b = bytes([ord(s) for s in string])
    s = b.decode("raw_unicode_escape")
    s = decode(s, "rot13")
    b = [round((ord(c) - 169) / 11) for c in s]
    s = ""
    for i in b:
        s += str(i)
    return int(s)
