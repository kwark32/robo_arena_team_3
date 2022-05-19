import math


class Vector:
    def __init__(self, x=0, y=0, other=None):
        self.x = x
        self.y = y
        self._x_for_mag = 0.0
        self._y_for_mag = 0.0
        self._mag = 0.0
        if other is not None:
            self.x = other.x
            self.y = other.y

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

    def magnitude(self):
        if self.x != self._x_for_mag or self.y != self._y_for_mag:
            self._mag = math.sqrt(self.x * self.x + self.y * self.y)
        return self._mag

    def set_magnitude(self, value):
        mag = self.magnitude()
        if mag != 0:
            factor = value / mag
        else:
            factor = 0
        self.mult(factor)

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
