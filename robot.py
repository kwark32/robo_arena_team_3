import math
import time

from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint
from util import Vector, ns_to_s, limit


class Robot:
    def __init__(self, radius=15,
                 position=Vector(0.0, 0.0), rotation=0.0,
                 max_velocity=120, max_ang_velocity=3,
                 max_accel=60, max_ang_accel=1.5):
        self.radius = radius
        self.position = position
        self.rotation = rotation  # in rad
        self.velocity = Vector(0.0, 0.0)  # in px/s
        self.ang_velocity = 0.0  # in rad/s
        self.accel = Vector(0.0, 0.0)  # in px/s^2
        self.ang_accel = 0.0  # in rad/s^2
        self.max_velocity = max_velocity
        self.max_ang_velocity = max_ang_velocity
        self.max_accel = max_accel
        self.max_ang_accel = max_ang_accel
        self._last_move_time_ns = time.time_ns()

    def draw(self, qp):
        qp.setPen(QColor(46, 26, 71))
        qp.setBrush(QColor(255, 53, 184))
        qp.drawEllipse(QPoint(round(self.position.x),
                              round(self.position.y)),
                       self.radius, self.radius)
        qp.drawLine(round(self.position.x), round(self.position.y),
                    round(self.position.x + self.radius * math.sin(self.rotation)),
                    round(self.position.y - self.radius * math.cos(self.rotation)))

    def update(self):
        time_diff = ns_to_s(time.time_ns() - self._last_move_time_ns)
        self._last_move_time_ns = time.time_ns()

        self.accel.limit_by_scalar(-self.max_accel, self.max_accel)

        velocity_change = Vector(other=self.accel)
        velocity_change.mult(time_diff)
        self.velocity.add(velocity_change)

        self.velocity.limit_by_scalar(-self.max_velocity, self.max_velocity)

        position_change = Vector(other=self.velocity)
        position_change.mult(time_diff)
        self.position.add(position_change)

        self.ang_accel = limit(self.ang_accel, -self.max_ang_accel, self.max_ang_accel)
        self.ang_velocity += self.ang_accel * time_diff

        self.ang_velocity = limit(self.ang_velocity, -self.max_ang_velocity, self.max_ang_velocity)
        self.rotation += self.ang_velocity * time_diff

        while self.rotation >= math.tau:
            self.rotation -= math.tau
        while self.rotation < 0:
            self.rotation += math.tau
