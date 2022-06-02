import math

from PyQt5.QtGui import QPixmap
from util import Vector, limit, get_main_path, draw_img_with_rot
from constants import ROBOT_TEXTURE_SIZE, ARENA_SIZE


class Robot:
    def __init__(self, is_player=False, radius=20,
                 position=Vector(0.0, 0.0), rotation=0.0,
                 max_velocity=90, max_ang_velocity=3,
                 max_accel=180, max_ang_accel=9,
                 physics_world=None):

        self.is_player = is_player

        self.input = None
        if is_player:
            self.input = PlayerInput()

        self.radius = radius

        self.ang_accel = 0  # in rad/s^2
        self.ang_velocity = 0  # in rad/s

        self.position = position
        self.rotation = rotation  # in rad

        self.accel = Vector(0, 0)  # in px/s^2
        self.local_accel = Vector(0, 0)  # in px/s^2, local to robot

        self.velocity = Vector(0, 0)  # in px/s
        self.local_velocity = Vector(0, 0)  # in px/s, local to robot

        self.max_ang_accel = max_ang_accel
        self.max_ang_velocity = max_ang_velocity

        self.max_accel = max_accel
        self.max_velocity = max_velocity

        self.last_position = position
        self.last_delta_time = 1

        texture_path = get_main_path() + "/textures/moving/"
        self.body_texture = QPixmap(texture_path + "tank_red_"
                                    + str(ROBOT_TEXTURE_SIZE) + ".png")
        if is_player:
            self.body_texture = QPixmap(texture_path + "tank_blue_"
                                        + str(ROBOT_TEXTURE_SIZE) + ".png")

        self.physics_body = None
        if physics_world is not None:
            self.physics_body = physics_world.add_rect(position,
                                                       ROBOT_TEXTURE_SIZE,
                                                       ROBOT_TEXTURE_SIZE,
                                                       rotation=rotation,
                                                       static=False)

    def draw(self, qp):
        draw_img_with_rot(qp, self.body_texture, ROBOT_TEXTURE_SIZE,
                          self.position, self.rotation)

    def update(self, delta_time):
        if self.physics_body is None:
            return

        real_local_velocity = Vector(other=self.position)
        real_local_velocity.sub(self.last_position)
        real_local_velocity.div(self.last_delta_time)
        real_local_velocity.rotate(-self.rotation)

        if self.is_player:
            forward_velocity_goal = 0
            ang_velocity_goal = 0
            if self.input.up:
                forward_velocity_goal += 1
            if self.input.down:
                forward_velocity_goal -= 1
            if self.input.left:
                ang_velocity_goal -= 1
            if self.input.right:
                ang_velocity_goal += 1

            if (forward_velocity_goal == 0
                    or (forward_velocity_goal == 1
                        and self.local_velocity.y < 0)
                    or (forward_velocity_goal == -1
                        and self.local_velocity.y > 0)):
                self.local_velocity.y = real_local_velocity.y

            forward_velocity_goal *= self.max_velocity
            ang_velocity_goal *= self.max_ang_velocity

            self.local_accel.y = forward_velocity_goal - self.local_velocity.y
            self.local_accel.y /= delta_time
            self.ang_accel = ang_velocity_goal - self.ang_velocity
            self.ang_accel /= delta_time
        else:
            self.update_ai(delta_time)

        self.ang_accel = limit(self.ang_accel,
                               -self.max_ang_accel,
                               self.max_ang_accel)
        self.ang_velocity += self.ang_accel * delta_time

        self.ang_velocity = limit(self.ang_velocity,
                                  -self.max_ang_velocity,
                                  self.max_ang_velocity)
        self.rotation += self.ang_velocity * delta_time

        while self.rotation >= math.tau:
            self.rotation -= math.tau
        while self.rotation < 0:
            self.rotation += math.tau

        self.accel.limit_magnitude(self.max_accel)
        self.local_accel.limit_magnitude(self.max_accel)

        velocity_change = Vector(other=self.accel)
        velocity_change.mult(delta_time)
        self.velocity.add(velocity_change)
        local_velocity_change = Vector(other=self.local_accel)
        local_velocity_change.mult(delta_time)
        self.local_velocity.add(local_velocity_change)

        self.velocity.limit_magnitude(self.max_velocity)
        self.local_velocity.limit_magnitude(self.max_velocity)

        position_change = Vector(other=self.velocity)
        rotated_local_velocity = Vector(other=self.local_velocity)
        rotated_local_velocity.rotate(self.rotation)
        position_change.add(rotated_local_velocity)
        position_change.limit_magnitude(self.max_velocity)
        position_change.mult(delta_time)
        self.position.add(position_change)

        self.last_position = Vector(self.physics_body.position[0],
                                    ARENA_SIZE - self.physics_body.position[1])
        self.last_delta_time = delta_time

        self.physics_body.position = (self.position.x,
                                      ARENA_SIZE - self.position.y)
        self.physics_body.angle = -self.rotation

    def update_ai(self, delta_time):
        self.ang_accel = self.max_ang_accel
        self.local_accel = Vector(0, self.max_accel)

    def refresh_from_physics(self):
        if self.physics_body is not None:
            self.position.x = self.physics_body.position[0]
            self.position.y = ARENA_SIZE - self.physics_body.position[1]


class PlayerInput:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
