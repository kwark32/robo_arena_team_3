import json

from arena import *


def load_map(file):
    map_text = open(file, "r").read()
    map_json = json.loads(map_text)
    if map_json["version"] != 1
        print("Invalid map version!")
        return

    arena = Arena(tile_count=round(map_json["size"]))
    tiles = arena.get_empty_tiles()
    for y in range(arena.size):
        for x in range(arena.size):
            tile_count = map_json["tiles"][y]["row"][x]["count"]
            for curr_tile in range(tile_count):
                tile = Tile(tile_type=)
            if tile_count > 1:

    print(map_json)
    print(map_json["version"])
    print(map_json["size"])
    print(map_json["tiles"][0])
