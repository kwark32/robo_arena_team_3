try:
    import simplejson as json
except ImportError:
    import json

from PIL import Image
from arena import Arena, tile_type_dict
from util import Vector, get_main_path
from constants import MAP_FORMAT_VERSION
from globals import GameInfo
from animation import Animation


json_map_path = get_main_path() + "arenas/json/"
png_map_path = get_main_path() + "arenas/png/"


def add_physics(arena, physics_world):
    colliders = []
    for y in range(arena.tile_count.y):
        row = []
        for x in range(arena.tile_count.x):
            row.append(arena.tiles[y][x].has_collision)
        colliders.append(row)

    for y, row in enumerate(colliders):
        for x, col in enumerate(row):
            if col:
                row[x] = False
                x_count = 1
                while x + x_count < len(row) and row[x + x_count]:
                    row[x + x_count] = False
                    x_count += 1

                y_count = 1
                while y + y_count < len(colliders):
                    test_row = colliders[y + y_count]
                    is_valid_row = True
                    for tile in range(x_count):
                        if not test_row[x + tile]:
                            is_valid_row = False
                            break
                    if is_valid_row:
                        for tile in range(x_count):
                            test_row[x + tile] = False
                        y_count += 1
                    else:
                        break

                tile_type = arena.tiles[y][x]
                width = GameInfo.arena_tile_size * x_count
                height = GameInfo.arena_tile_size * y_count
                x_pos = x * GameInfo.arena_tile_size + int(width / 2)
                y_pos = y * GameInfo.arena_tile_size + int(height / 2)
                physics_world.add_rect(Vector(x_pos, y_pos), width, height, user_data=tile_type)


def load_map(file, physics_world=None):
    if file.endswith("json"):
        arena = load_map_json(json_map_path + file)
    elif file.endswith("png"):
        arena = load_map_png(png_map_path + file)
    else:
        return None

    if not GameInfo.is_headless:
        tiles = arena.tiles
        for y in range(arena.tile_count.y):
            for x in range(arena.tile_count.x):
                tile = tiles[y][x]
                if tile.has_animation:
                    pos = Vector(x, y)
                    pos.mult(GameInfo.arena_tile_size)
                    pos.add_scalar(GameInfo.arena_tile_size / 2)
                    pos.round()
                    anim = Animation("animated_tiles/" + tile.name, pos, single_vfx=False)
                    anim.play(True, 0)
                    arena.tile_animations.append(anim)
        arena.calc_tile_anim_groups()

    if physics_world is not None:
        add_physics(arena, physics_world)

    return arena


def load_map_json(file):
    with open(file, "r") as f:
        map_text = f.read()
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


def load_map_png(file):
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

    arena.tiles = tiles

    return arena
