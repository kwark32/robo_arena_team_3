import math

from os.path import dirname, abspath


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._x_for_mag = 0
        self._y_for_mag = 0
        self._mag = 0

    def to_string(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def copy(self):
        return Vector(self.x, self.y)

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def add_scalar(self, other):
        self.x += other
        self.y += other

    def sub(self, other):
        self.x -= other.x
        self.y -= other.y

    def sub_scalar(self, other):
        self.x -= other
        self.y -= other

    def mult(self, other):
        self.x *= other
        self.y *= other

    def div(self, other):
        self.x /= other
        self.y /= other

    def rotate(self, angle):
        x = self.x
        y = self.y
        self.x = x * math.cos(angle) - y * math.sin(angle)
        self.y = x * math.sin(angle) + y * math.cos(angle)

    def magnitude(self):
        if self.x != self._x_for_mag or self.y != self._y_for_mag:
            self._mag = math.sqrt(self.x * self.x + self.y * self.y)
            self._x_for_mag = self.x
            self._y_for_mag = self.y
        return self._mag

    def set_magnitude(self, value):
        mag = self.magnitude()
        if mag != 0:
            factor = value / mag
        else:
            factor = 0
        self.mult(factor)

    def limit_magnitude(self, value):
        if self.magnitude() > value:
            self.set_magnitude(value)

    def limit_by_scalar(self, lower, upper):
        self.x = limit(self.x, lower, upper)
        self.y = limit(self.y, lower, upper)

    def limit(self, lower, upper):
        self.x = limit(self.x, lower.x, upper.x)
        self.y = limit(self.y, lower.y, upper.y)


def ns_to_s(ns):
    return (round(ns) >> 10) / 976562.5  # shift to ~us, then float division


def limit(value, lower, upper):
    if value < lower:
        value = lower
    elif value > upper:
        value = upper
    return value


def get_main_path():
    return dirname(abspath(__file__))


def rad_to_deg(value):
    return value * 57.2957795


def deg_to_rad(value):
    return value / 57.2957795


def draw_img_with_rot(qp, img, width, height, position, rotation):
    qp.translate(position.x, position.y)
    qp.rotate(rad_to_deg(rotation))
    qp.drawPixmap(-round(width / 2), -round(height / 2), img)
    qp.resetTransform()
