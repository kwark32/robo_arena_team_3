from util import Vector, ns_to_s
import time


class Robot:
    radius = 15
    position = Vector(0.0, 0.0)
    rotation = 0.0
    velocity = Vector(0.0, 0.0)  # in px/s
    ang_velocity = 0.0  # in deg/s
    __last_move_time_ns = 0

    def __init__(self, position=0, rotation=0):
        self.position = position
        self.rotation = rotation
        self.__last_move_time_ns = time.time_ns()

    def draw(self):
        print("Drawing robot...")

    def update(self):
        time_diff = ns_to_s(time.time_ns() - self.__last_move_time_ns)
        self.position.add(self.velocity.mult(time_diff))
        self.rotation += self.ang_velocity * time_diff

        self.__last_move_time_ns = time.time_ns()
