import numpy as np
from PyQt5.QtGui import QColor


class TileType:
    def __init__(self, colour=QColor(0, 0, 0)):
        self.colour = colour


class TileTypes:
    GROUND_TILE = TileType(QColor(100, 100, 100))
    WALL_TILE = TileType(QColor(70, 70, 70))
    WATER_TILE = TileType(QColor(86, 145, 204))
    FIRE_TILE = TileType(QColor(255, 0, 77))
    EARTH_TILE = TileType(QColor(97, 27, 27))
    AIR_TILE = TileType(QColor(255, 251, 230))
    PORTAL_TILE = TileType(QColor(97, 92, 191))
    tile_dict = {
        "ground": GROUND_TILE,
        "wall": WALL_TILE,
        "water": WATER_TILE,
        "fire": FIRE_TILE,
        "earth": EARTH_TILE,
        "air": AIR_TILE,
        "portal": PORTAL_TILE
    }


class Tile:
    def __init__(self, tile_type=TileTypes.GROUND_TILE):
        self.tile_type = tile_type


class Arena:
    def __init__(self, tile_size=10, tile_count=100):
        self.tile_size = tile_size
        self.tile_count = tile_count
        self.size = self.tile_size * self.tile_count
        self.tiles = self.get_empty_tiles()

    def get_empty_tiles(self):
        return np.empty((self.tile_count, self.tile_count), dtype=Tile)

    def draw(self, qp):
        for i in range(self.tile_count):
            for j in range(self.tile_count):
                qp.fillRect(i * self.tile_size, j * self.tile_size,
                            self.tile_size, self.tile_size,
                            self.tiles[i][j].tile_type.colour)
