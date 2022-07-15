try:
    import simplejson as json
except ImportError:
    import json

from PIL import Image
from arena import Arena, tile_type_dict
from util import Vector, get_main_path
from constants import MAP_FORMAT_VERSION
from globals import GameInfo


json_map_path = get_main_path() + "/arenas/json/"
png_map_path = get_main_path() + "/arenas/png/"


def load_map(file, physics_world=None):
    if file.endswith("json"):
        return load_map_json(json_map_path + file, physics_world=physics_world)
    elif file.endswith("png"):
        return load_map_png(png_map_path + file, physics_world=physics_world)
    else:
        return None


def load_map_json(file, physics_world=None):
    map_text = open(file, "r").read()
    map_json = json.loads(map_text)
    if map_json["version"] != MAP_FORMAT_VERSION:
        print("Invalid map version!")
        return

    map_tile_count = map_json["size"]
    arena = Arena(Vector(map_tile_count, map_tile_count))
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
                tile_type = tile_type_dict[tile["tile"]]
                if tile_type.has_collision:
                    width = tile["count"] * GameInfo.arena_tile_size
                    height = row["count"] * GameInfo.arena_tile_size
                    x = t * GameInfo.arena_tile_size + int(width / 2)
                    y = r * GameInfo.arena_tile_size + int(height / 2)
                    physics_world.add_rect(Vector(x, y), width, height, user_data=tile_type)
                t += tile["count"]
            r += row["count"]

    return arena


tile_type_colors = {
    (150, 150, 150): "ground",
    (0, 0, 0): "wall",
    (150, 100, 0): "earth",
    (0, 255, 0): "tower_1",
    (255, 255, 255): "hole",
    (0, 0, 255): "water",
    (255, 0, 0): "lava",
    (255, 100, 0): "fire",
    (255, 0, 255): "portal_1",
    (0, 255, 255): "portal_2"
}


def load_map_png(file, physics_world=None):
    im = Image.open(file)
    pix = im.load()
    arena = Arena(Vector(im.size[0], im.size[1]))
    tiles = arena.get_empty_tiles()

    for y in range(im.size[1]):
        for x in range(im.size[0]):
            color = pix[x, y]
            if len(color) > 3:
                color = color[:3]
            tile_type = tile_type_colors.get(color)
            if tile_type is None:
                continue
            tiles[y][x] = tile_type_dict[tile_type]
            if physics_world is not None:
                if tiles[y][x].has_collision:
                    width = GameInfo.arena_tile_size
                    height = GameInfo.arena_tile_size
                    x_pos = x * GameInfo.arena_tile_size + int(width / 2)
                    y_pos = y * GameInfo.arena_tile_size + int(height / 2)
                    physics_world.add_rect(Vector(x_pos, y_pos), width, height, user_data=tile_type)

    arena.tiles = tiles

    return arena
