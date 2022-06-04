from PyQt5.QtGui import QPixmap
from weapons import TankCannon
from util import Vector, limit, get_main_path, draw_img_with_rot, limit_rot
from constants import ARENA_SIZE


class Robot:
    def __init__(self, physics_world, is_player=False, health=1000, radius=20, position=Vector(0, 0), rotation=0,
                 max_velocity=120, max_ang_velocity=4, max_accel=200, max_ang_accel=12):

        self.is_player = is_player

        self.input = None
        if is_player:
            self.input = PlayerInput()

        self.radius = radius

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

        self.last_position = position
        self.last_delta_time = 1

        texture_path = get_main_path() + "/textures/moving/"
        self.body_texture = QPixmap(texture_path + "tank_red_40.png")
        if is_player:
            self.body_texture = QPixmap(texture_path + "tank_blue_40.png")

        self.texture_size = Vector(self.body_texture.width(), self.body_texture.height())

        self.physics_world = physics_world

        self.physics_body = physics_world.add_rect(position, self.texture_size.x, self.texture_size.y,
                                                   rotation=-rotation, static=False, user_data=self)

        self.weapon = TankCannon(self.physics_world)

        self.health = int(health)
        self.is_dead = False

    def draw(self, qp):
        draw_img_with_rot(qp, self.body_texture, self.texture_size.x, self.texture_size.y, self.position, self.rotation)

    def update(self, delta_time, curr_time):
        real_local_velocity = self.position.copy()
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
            if self.input.shoot:
                self.weapon.shoot(curr_time, self, self.position, self.rotation)

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

        self.ang_accel = limit(self.ang_accel, -self.max_ang_accel, self.max_ang_accel)
        self.ang_velocity += self.ang_accel * delta_time

        self.ang_velocity = limit(self.ang_velocity, -self.max_ang_velocity, self.max_ang_velocity)
        self.rotation += self.ang_velocity * delta_time
        self.rotation = limit_rot(self.rotation)

        self.accel.limit_magnitude(self.max_accel)
        self.local_accel.limit_magnitude(self.max_accel)

        velocity_change = self.accel.copy()
        velocity_change.mult(delta_time)
        self.velocity.add(velocity_change)
        local_velocity_change = self.local_accel.copy()
        local_velocity_change.mult(delta_time)
        self.local_velocity.add(local_velocity_change)

        self.velocity.limit_magnitude(self.max_velocity)
        self.local_velocity.limit_magnitude(self.max_velocity)

        position_change = self.velocity.copy()
        rotated_local_velocity = self.local_velocity.copy()
        rotated_local_velocity.rotate(self.rotation)
        position_change.add(rotated_local_velocity)
        position_change.limit_magnitude(self.max_velocity)
        position_change.mult(delta_time)
        self.position.add(position_change)

        self.last_position = Vector(self.physics_body.position[0], ARENA_SIZE - self.physics_body.position[1])
        self.last_delta_time = delta_time

        self.physics_body.transform = ((self.position.x, ARENA_SIZE - self.position.y), -self.rotation)

    def update_ai(self, delta_time):
        self.ang_accel = self.max_ang_accel
        self.local_accel.y = self.max_accel

    def refresh_from_physics(self):
        if self.physics_body is not None:
            self.position.x = self.physics_body.position[0]
            self.position.y = ARENA_SIZE - self.physics_body.position[1]

    def take_damage(self, damage):
        self.health -= int(damage)
        if self.health <= 0:
            self.health = 0
            self.is_dead = True

    def die(self):
        self.physics_world.world.DestroyBody(self.physics_body)
        print("<cool tank explode animation> or something...")


class PlayerInput:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.shoot = False
