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

    def limit_by_scalar(self, lower, upper):
        self.x = limit_scalar(self.x, lower, upper)
        self.y = limit_scalar(self.y, lower, upper)

    def limit(self, lower, upper):
        self.x = limit_scalar(self.x, lower.x, upper.x)
        self.y = limit_scalar(self.y, lower.y, upper.y)


def ns_to_s(ns):
    return (round(ns) >> 10) / 976562.5  # shift to ~us, then float division


def limit_scalar(value, lower, upper):
    if value < lower:
        value = lower
    elif value > upper:
        value = upper
    return value
