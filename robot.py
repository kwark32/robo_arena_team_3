import math

from transform import SimBody
from weapons import TankCannon
from util import Vector, get_main_path, draw_img_with_rot, painter_transform_with_rot
from globals import GameInfo, Fonts
from constants import FIXED_DELTA_TIME, MAX_ROBOT_HEALTH, DEBUG_MODE, ROBOT_COLLISION_SOUND_SPEED_FACTOR
from constants import MIN_SOUND_DELAY_FRAMES
from robot_AI import RobotAI
from sound_manager import SoundManager
from arena import TileType

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap, QPolygon
    from PyQt5.QtCore import QPoint


robot_texture_path = get_main_path() + "/textures/moving/"


class RobotInfo:
    def __init__(self, robot, physics_frame=0):
        self.robot_body = robot.sim_body.as_tuples()
        self.player_id = robot.robot_id
        self.next_bullet_id = robot.next_bullet_id
        self.health = robot.health
        self.weapon_class = robot.weapon.weapon_type
        self.last_shot_frame = robot.weapon.last_shot_frame
        self.player_name = robot.player_name
        self.last_position = robot.last_position.as_tuple()
        self.effects = []
        for effect in robot.effects:
            self.effects.append(effect.copy())
        self.effect_data = robot.effect_data
        self.input = robot.input

        self.died = False

        if robot.last_death_frame == physics_frame > 0:
            self.died = True

    def set_robot_values(self, robot):
        robot.robot_id = self.player_id
        robot.next_bullet_id = self.next_bullet_id
        robot.player_name = self.player_name
        robot.sim_body.set_tuples(self.robot_body)
        robot.extrapolation_body.set(robot.sim_body)
        robot.revert_effects()
        robot.effects = self.effects
        robot.effect_data = self.effect_data
        robot.health = self.health
        if robot.weapon is None or robot.weapon.weapon_type is not self.weapon_class:
            robot.weapon = self.weapon_class()
        robot.weapon.last_shot_frame = self.last_shot_frame
        robot.last_position = Vector(self.last_position[0], self.last_position[1])
        robot.forward_velocity_goal = 0
        robot.set_physics_body()
        if not robot.has_ai:
            robot.input = self.input
        if self.died:
            robot.die()


class Robot:
    def __init__(self, world_sim, robot_id=-1, is_player=False, has_ai=True,
                 size=Vector(40, 40), position=Vector(0, 0), rotation=0,
                 max_velocity=120, max_ang_velocity=4, max_accel=200, max_ang_accel=12, player_name=""):
        self.creation_frame = world_sim.physics_frame_count

        self.robot_id = robot_id
        if robot_id < 0:
            for robot in world_sim.robots:
                if robot.robot_id >= GameInfo.next_player_id:
                    GameInfo.next_player_id = robot.robot_id + 1
            self.robot_id = GameInfo.next_player_id
            GameInfo.next_player_id += 1
        self.next_bullet_id = 0

        self.player_name = player_name

        self.max_velocity = max_velocity
        self.max_ang_velocity = max_ang_velocity
        self.max_accel = max_accel
        self.max_ang_accel = max_ang_accel

        self.sim_body = SimBody(position=position, rotation=rotation, max_velocity=max_velocity,
                                max_ang_velocity=max_ang_velocity, max_accel=max_accel, max_ang_accel=max_ang_accel)
        self.extrapolation_body = self.sim_body.copy()

        self.effects = []
        self.effect_data = {}

        self.is_player = is_player
        self.has_ai = has_ai

        self.input = None

        self.size = size

        self.real_velocity = Vector(0, 0)

        self.last_position = position.copy()
        self.forward_velocity_goal = 0

        self.last_collision_sound_frame = 0

        self._body_texture = None
        self._texture_size = None

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.physics_body = self.physics_world.add_rect(Vector(position.x, position.y), self.size.x, self.size.y,
                                                        rotation=rotation, static=False, user_data=self)

        self.weapon = TankCannon(self.world_sim)

        self.max_health = MAX_ROBOT_HEALTH
        self.health = self.max_health
        self.to_remove = False
        self.is_dead = False
        self.last_death_frame = 0

        self.should_respawn = True
        self.robot_ai = None
        if has_ai:
            self.should_respawn = False
            self.robot_ai = RobotAI(self)

    @property
    def get_next_bullet_id(self):
        self.next_bullet_id += 1
        return self.next_bullet_id

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

        if DEBUG_MODE and self.robot_ai is not None and self.robot_ai.shortest_path is not None:
            painter_transform_with_rot(qp, Vector(0, 0), 0)
            qp.setPen(Fonts.fps_color)
            poly = QPolygon()
            tile_size = GameInfo.arena_tile_size
            for p in self.robot_ai.shortest_path:
                if p == self.robot_ai.shortest_path[0]:
                    poly.append(QPoint(int(self.sim_body.position.x), int(self.sim_body.position.y)))
                else:
                    poly.append(QPoint(int(p[0] * tile_size + tile_size / 2), int(p[1] * tile_size + tile_size / 2)))
            for p in reversed(self.robot_ai.shortest_path):
                if p == self.robot_ai.shortest_path[0]:
                    poly.append(QPoint(int(self.sim_body.position.x), int(self.sim_body.position.y)))
                else:
                    poly.append(QPoint(int(p[0] * tile_size + tile_size / 2), int(p[1] * tile_size + tile_size / 2)))

            qp.drawPolygon(poly)
            qp.restore()

    def update(self, delta_time):
        if int(self.health) <= 0:
            self.health = 0
            self.die()
            if not self.should_respawn:
                return
            elif self.health > self.max_health:
                self.health = self.max_health

        self.revert_effects()

        current_tile = self.get_center_tile()
        if current_tile.effect_class is not None:
            effect = current_tile.effect_class(FIXED_DELTA_TIME / 2)
            self.effects.append(effect)
            effect.world_sim = self.world_sim

        self.apply_effects(delta_time)

        # last_forward_velocity_goal = self.forward_velocity_goal

        self.real_velocity = self.sim_body.position.copy()
        self.real_velocity.sub(self.last_position)
        self.real_velocity.div(FIXED_DELTA_TIME)
        real_local_velocity = self.real_velocity.copy()
        real_local_velocity.rotate(-self.sim_body.rotation)

        self.sim_body.local_velocity.y = real_local_velocity.y

        if self.has_ai:
            if self.input is None:
                self.input = PlayerInput()
            self.robot_ai.update(delta_time)

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
                    if not self.weapon.shoot(self.robot_id, self.get_next_bullet_id,
                                             self.sim_body.position, self.sim_body.rotation):
                        self.next_bullet_id -= 1

            # if ((self.forward_velocity_goal == 0 and last_forward_velocity_goal != 0)
            #         or (self.forward_velocity_goal == 1 and self.sim_body.local_velocity.y < 0)
            #         or (self.forward_velocity_goal == -1 and self.sim_body.local_velocity.y > 0)):
            #     self.sim_body.local_velocity.y = real_local_velocity.y

            self.forward_velocity_goal *= self.sim_body.max_velocity
            ang_velocity_goal *= self.sim_body.max_ang_velocity

            self.sim_body.local_accel.y = (self.forward_velocity_goal - self.sim_body.local_velocity.y) / delta_time
            self.sim_body.ang_accel = (ang_velocity_goal - self.sim_body.ang_velocity) / delta_time

        self.sim_body.step(delta_time)
        self.extrapolation_body.set(self.sim_body)

        self.last_position = Vector(self.physics_body.position[0], self.physics_body.position[1])

        self.set_physics_body()

    def get_center_tile(self):
        tile_size = GameInfo.arena_tile_size
        tile_count = self.world_sim.arena.tile_count
        tile_position = self.sim_body.position.copy()
        tile_position.div(tile_size)
        tile_position.floor()
        tile_position.limit_range(Vector(0, 0), tile_count)
        return self.world_sim.arena.tiles[tile_position.y][tile_position.x]

    def set_physics_body(self):
        self.physics_body.transform = ((self.sim_body.position.x, self.sim_body.position.y), self.sim_body.rotation)

    def refresh_from_physics(self):
        if self.physics_body is not None:
            self.sim_body.position.x = self.physics_body.position[0]
            self.sim_body.position.y = self.physics_body.position[1]

    def apply_effects(self, delta_time):
        for effect in self.effects:
            effect.apply(self, delta_time)

    def revert_effects(self):
        expired_effects = []
        for effect in self.effects:
            effect.revert(self)
            if effect.duration <= 0:
                expired_effects.append(effect)

        for expired in expired_effects:
            self.effects.remove(expired)
        expired_effects.clear()

    def change_health(self, delta_healh):
        self.health += delta_healh

    def die(self):
        print("<cool tank explode animation> or something... (for robot ID " + str(self.robot_id) + ")")
        self.is_dead = True
        self.last_death_frame = self.world_sim.physics_frame_count
        if self.should_respawn:
            self.respawn()
        else:
            self.remove()

    def respawn(self):
        self.revert_effects()
        self.effects.clear()
        self.health = self.max_health
        self.sim_body.reset(position=Vector(self.world_sim.arena.size.x / 2, self.world_sim.arena.size.y / 2),
                            rotation=0)
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

    def set_position(self, position, stop_robot=False, stop_robot_rotation=False):
        self.last_position = position.copy()
        self.sim_body.position = position.copy()
        if stop_robot:
            self.real_velocity = (0, 0)
            self.sim_body.velocity = (0, 0)
            self.sim_body.local_velocity = (0, 0)
        if stop_robot_rotation:
            self.sim_body.ang_velocity = 0
        self.extrapolation_body.set(self.sim_body)
        self.set_physics_body()


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
        return player_input

    def to_string(self):
        return ("PlayerInput {\n  Up: " + str(self.up) + "\n  Down: " + str(self.down) + "\n  Left: "
                + str(self.left) + "\n  Right: " + str(self.right) + "\n  Shoot: " + str(self.shoot)
                + "\n  Shoot Pressed: " + str(self.shoot_pressed) + "\n}")


def collide_robot(robot, other, normal=Vector(0, 0)):
    if normal.equal(Vector(0, 0) or robot.real_velocity.equal(Vector(0, 0))):
        return

    normal.rotate(robot.sim_body.rotation)

    pos = robot.sim_body.position
    if isinstance(other, Robot):
        velocity = robot.real_velocity.diff(other.real_velocity)
        angle = velocity.angle(normal)
        mag = velocity.magnitude() * math.sin(angle)
        if (robot.world_sim.physics_frame_count > robot.last_collision_sound_frame + MIN_SOUND_DELAY_FRAMES
                and abs(mag) > robot.max_velocity * ROBOT_COLLISION_SOUND_SPEED_FACTOR):
            robot.last_collision_sound_frame = robot.world_sim.physics_frame_count
            SoundManager.instance.play_sfx("collision_tank_tank", pos=pos)
    elif isinstance(other, TileType) and other.has_collision:
        angle = robot.real_velocity.angle(normal)
        mag = robot.real_velocity.magnitude() * math.sin(angle)
        if (robot.world_sim.physics_frame_count > robot.last_collision_sound_frame + MIN_SOUND_DELAY_FRAMES
                and abs(mag) > robot.max_velocity * ROBOT_COLLISION_SOUND_SPEED_FACTOR):
            robot.last_collision_sound_frame = robot.world_sim.physics_frame_count
            SoundManager.instance.play_sfx("collision_tank_wall", pos=pos)
