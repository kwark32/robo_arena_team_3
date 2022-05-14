class Vector:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

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
