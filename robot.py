from util import Vector, ns_to_s
import time
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPoint


class Robot:
    def __init__(self, radius=15, position=Vector(0.0, 0.0), rotation=Vector(0.0, 0.0)):
        self.radius = radius
        self.position = position
        self.rotation = rotation
        self.velocity = Vector(0.0, 0.0)  # in px/s
        self.ang_velocity = 0.0  # in deg/s
        self.__last_move_time_ns = time.time_ns()

    def draw(self, qp):
        qp.setPen(QColor(200, 200, 200))
        qp.drawEllipse(QPoint(self.position.x, self.position.y), self.radius, self.radius)

    def update(self):
        time_diff = ns_to_s(time.time_ns() - self.__last_move_time_ns)
        self.position.add(self.velocity.mult(time_diff))
        self.rotation += self.ang_velocity * time_diff

        self.__last_move_time_ns = time.time_ns()
