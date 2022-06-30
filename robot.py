from transform import SimBody
from weapons import TankCannon
from util import Vector, get_main_path, draw_img_with_rot
from globals import GameInfo
from constants import ARENA_SIZE, FIXED_DELTA_TIME, MAX_ROBOT_HEALTH

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


robot_texture_path = get_main_path() + "/textures/moving/"


def set_robot_values(robot, robot_info):
    robot.robot_id = robot_info.player_id
    robot.player_name = robot_info.player_name
    robot.sim_body = robot_info.robot_body
    robot.extrapolation_body = robot_info.robot_body.copy()
    robot.health = robot_info.health
    if robot.weapon is None or robot.weapon.weapon_type is not robot_info.weapon_class:
        robot.weapon = robot_info.weapon_class()
    robot.weapon.last_shot_frame = robot_info.last_shot_frame
    robot.last_position = robot_info.last_position
    robot.forward_velocity_goal = 0
    robot.set_physics_body()
    if robot_info.died:
        robot.die()


class Robot:
    next_id = 0

    def __init__(self, world_sim, robot_id=-1, is_player=False, has_ai=True,
                 size=Vector(40, 40), position=Vector(0, 0), rotation=0,
                 max_velocity=120, max_ang_velocity=4, max_accel=200, max_ang_accel=12, player_name=""):

        self.robot_id = robot_id
        if robot_id == -1:
            self.robot_id = Robot.next_id
            Robot.next_id += 1

        self.player_name = player_name

        self.max_velocity = max_velocity
        self.max_ang_velocity = max_ang_velocity
        self.max_accel = max_accel
        self.max_ang_accel = max_ang_accel

        self.sim_body = SimBody(position=position, rotation=rotation, max_velocity=max_velocity,
                                max_ang_velocity=max_ang_velocity, max_accel=max_accel, max_ang_accel=max_ang_accel)
        self.extrapolation_body = self.sim_body.copy()

        self.effects = []

        self.is_player = is_player
        self.has_ai = has_ai

        self.should_respawn = True
        if has_ai:
            self.should_respawn = False

        self.input = None

        self.size = size

        self.real_velocity = Vector(0, 0)

        self.last_position = position.copy()
        self.forward_velocity_goal = 0

        self._body_texture = None
        self._texture_size = None

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.physics_body = self.physics_world.add_rect(Vector(position.x, ARENA_SIZE - position.y),
                                                        self.size.x, self.size.y,
                                                        rotation=-rotation, static=False, user_data=self)

        self.weapon = TankCannon(self.world_sim)

        self.max_health = MAX_ROBOT_HEALTH
        self.health = self.max_health
        self.to_remove = False
        self.is_dead = False
        self.last_death_frame = 0

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
        #self.extrapolation_body.step(delta_time)
        draw_img_with_rot(qp, self.body_texture, self.size.x, self.size.y,
                          self.extrapolation_body.position, self.extrapolation_body.rotation)

    def update(self, delta_time):
        if int(self.health) <= 0:
            self.health = 0
            self.die()
            if not self.should_respawn:
                return

        current_tile = self.get_center_tile()
        if current_tile.effect_class is not None:
            self.effects.append(current_tile.effect_class())

        self.apply_effects(delta_time)

        # last_forward_velocity_goal = self.forward_velocity_goal

        self.real_velocity = self.sim_body.position.copy()
        self.real_velocity.sub(self.last_position)
        self.real_velocity.div(FIXED_DELTA_TIME)
        real_local_velocity = self.real_velocity.copy()
        real_local_velocity.rotate(-self.sim_body.rotation)

        self.sim_body.local_velocity.y = real_local_velocity.y

        if not self.has_ai:
            if self.input is not None:
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
                    if self.weapon is not None:
                        self.weapon.shoot(self.robot_id, self.sim_body.position, self.sim_body.rotation)

                # if ((self.forward_velocity_goal == 0 and last_forward_velocity_goal != 0)
                #         or (self.forward_velocity_goal == 1 and self.sim_body.local_velocity.y < 0)
                #         or (self.forward_velocity_goal == -1 and self.sim_body.local_velocity.y > 0)):
                #     self.sim_body.local_velocity.y = real_local_velocity.y

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

        self.set_physics_body()

    def update_ai(self, delta_time):
        self.sim_body.ang_accel = self.sim_body.max_ang_accel
        self.sim_body.local_accel.y = self.sim_body.max_accel

    def get_center_tile(self):
        tile_size = self.world_sim.arena.tile_size
        tile_count = self.world_sim.arena.tile_count
        tile_position = self.sim_body.position.copy()
        tile_position.div(tile_size)
        tile_position.x = int(tile_position.x)
        tile_position.y = int(tile_position.y)
        tile_position.limit_by_scalar(0, tile_count - 1)
        return self.world_sim.arena.tiles[tile_position.y][tile_position.x]

    def set_physics_body(self):
        self.physics_body.transform = ((self.sim_body.position.x, ARENA_SIZE - self.sim_body.position.y),
                                       -self.sim_body.rotation)

    def refresh_from_physics(self):
        if self.physics_body is not None:
            self.sim_body.position.x = self.physics_body.position[0]
            self.sim_body.position.y = ARENA_SIZE - self.physics_body.position[1]

    def apply_effects(self, delta_time):
        expired_effects = []
        for effect in self.effects:
            effect.revert(self)
            if effect.duration <= 0:
                expired_effects.append(effect)

        for expired in expired_effects:
            self.effects.remove(expired)
        expired_effects.clear()

        for effect in self.effects:
            effect.apply(self, delta_time)

    def take_damage(self, damage):
        self.health -= damage

    def die(self):
        print("<cool tank explode animation> or something... (for robot ID " + str(self.robot_id) + ")")
        self.is_dead = True
        self.last_death_frame = self.world_sim.physics_frame_count
        if self.should_respawn:
            self.respawn()
        else:
            self.remove()

    def respawn(self):
        self.health = self.max_health
        self.sim_body.reset(position=Vector(ARENA_SIZE / 2, ARENA_SIZE / 2), rotation=0)
        self.extrapolation_body.set(self.sim_body)
        self.last_position = self.sim_body.position.copy()
        self.forward_velocity_goal = 0
        self.set_physics_body()
        self.is_dead = False

    def remove(self):
        self.to_remove = True
        if self.physics_body is not None:
            self.physics_world.world.DestroyBody(self.physics_body)
            self.physics_body = None


class PlayerInput:
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.shoot = False
        self.shoot_pressed = False

    def copy(self):
        player_input = PlayerInput()
        player_input.up = self.up
        player_input.down = self.down
        player_input.left = self.left
        player_input.right = self.right
        player_input.shoot = self.shoot
        player_input.shoot_pressed = self.shoot_pressed

    def to_string(self):
        return ("PlayerInput {\n  Up: " + self.up + "\n  Down: " + self.down + "\n  Left: " + self.left + "\n  Right: "
                + self.right + "\n  Shoot: " + self.shoot + "\n  Shoot Pressed: " + self.shoot_pressed + "\n}")
