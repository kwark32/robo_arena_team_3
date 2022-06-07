from transform import SimBody
from weapons import TankCannon
from util import Vector, get_main_path, draw_img_with_rot
from constants import GameInfo, ARENA_SIZE

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


robot_texture_path = get_main_path() + "/textures/moving/"


class Robot:
    def __init__(self, world_sim, is_player=False, has_ai=True, health=1000,
                 size=Vector(40, 40), position=Vector(0, 0), rotation=0,
                 max_velocity=120, max_ang_velocity=4, max_accel=200, max_ang_accel=12):

        self.sim_body = SimBody(position=position, rotation=rotation, max_velocity=max_velocity,
                                max_ang_velocity=max_ang_velocity, max_accel=max_accel, max_ang_accel=max_ang_accel)
        self.extrapolation_body = self.sim_body.copy()

        self.is_player = is_player
        self.has_ai = has_ai

        self.input = None
        if not has_ai:
            self.input = PlayerInput()

        self.size = size

        self.real_velocity = Vector(0, 0)

        self.last_position = position
        self.last_delta_time = 1

        self.forward_velocity_goal = 0

        self._body_texture = None
        self._texture_size = None

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.physics_body = self.physics_world.add_rect(position, self.size.x, self.size.y,
                                                        rotation=-rotation, static=False, user_data=self)

        self.weapon = TankCannon(self.world_sim)

        self.health = int(health)
        self.is_dead = False

    @property
    def body_texture(self):
        if self._body_texture is None:
            self._body_texture = QPixmap(robot_texture_path + "tank_red_40.png")
            if self.is_player:
                self._body_texture = QPixmap(robot_texture_path + "tank_blue_40.png")
            if self._body_texture.width() != self.size.x or self._body_texture.height() != self.size.y:
                print("WARN: Robot texture size is not equal to robot (collider) size!")
        return self._body_texture

    def draw(self, qp, delta_time):
        self.extrapolation_body.step(delta_time)
        draw_img_with_rot(qp, self.body_texture, self.size.x, self.size.y,
                          self.extrapolation_body.position, self.extrapolation_body.rotation)

    def update(self, delta_time, curr_time):
        last_forward_velocity_goal = self.forward_velocity_goal

        self.real_velocity = self.sim_body.position.copy()
        self.real_velocity.sub(self.last_position)
        self.real_velocity.div(self.last_delta_time)
        real_local_velocity = self.real_velocity.copy()
        real_local_velocity.rotate(-self.sim_body.rotation)

        if not self.has_ai:
            self.forward_velocity_goal = 0
            ang_velocity_goal = 0
            if self.input.up:
                self.forward_velocity_goal += 1
            if self.input.down:
                self.forward_velocity_goal -= 1
            if self.input.left:
                ang_velocity_goal -= 1
            if self.input.right:
                ang_velocity_goal += 1
            if self.input.shoot or self.input.shoot_pressed:
                self.input.shoot_pressed = False
                self.weapon.shoot(curr_time, self, self.sim_body.position, self.sim_body.rotation)

            if ((self.forward_velocity_goal == 0 and last_forward_velocity_goal != 0)
                    or (self.forward_velocity_goal == 1 and self.sim_body.local_velocity.y < 0)
                    or (self.forward_velocity_goal == -1 and self.sim_body.local_velocity.y > 0)):
                pass
            self.sim_body.local_velocity.y = real_local_velocity.y

            self.forward_velocity_goal *= self.sim_body.max_velocity
            ang_velocity_goal *= self.sim_body.max_ang_velocity

            self.sim_body.local_accel.y = (self.forward_velocity_goal - self.sim_body.local_velocity.y) / delta_time
            self.sim_body.ang_accel = (ang_velocity_goal - self.sim_body.ang_velocity) / delta_time
        else:
            self.update_ai(delta_time)

        self.sim_body.step(delta_time)
        if not GameInfo.is_headless:
            self.extrapolation_body.set(self.sim_body)

        self.last_position = Vector(self.physics_body.position[0], ARENA_SIZE - self.physics_body.position[1])
        self.last_delta_time = delta_time

        self.physics_body.transform = ((self.sim_body.position.x, ARENA_SIZE - self.sim_body.position.y),
                                       -self.sim_body.rotation)

    def update_ai(self, delta_time):
        self.sim_body.ang_accel = self.sim_body.max_ang_accel
        self.sim_body.local_accel.y = self.sim_body.max_accel

    def refresh_from_physics(self):
        if self.physics_body is not None:
            self.sim_body.position.x = self.physics_body.position[0]
            self.sim_body.position.y = ARENA_SIZE - self.physics_body.position[1]

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
        self.shoot_pressed = False
        self.shoot = False
