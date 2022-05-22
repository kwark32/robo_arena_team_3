import sys
import time

from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint
from robot import Robot
from util import Vector, get_main_path, ns_to_s
from json_interface import load_map
from arena import init_tile_dict


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        init_tile_dict()

        self.running = True

        self.arena = None
        self.robots = []
        self.player_input = None

        self.init_arena()
        self.init_robots()

        self.initUI()
        self.arena_pixmap = QPixmap(self.arena.size, self.arena.size)

        self._last_frame_time_ns = time.time_ns()

        self._frames_since_last_show = 0
        self._last_fps_show_time = time.time_ns()
        self.fps = 0

        self.first = True  # temporary, until arena changes per frame

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def keyPressEvent(self, event):
        if self.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.player_input.up = True
        elif event.key() == Qt.Key_S:
            self.player_input.down = True
        elif event.key() == Qt.Key_A:
            self.player_input.left = True
        elif event.key() == Qt.Key_D:
            self.player_input.right = True
        event.accept()

    def keyReleaseEvent(self, event):
        if self.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.player_input.up = False
        elif event.key() == Qt.Key_S:
            self.player_input.down = False
        elif event.key() == Qt.Key_A:
            self.player_input.left = False
        elif event.key() == Qt.Key_D:
            self.player_input.right = False
        event.accept()

    def init_arena(self):
        map_path = get_main_path() + "/test_map.json"
        self.arena = load_map(map_path)

    def init_robots(self):
        self.robots.append(Robot(is_player=True, position=Vector(500, 500)))
        self.robots.append(Robot(is_player=False, position=Vector(250, 250)))
        self.robots.append(Robot(is_player=False, position=Vector(250, 750)))
        self.robots.append(Robot(is_player=False, position=Vector(750, 250)))
        self.robots.append(Robot(is_player=False, position=Vector(750, 750)))
        for robot in self.robots:
            if robot.is_player:
                self.player_input = robot.input
                break

    def paintEvent(self, event):
        curr_time_ns = time.time_ns()
        delta_time = ns_to_s(curr_time_ns - self._last_frame_time_ns)
        self._last_frame_time_ns = curr_time_ns

        self._frames_since_last_show += 1
        last_fps_show_delta = ns_to_s(curr_time_ns - self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = curr_time_ns

        if self.first:  # draw arena only one time (for now)
            arena_painter = QPainter(self.arena_pixmap)
            self.arena.draw(arena_painter)
            arena_painter.end()
            self.first = False

        for robot in self.robots:
            robot.update(delta_time)

        qp = QPainter(self)

        # draw arena pixmap
        qp.drawPixmap(QPoint(), self.arena_pixmap)

        # draw robots
        for robot in self.robots:
            robot.draw(qp)

        qp.setPen(Qt.red)
        qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.setWindowTitle("Robo Arena")
    window.show()
    while window.running:  # main loop
        window.update()
        app.processEvents()

    sys.exit(0)


if __name__ == '__main__':
    main()
