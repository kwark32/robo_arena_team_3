import os

import numpy as np
import pixmap_resource_manager as prm

from util import draw_img_with_rot, get_main_path
from globals import GameInfo
from constants import FIXED_DELTA_TIME

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


animation_path = "textures/"

animations_fps = {
    "animated_tiles/fire": 10,
    "animated_tiles/portal_1": 10,
    "animated_tiles/portal_2": 10,
    "vfx/tank_blue_explosion": 10,
    "vfx/tank_red_explosion": 10
}


class Animation:
    world_scene = None

    def __init__(self, name, position, rotation=0, single_vfx=True):
        self.name = name
        self.position = position.copy()
        self.rotation = rotation

        self._frames = None
        self._fps = animations_fps.get(name)
        if self._fps is None:
            self._fps = 10
        self._curr_frame = 0
        self._playing = False
        self._loop = False

        self._frame_count = 0

        self._start_physics_frame = 0

        if not GameInfo.is_headless:
            self._frames = []
            path = animation_path + name + "/"
            file_list = os.listdir(get_main_path() + path)
            file_list = sorted(file_list)
            self._frames = np.empty(len(file_list), dtype=QPixmap)
            for i, file_name in enumerate(file_list):
                self._frames[i] = prm.get_pixmap(path + file_name[:-4])
            self._frame_count = len(file_list)

        if single_vfx and Animation.world_scene is not None and not Animation.world_scene.world_sim.catchup_frame:
            Animation.world_scene.animations.append(self)
            self.play(False, Animation.world_scene.world_sim.physics_frame_count)

    def update(self, physics_frame):
        self._curr_frame = int((physics_frame - self._start_physics_frame) * FIXED_DELTA_TIME * self._fps)

        if self._curr_frame >= self._frame_count:
            if self._loop:
                self._curr_frame = self._curr_frame % self._frame_count
                self._start_physics_frame = physics_frame
            else:
                self._curr_frame = 0
                self._playing = False
                return False

        return True

    def play(self, loop, physics_frame):
        self._curr_frame = 0
        self._loop = loop
        self._playing = True

        self._start_physics_frame = physics_frame

    def draw(self, qp, physics_frame):
        if not self._playing or not self.update(physics_frame):
            return False

        frame = self._frames[self._curr_frame]
        draw_img_with_rot(qp, frame, frame.width(), frame.height(), self.position, self.rotation)
        return self._curr_frame < len(self._frames) - 1 or self._loop

    def get_frame(self):
        return self._frames[self._curr_frame]

    def get_start_time_frame(self):
        return self._start_physics_frame
