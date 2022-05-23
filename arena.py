import numpy as np

from PyQt5.QtGui import QImage
from util import get_main_path


tile_type_dict = {
    "ground": None,
    "wall": None,
    "water": None,
    "fire": None,
    "earth": None,
    "air": None,
    "portal_blue": None,
    "portal_red": None
}


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


def init_tile_dict():
    for key in tile_type_dict:
        texture_size = tile_texture_sizes[key]
        tile_type_dict[key] = TileType(image=QImage(get_main_path()
                                                    + "/textures/"
                                                    + str(texture_size) + "x"
                                                    + str(texture_size) + "/"
                                                    + key + ".png"),
                                       texture_size=texture_size)


class TileType:
    def __init__(self, image=None, texture_size=0):
        self.image = image
        self.texture_size = texture_size


class Tile:
    def __init__(self, tile_type=TileType()):
        self.tile_type = tile_type


class Arena:
    def __init__(self, tile_size=40, tile_count=25):
        init_tile_dict()

        self.tile_size = tile_size
        self.tile_count = tile_count
        self.size = self.tile_size * self.tile_count
        self.tiles = self.get_empty_tiles()

    def get_empty_tiles(self):
        # get array of empty tiles with correct dimensions
        return np.empty((self.tile_count, self.tile_count), dtype=Tile)

    def draw(self, qp):
        for y in range(self.tile_count):
            for x in range(self.tile_count):
                x_pos = x * self.tile_size
                y_pos = y * self.tile_size

                curr_tile_type = self.tiles[y][x].tile_type

                # calculate correct part of the texture
                tiles_per_texture = curr_tile_type.texture_size
                tiles_per_texture /= self.tile_size
                tile_in_img_offset_x = x % tiles_per_texture
                tile_in_img_offset_y = y % tiles_per_texture

                # draw tile image
                qp.drawImage(x_pos, y_pos, curr_tile_type.image,
                             tile_in_img_offset_x * self.tile_size,
                             tile_in_img_offset_y * self.tile_size,
                             self.tile_size, self.tile_size)
