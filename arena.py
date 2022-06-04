import numpy as np

from PyQt5.QtGui import QPixmap
from util import Vector, get_main_path


tile_texture_path = get_main_path() + "/textures/tiles/"


class TileType:
    def __init__(self, name, has_collision):
        self.name = name
        self.has_collision = has_collision
        self._texture = None
        self._texture_size = None

    @property
    def texture(self):
        if self._texture is None:
            self.load_image()
        return self._texture

    @property
    def texture_size(self):
        if self._texture_size is None:
            self.load_image()
        return self._texture_size

    def load_image(self):
        filename = tile_texture_path + self.name + ".png"
        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.name
                  + " has 0 size or is missing at " + filename + "!")


tile_type_dict = {
    "ground": TileType("ground", False),
    "wall": TileType("wall", True),
    "earth": TileType("earth", False),
    "tower_1": TileType("tower_1", True),
    "hole": TileType("hole", False),
    "water": TileType("water", False),
    "lava": TileType("lava", False),
    "fire": TileType("fire", False),
    "portal_1": TileType("portal_1", False),
    "portal_2": TileType("portal_2", False),
}


class Tile:
    def __init__(self, tile_type=None):
        self.tile_type = tile_type


class Arena:
    def __init__(self, size, tile_count):
        self.size = int(size)
        self.tile_count = int(tile_count)
        self.tile_size = int(self.size / self.tile_count)
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
                tiles_per_texture = curr_tile_type.texture_size.copy()
                tiles_per_texture.div(self.tile_size)
                tile_in_img_offset = Vector(x % round(tiles_per_texture.x), y % round(tiles_per_texture.y))

                # draw tile image
                qp.drawPixmap(x_pos, y_pos, curr_tile_type.texture,
                              tile_in_img_offset.x * self.tile_size, tile_in_img_offset.y * self.tile_size,
                              curr_tile_type.texture_size.x, curr_tile_type.texture_size.y)
