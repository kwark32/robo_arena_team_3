import math

from os.path import dirname, abspath
from camera import CameraState
from globals import GameInfo


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

    def equal(self, other):
        return self.x == other.x and self.y == other.y

    def round(self):
        self.x = round(self.x)
        self.y = round(self.y)

    def floor(self):
        self.x = int(self.x)
        self.y = int(self.y)

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

    def limit_range(self, lower, upper):
        self.x = limit(self.x, lower.x, upper.x - 1)
        self.y = limit(self.y, lower.y, upper.y - 1)

    def lerp_to(self, other, amount):
        self.x = lerp(self.x, other.x, amount)
        self.y = lerp(self.y, other.y, amount)

    def diff(self, other):
        diff = other.copy()
        diff.sub(self)
        return diff

    def dist(self, other):
        diff = self.diff(other)
        return diff.magnitude()

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def signed_angle(self, from_vec=None):
        if from_vec is None:
            from_vec = Vector(0, 1)
        dot = from_vec.dot(self)
        det = from_vec.x * self.y - from_vec.y * self.x
        return math.atan2(det, dot)

    def angle(self, from_vec=None):
        if from_vec is None:
            from_vec = Vector(0, 1)
        mags = self.magnitude() * from_vec.magnitude()
        if mags > 0:
            cos = (self.x * from_vec.x + self.y * from_vec.y) / mags
            return math.acos(limit(cos, -1, 1))
        return 0

    def as_tuple(self):
        return self.x, self.y


def ns_to_s(ns):
    return (round(ns) >> 10) / 976562.5  # shift to ~us, then float division


def s_to_ns(s):
    return round(s * 976562.5) << 10  # float multiply to ~us, then shift to ns


def get_delta_time_s(now_ns, last_ns):
    return ns_to_s(now_ns - last_ns)


def limit(value, lower, upper):
    if value < lower:
        value = lower
    elif value > upper:
        value = upper
    return value


_main_path = dirname(abspath(__file__)) + "/"


def get_main_path():
    return _main_path


def rad_to_deg(value):
    return value * 57.2957795


def deg_to_rad(value):
    return value / 57.2957795


def is_object_on_screen(pos, radius=None):
    if CameraState.position is None:
        return True
    if radius is None:
        radius = CameraState.max_object_radius
    half_screen = GameInfo.window_reference_size.copy()
    half_screen.div(2)
    half_screen.add_scalar(radius)
    return (CameraState.position.x - half_screen.x <= pos.x <= CameraState.position.x + half_screen.x
            and CameraState.position.y - half_screen.y <= pos.y <= CameraState.position.y + half_screen.y)


def painter_transform_with_rot(qp, position, rotation):
    qp.save()
    cam_pos = Vector(0, 0)
    if CameraState.position is not None:
        cam_pos = GameInfo.window_reference_size.copy()
        cam_pos.div(2)
        cam_pos.sub(CameraState.position)
        cam_pos.round()
    position = position.copy()
    position.x += CameraState.x_offset
    qp.translate(round(position.x) + round(cam_pos.x), round(position.y) + round(cam_pos.y))
    if rotation != 0:
        qp.rotate(rad_to_deg(rotation))


def draw_img_with_rot(qp, img, width, height, position, rotation):
    if not is_object_on_screen(position):
        return
    painter_transform_with_rot(qp, position, rotation)
    qp.drawPixmap(-round(width / 2), -round(height / 2), img)
    qp.restore()


def draw_text_with_rot(qp, text, width, height, position, rotation):
    if CameraState.scale.x != CameraState.scale.y:
        offset = (CameraState.scale.x - CameraState.scale.y) * GameInfo.window_reference_size.x * 0.5
        position = position.copy()
        position.x += offset
    if not is_object_on_screen(position):
        return
    painter_transform_with_rot(qp, position, rotation)
    qp.drawText(-round(width / 2), -round(height / 2), text)
    qp.restore()


def limit_rot(value):
    while value >= math.tau:
        value -= math.tau
    while value < 0:
        value += math.tau
    return value


def is_point_inside_rect(point, top_left, bottom_right):
    return top_left.x <= point.x <= bottom_right.x and top_left.y <= point.y <= bottom_right.y


def lerp(a, b, t):
    return a + t * (b - a)
