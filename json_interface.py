import json

from arena import Arena, Tile, tile_type_dict


def load_map(file, size):
    map_text = open(file, "r").read()
    map_json = json.loads(map_text)
    if map_json["version"] != 1:
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
                    tile = Tile(tile_type=tile_type_dict[n])
                    tiles[y+curr_row][x+curr_tile] = tile
                x += tc
                tile_index += 1
        y += row_count
        row_index += 1

    arena.tiles = tiles
    return arena
