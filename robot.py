import math
import time

from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint
from util import Vector, ns_to_s, limit


class Robot:
    def __init__(self, radius=15,
                 position=Vector(0.0, 0.0), rotation=0.0,
                 max_velocity=90, max_ang_velocity=3,
                 max_accel=180, max_ang_accel=9):

        self.input = PlayerInput()

        self.radius = radius

        self.ang_accel = 0  # in rad/s^2
        self.ang_velocity = 0  # in rad/s

        self.position = position
        self.rotation = rotation  # in rad

        self.accel = Vector(0, 0)  # in px/s^2
        self.local_accel = Vector(0, 0)  # in px/s^2, local to robot

        self.velocity = Vector(0, 0)  # in px/s
        self.local_velocity = Vector(0, 0)  # in px/s, local to robot

        self.max_ang_accel = max_ang_accel
        self.max_ang_velocity = max_ang_velocity

        self.max_accel = max_accel
        self.max_velocity = max_velocity

        self._last_move_time_ns = time.time_ns()

    def draw(self, qp):
        qp.setPen(QColor(46, 26, 71))
        qp.setBrush(QColor(255, 53, 184))
        qp.drawEllipse(QPoint(round(self.position.x),
                              round(self.position.y)),
                       self.radius, self.radius)
        qp.drawLine(round(self.position.x), round(self.position.y),
                    round(self.position.x
                          + self.radius * math.sin(self.rotation)),
                    round(self.position.y
                          - self.radius * math.cos(self.rotation)))

    def update(self):
        delta_time = ns_to_s(time.time_ns() - self._last_move_time_ns)
        self._last_move_time_ns = time.time_ns()

        forward_velocity_goal = 0
        ang_velocity_goal = 0
        if self.input.up:
            forward_velocity_goal -= 1
        if self.input.down:
            forward_velocity_goal += 1
        if self.input.left:
            ang_velocity_goal -= 1
        if self.input.right:
            ang_velocity_goal += 1

        forward_velocity_goal *= self.max_velocity
        ang_velocity_goal *= self.max_ang_velocity

        self.local_accel.y = (forward_velocity_goal - self.local_velocity.y)
        self.local_accel.y /= delta_time
        self.ang_accel = (ang_velocity_goal - self.ang_velocity)
        self.ang_accel /= delta_time

        self.ang_accel = limit(self.ang_accel,
                               -self.max_ang_accel,
                               self.max_ang_accel)
        self.ang_velocity += self.ang_accel * delta_time

        self.ang_velocity = limit(self.ang_velocity,
                                  -self.max_ang_velocity,
                                  self.max_ang_velocity)
        self.rotation += self.ang_velocity * delta_time

        while self.rotation >= math.tau:
            self.rotation -= math.tau
        while self.rotation < 0:
            self.rotation += math.tau

        self.accel.limit_magnitude(self.max_accel)
        self.local_accel.limit_magnitude(self.max_accel)

        velocity_change = Vector(other=self.accel)
        velocity_change.mult(delta_time)
        self.velocity.add(velocity_change)
        local_velocity_change = Vector(other=self.local_accel)
        local_velocity_change.mult(delta_time)
        self.local_velocity.add(local_velocity_change)

        self.velocity.limit_magnitude(self.max_velocity)
        self.local_velocity.limit_magnitude(self.max_velocity)

        position_change = Vector(other=self.velocity)
        rotated_local_velocity = Vector(other=self.local_velocity)
        rotated_local_velocity.rotate(self.rotation)
        position_change.add(rotated_local_velocity)
        position_change.limit_magnitude(self.max_velocity)
        position_change.mult(delta_time)
        self.position.add(position_change)


class PlayerInput:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
