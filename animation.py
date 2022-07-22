import os
import numpy as np

from util import get_main_path, draw_img_with_rot
from globals import GameInfo
from constants import FIXED_DELTA_TIME

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


animated_tiles_path = get_main_path() + "/textures/animated_tiles/"

animations_fps = {
    "fire": 10,
    "portal_1": 10,
    "portal_2": 10
}


class Animation:
    def __init__(self, name, position):
        self.name = name
        self.position = position.copy()

        self._frames = None
        self._fps = animations_fps[name]
        self._curr_frame = 0
        self._playing = False
        self._loop = False

        self._frame_count = 0

        self._start_physics_frame = 0

        if not GameInfo.is_headless:
            self._frames = []
            path = animated_tiles_path + name + "/"
            file_list = os.listdir(path)
            file_list = sorted(file_list)
            self._frames = np.empty(len(file_list), dtype=QPixmap)
            for i, name in enumerate(file_list):
                self._frames[i] = QPixmap(path + name)
            self._frame_count = len(file_list)

    def update(self, physics_frame):
        self._curr_frame = int((physics_frame - self._start_physics_frame) * FIXED_DELTA_TIME * self._fps)

        if self._curr_frame >= self._frame_count:
            if self._loop:
                self._curr_frame = self._curr_frame % self._frame_count
                self._start_physics_frame = physics_frame
            else:
                self._playing = False

    def play(self, loop, physics_frame):
        self._curr_frame = 0
        self._loop = loop
        self._playing = True

        self._start_physics_frame = physics_frame

    def draw(self, qp, physics_frame):
        self.update(physics_frame)
        frame = self._frames[self._curr_frame]
        draw_img_with_rot(qp, frame, frame.width(), frame.height(), self.position, 0)

    def get_frame(self):
        return self._frames[self._curr_frame]
