try:
    import simplejson as json
except ImportError:
    import json

from arena import Arena, TileType, tile_type_dict
from util import Vector
from constants import ARENA_SIZE, MAP_FORMAT_VERSION


def load_map(file, size, physics_world=None):
    map_text = open(file, "r").read()
    map_json = json.loads(map_text)
    if map_json["version"] != MAP_FORMAT_VERSION:
        print("Invalid map version!")
        return

    map_tile_count = map_json["size"]
    arena = Arena(size, map_tile_count)
    tiles = arena.get_empty_tiles()
    row_index = 0
    y = 0
    while y < arena.tile_count:
        row_count = map_json["tiles"][row_index]["count"]
        for curr_row in range(row_count):
            tile_index = 0
            x = 0
            while x < arena.tile_count:
                # tile count:
                tc = map_json["tiles"][row_index]["row"][tile_index]["count"]
                for curr_tile in range(tc):
                    # tile name:
                    n = map_json["tiles"][row_index]["row"][tile_index]["tile"]
                    tiles[y+curr_row][x+curr_tile] = tile_type_dict[n]
                x += tc
                tile_index += 1
        y += row_count
        row_index += 1

    arena.tiles = tiles

    if physics_world is not None:
        r = 0
        for row in map_json["tiles"]:
            t = 0
            for tile in row["row"]:
                if tile_type_dict[tile["tile"]].has_collision:
                    width = tile["count"] * arena.tile_size
                    height = row["count"] * arena.tile_size
                    x = t * arena.tile_size + int(width / 2)
                    y = r * arena.tile_size + int(height / 2)
                    physics_world.add_rect(Vector(x, ARENA_SIZE - y), width, height)
                t += tile["count"]
            r += row["count"]

    return arena
