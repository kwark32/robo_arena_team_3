import numpy as np

from PyQt5.QtGui import QImage
from util import get_main_path


class TileType:
    def __init__(self, image=None, texture_size=0):
        self.image = image
        self.texture_size = texture_size


tile_texture_sizes = {
    "ground": 40,
    "wall": 40,
    "water": 40,
    "fire": 40,
    "earth": 40,
    "air": 40,
    "portal_blue": 40,
    "portal_red": 40
}


class TileTypes:
    tile_dict = {
        "ground": None,
        "wall": None,
        "water": None,
        "fire": None,
        "earth": None,
        "air": None,
        "portal_blue": None,
        "portal_red": None
    }


def init_tile_dict():
    for key in TileTypes.tile_dict:
        texture_size = tile_texture_sizes[key]
        TileTypes.tile_dict[key] = TileType(image=QImage(get_main_path()
                                                         + "/textures/"
                                                         + str(texture_size)
                                                         + "x"
                                                         + str(texture_size)
                                                         + "/" + key + ".png"),
                                            texture_size=texture_size)


class Tile:
    def __init__(self, tile_type=TileType()):
        self.tile_type = tile_type


class Arena:
    def __init__(self, tile_size=40, tile_count=25):
        self.tile_size = tile_size
        self.tile_count = tile_count
        self.size = self.tile_size * self.tile_count
        self.tiles = self.get_empty_tiles()

    def get_empty_tiles(self):
        return np.empty((self.tile_count, self.tile_count), dtype=Tile)

    def draw(self, qp):
        for y in range(self.tile_count):
            for x in range(self.tile_count):
                tiles_per_texture = self.tiles[y][x].tile_type.texture_size
                tiles_per_texture /= self.tile_size
                tile_in_img_offset_x = x % tiles_per_texture
                tile_in_img_offset_y = y % tiles_per_texture

                ground_tile_type = TileTypes.tile_dict["ground"]
                tiles_per_texture_ground = ground_tile_type.texture_size
                tiles_per_texture_ground /= self.tile_size
                tile_in_img_offset_x_ground = x % tiles_per_texture_ground
                tile_in_img_offset_y_ground = y % tiles_per_texture_ground

                x_pos = x * self.tile_size
                y_pos = y * self.tile_size

                # ground behind the tiles, to fill alpha in some tile PNGs
                qp.drawImage(x_pos, y_pos, ground_tile_type.image,
                             tile_in_img_offset_x_ground * self.tile_size,
                             tile_in_img_offset_y_ground * self.tile_size,
                             self.tile_size, self.tile_size)

                # draw tile image
                qp.drawImage(x_pos, y_pos, self.tiles[y][x].tile_type.image,
                             tile_in_img_offset_x * self.tile_size,
                             tile_in_img_offset_y * self.tile_size,
                             self.tile_size, self.tile_size)
