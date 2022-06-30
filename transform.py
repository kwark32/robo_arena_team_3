from util import Vector, limit, limit_rot


def pos_change_from_velocity_accel(delta_time, velocity, accel, max_velocity, max_accel, dont_modify=False):
    if dont_modify:
        accel = accel.copy()

    accel.limit_magnitude(max_accel)

    velocity_change = accel.copy()
    velocity_change.mult(delta_time)
    velocity.add(velocity_change)

    if dont_modify:
        velocity = velocity.copy()

    velocity.limit_magnitude(max_velocity)

    position_change = velocity.copy()
    position_change.mult(delta_time)
    return position_change


def rot_change_from_velocity_accel(delta_time, ang_velocity, ang_accel, max_ang_velocity, max_ang_accel,
                                   body=None, dont_modify=False):
    if not dont_modify and body is None:
        dont_modify = True

    ang_accel = limit(ang_accel, -max_ang_accel, max_ang_accel)
    if not dont_modify:
        body.ang_accel = ang_accel

    ang_velocity += ang_accel * delta_time

    ang_velocity = limit(ang_velocity, -max_ang_velocity, max_ang_velocity)
    if not dont_modify:
        body.ang_velocity = ang_velocity

    return ang_velocity * delta_time


class SimpleBody:
    def __init__(self, position=Vector(0, 0), rotation=0):
        self.position = position.copy()
        self.rotation = rotation

        self.local_velocity = Vector(0, 0)

        self._was_reset = False

    def copy(self):
        body = SimpleBody()
        body.set(self)
        return body

    def set(self, other):
        self.position = other.position
        self.rotation = other.rotation

        self.local_velocity = other.local_velocity

    def step(self, delta_time):
        if self._was_reset:
            self._was_reset = True
            return

        movement = self.local_velocity.copy()
        movement.rotate(self.rotation)
        movement.mult(delta_time)
        self.position.add(movement)

    def reset(self, position=Vector(0, 0), rotation=0):
        self.position = position.copy()
        self.rotation = rotation

        self.local_velocity = Vector(0, 0)

        self._was_reset = False


class SimBody:
    def __init__(self, position=Vector(0, 0), rotation=0, max_velocity=0,
                 max_ang_velocity=0, max_accel=0, max_ang_accel=0):
        self.ang_accel = 0  # in rad/s^2
        self.ang_velocity = 0  # in rad/s

        self.position = position.copy()
        self.rotation = rotation  # in rad

        self.accel = Vector(0, 0)  # in px/s^2
        self.local_accel = Vector(0, 0)  # in px/s^2, local to robot

        self.velocity = Vector(0, 0)  # in px/s
        self.local_velocity = Vector(0, 0)  # in px/s, local to robot

        self.max_ang_accel = max_ang_accel
        self.max_ang_velocity = max_ang_velocity

        self.max_accel = max_accel
        self.max_velocity = max_velocity

        self._was_reset = False

    def copy(self):
        body = SimBody()
        body.set(self)
        return body

    def set(self, other):
        self.position = other.position
        self.rotation = other.rotation
        self.max_velocity = other.max_velocity
        self.max_ang_velocity = other.max_ang_velocity
        self.max_accel = other.max_accel
        self.max_ang_accel = other.max_ang_accel

        self.ang_accel = other.ang_accel
        self.ang_velocity = other.ang_velocity
        self.accel = other.accel
        self.local_accel = other.local_accel
        self.velocity = other.velocity
        self.local_velocity = other.local_velocity

    def step(self, delta_time):
        if self._was_reset:
            self._was_reset = False
            return

        if self.max_velocity < 0:
            self.max_velocity = 0
        if self.max_ang_velocity < 0:
            self.max_ang_velocity = 0
        if self.max_accel < 0:
            self.max_accel = 0
        if self.max_ang_accel < 0:
            self.max_ang_accel = 0

        pos_change = pos_change_from_velocity_accel(delta_time, self.velocity, self.accel,
                                                    self.max_velocity, self.max_accel)
        local_pos_change = pos_change_from_velocity_accel(delta_time, self.local_velocity, self.local_accel,
                                                          self.max_velocity, self.max_accel)
        local_pos_change.rotate(self.rotation)
        pos_change.add(local_pos_change)
        pos_change.limit_magnitude(self.max_velocity * delta_time)
        pos_change.add(self.position)
        self.position = pos_change

        rot_change = rot_change_from_velocity_accel(delta_time, self.ang_velocity, self.ang_accel,
                                                    self.max_ang_velocity, self.max_ang_accel, body=self)

        new_rot = self.rotation + rot_change
        new_rot = limit_rot(new_rot)
        self.rotation = new_rot

    def reset(self, position=Vector(0, 0), rotation=0):
        self.ang_accel = 0  # in rad/s^2
        self.ang_velocity = 0  # in rad/s

        self.position = position.copy()
        self.rotation = rotation  # in rad

        self.accel = Vector(0, 0)  # in px/s^2
        self.local_accel = Vector(0, 0)  # in px/s^2, local to robot

        self.velocity = Vector(0, 0)  # in px/s
        self.local_velocity = Vector(0, 0)  # in px/s, local to robot

        self._was_reset = True
