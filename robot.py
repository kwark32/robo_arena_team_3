from util import Vector
import time


class Robot:
    radius = 15
    position = Vector(0, 0)
    rotation = 0
    velocity = Vector(0, 0) # in px/s
    __last_move_time_ns = 0

    def __init__(self, position=0, rotation=0):
        self.position = position
        self.rotation = rotation
        self.__last_move_time_ns = time.time_ns()

    def draw(self):
        print("Drawing robot...")

    def update(self):
        self.position.add(self.velocity.mult(self.__last_move_time_ns / 1000000))
