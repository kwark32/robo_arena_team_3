class Vector:
    def __init__(self, x=0, y=0, other=None):
        self.x = x
        self.y = y
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


def ns_to_s(ns):
    return ns / 1000000.0
