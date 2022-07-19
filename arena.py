import random

import numpy as np
import effects

from globals import GameInfo
from camera import CameraState
from util import Vector, get_main_path, painter_transform_with_rot, draw_img_with_rot
from constants import MAX_POWER_UP_ITER, TILES_PER_POWER_UP

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap, QPainter


tile_texture_path = get_main_path() + "/textures/static_tiles/"
animated_tiles_texture_path = get_main_path() + "/textures/animated_tiles/"
power_up_texture_path = get_main_path() + "/textures/power_ups/"


class TileType:
    def __init__(self, name, has_collision=False, effect_class=None):
        self.name = name
        self.has_collision = has_collision
        self.effect_class = effect_class
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
        # TODO: remove
        if self.name == "fire" or self.name.startswith("portal_"):
            filename = animated_tiles_texture_path + self.name + "/" + self.name + "_0.png"

        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.name
                  + " has 0 size or is missing at " + filename + "!")


tile_type_dict = {
    "ground": TileType("ground"),
    "wall": TileType("wall", has_collision=True),
    "earth": TileType("earth", effect_class=effects.EarthTileEffect),
    "tower_1": TileType("tower_1", has_collision=True),
    "hole": TileType("hole", effect_class=effects.HoleTileEffect),
    "water": TileType("water", effect_class=effects.WaterTileEffect),
    "lava": TileType("lava", effect_class=effects.LavaTileEffect),
    "fire": TileType("fire", effect_class=effects.FireTileEffect),
    "portal_1": TileType("portal_1", effect_class=effects.Portal1TileEffect),
    "portal_2": TileType("portal_2", effect_class=effects.Portal2TileEffect),
}


class PowerUp:
    def __init__(self, arena, effect, index, position):
        self.power_up_type = type(self)
        if self.power_up_type is PowerUp:
            print("ERROR: PowerUp base class should not be instantiated!")

        self.arena = arena
        self.effect = effect
        self.index = index
        self.position = position
        self.arena.power_up_list.append(self)
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
        filename = power_up_texture_path + self.power_up_type.name + ".png"

        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.power_up_type.name
                  + " power up has 0 size or is missing at " + filename + "!")

    def apply(self, robot):
        robot.effects.append(self.effect)
        self.arena.power_ups[self.index.y][self.index.x] = None
        self.arena.power_up_list.remove(self)

    def draw(self, qp):
        draw_img_with_rot(qp, self.texture, self.texture_size.x, self.texture_size.y, self.position, 0)


class HealthPowerUp(PowerUp):
    name = "health"
    health_gain = 250

    def __init__(self, arena, index, position):
        effect = effects.HealthEffect(instant_change=HealthPowerUp.health_gain)
        super().__init__(arena, effect, index, position)


class Arena:
    def __init__(self, tile_count):
        self.tile_count = tile_count.copy()
        self.tile_count.round()
        self.size = Vector(self.tile_count.x, self.tile_count.y)
        self.size.mult(GameInfo.arena_tile_size)
        self.tiles = self.get_empty_tiles()
        self.power_ups = self.get_empty_power_ups()
        self.power_up_list = []

        self._portal_tiles = None

        self.background_pixmap = None

    @property
    def portal_1_tiles(self):
        if self._portal_tiles is None:
            self.get_portal_tiles()
        return self._portal_tiles[0]

    @property
    def portal_2_tiles(self):
        if self._portal_tiles is None:
            self.get_portal_tiles()
        return self._portal_tiles[1]

    def get_empty_tiles(self):
        # get array of empty tiles with correct dimensions
        return np.empty((self.tile_count.y, self.tile_count.x), dtype=TileType)

    def get_empty_power_ups(self):
        # get array of power_ups with correct dimensions
        return np.empty((self.tile_count.y, self.tile_count.x), dtype=PowerUp)

    # get different portal tiles for portal tile effects
    def get_portal_tiles(self):
        self._portal_tiles = [[], []]
        for y in range(self.tile_count.y):
            for x in range(self.tile_count.x):
                tile_type = self.tiles[y][x]
                if tile_type.name == "portal_1":
                    self._portal_tiles[0].append(Vector(x, y))
                if tile_type.name == "portal_2":
                    self._portal_tiles[1].append(Vector(x, y))
        return self._portal_tiles

    # place power ups in the arena
    def place_power_ups(self, delta_time):
        if len(self.power_up_list) * TILES_PER_POWER_UP >= self.tile_count.x * self.tile_count.y:
            return

        for i in range(MAX_POWER_UP_ITER):
            y = random.randrange(self.tile_count.y)
            x = random.randrange(self.tile_count.x)
            tile_type = self.tiles[y][x]
            power_up = self.power_ups[y][x]
            if tile_type.name == "ground" and power_up is None:
                # place power_up on current tile
                position = Vector(x, y)
                position.mult(GameInfo.arena_tile_size)
                position.add(Vector(GameInfo.arena_tile_size / 2, GameInfo.arena_tile_size / 2))
                self.power_ups[y][x] = HealthPowerUp(self, Vector(x, y), position)
                break

    def draw(self, qp):
        if self.background_pixmap is None:
            self.background_pixmap = QPixmap(self.size.x, self.size.y)
            painter = QPainter(self.background_pixmap)
            for y in range(self.tile_count.y):
                for x in range(self.tile_count.x):
                    x_pos = x * GameInfo.arena_tile_size
                    y_pos = y * GameInfo.arena_tile_size

                    curr_tile_type = self.tiles[y][x]

                    # calculate correct part of the texture
                    tiles_per_texture = curr_tile_type.texture_size.copy()
                    tiles_per_texture.div(GameInfo.arena_tile_size)
                    tile_in_img_offset = Vector(x % round(tiles_per_texture.x), y % round(tiles_per_texture.y))

                    # draw tile image
                    painter.drawPixmap(x_pos, y_pos, curr_tile_type.texture,
                                       tile_in_img_offset.x * GameInfo.arena_tile_size,
                                       tile_in_img_offset.y * GameInfo.arena_tile_size,
                                       GameInfo.arena_tile_size, GameInfo.arena_tile_size)

            painter.end()

        painter_transform_with_rot(qp, Vector(self.background_pixmap.width() / 2,
                                              self.background_pixmap.height() / 2), 0)
        paint_start = Vector(-self.size.x / 2, -self.size.y / 2)
        cam_pos = Vector(0, 0)
        if CameraState.position is not None:
            cam_pos = CameraState.position.copy()
        paint_cutoff = Vector(max(-GameInfo.window_reference_size.x / 2 + cam_pos.x, 0),
                              max(-GameInfo.window_reference_size.y / 2 + cam_pos.y, 0))
        paint_start.add(paint_cutoff)

        end_cutoff = Vector(min(-GameInfo.window_reference_size.x / 2 - cam_pos.x + self.size.x, 0),
                            min(-GameInfo.window_reference_size.y / 2 - cam_pos.y + self.size.y, 0))
        size = GameInfo.window_reference_size.copy()
        size.add(end_cutoff)

        if size.x > 0 and size.y > 0:
            qp.drawPixmap(round(paint_start.x), round(paint_start.y), round(size.x), round(size.y),
                          self.background_pixmap, round(paint_cutoff.x), round(paint_cutoff.y),
                          round(size.x), round(size.y))
        qp.restore()

        for power_up in self.power_up_list:
            power_up.draw(qp)
