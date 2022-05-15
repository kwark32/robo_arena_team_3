import math
import time

from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint
from util import Vector, ns_to_s


class Robot:
    def __init__(self, radius=15, position=Vector(0.0, 0.0), rotation=0.0, move_speed=60):
        self.radius = radius
        self.position = position
        self.rotation = rotation  # in rad
        self.velocity = Vector(0.0, 0.0)  # in px/s
        self.ang_velocity = 0.0  # in rad/s
        self.move_speed = move_speed
        self._last_move_time_ns = time.time_ns()

    def draw(self, qp):
        qp.setPen(QColor(46, 26, 71))
        qp.setBrush(QColor(255, 53, 184))
        qp.drawEllipse(QPoint(round(self.position.x),
                              round(self.position.y)),
                       self.radius, self.radius)
        qp.drawLine(self.position.x, self.position.y,
                    self.position.x + self.radius * math.sin(self.rotation),
                    self.position.y - self.radius * math.cos(self.rotation))

    def update(self):
        time_diff = ns_to_s(time.time_ns() - self._last_move_time_ns)
        move = Vector(other=self.velocity)
        move.mult(time_diff)
        self.position.add(move)
        self.rotation += self.ang_velocity * time_diff
        while self.rotation > math.tau:
            self.rotation -= math.tau
        while self.rotation < 0:
            self.rotation += math.tau

        self._last_move_time_ns = time.time_ns()
