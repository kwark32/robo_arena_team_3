import time

from PyQt5.QtGui import QPainter, QPixmap, QPolygon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from robot import Robot
from util import Vector, get_main_path, ns_to_s
from json_interface import load_map
from physics import PhysicsWorld
from constants import ARENA_SIZE, DEBUG_MODE


class WorldScene(QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.physics_world = PhysicsWorld()
        self.arena = None
        self.robots = []
        self.player_input = None

        self.init_arena(size)
        self.init_robots()

        self.init_ui()
        self.arena_pixmap = QPixmap(size, size)

        self._last_frame_time_ns = time.time_ns()

        self._frames_since_last_show = 0
        self._last_fps_show_time = time.time_ns()
        self.fps = 0

        self.first = True  # temporary, until arena changes per frame

    def init_ui(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)
        self.show()

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

    def init_arena(self, size):
        map_path = get_main_path() + "/test_map.json"
        self.arena = load_map(map_path, size, physics_world=self.physics_world)

    def init_robots(self):
        self.robots.append(Robot(is_player=True, position=Vector(500, 500),
                                 physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(250, 250),
                                 physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(250, 750),
                                 physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(750, 250),
                                 physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(750, 750),
                                 physics_world=self.physics_world))

        for robot in self.robots:
            if robot.is_player:
                self.player_input = robot.input
                break

    def update_world(self):
        curr_time_ns = time.time_ns()
        delta_time = ns_to_s(curr_time_ns - self._last_frame_time_ns)
        self._last_frame_time_ns = curr_time_ns

        self._frames_since_last_show += 1
        last_fps_show_delta = ns_to_s(curr_time_ns - self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = curr_time_ns

        for robot in self.robots:
            robot.update(delta_time)

        # maybe delta_time instead of 0.016 (~1/60th s)
        self.physics_world.world.Step(0.016, 0, 10)

        for robot in self.robots:
            robot.refresh_from_physics()

    def paintEvent(self, event):
        self.update_world()

        if self.first:  # draw arena only one time (for now)
            arena_painter = QPainter(self.arena_pixmap)
            self.arena.draw(arena_painter)
            arena_painter.end()
            self.first = False

        qp = QPainter(self)
        qp.setPen(Qt.red)

        # draw arena pixmap
        qp.drawPixmap(QPoint(), self.arena_pixmap)

        # draw robots
        for robot in self.robots:
            robot.draw(qp)

        # debugging physics shapes
        if DEBUG_MODE:
            for body in self.physics_world.world.bodies:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    vertices = [(body.transform * v) for v in shape.vertices]
                    vertices = [(v[0], ARENA_SIZE - v[1]) for v in vertices]
                    poly = QPolygon()
                    for vert in vertices:
                        poly.append(QPoint(vert[0], vert[1]))
                    qp.drawPolygon(poly)

        qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()