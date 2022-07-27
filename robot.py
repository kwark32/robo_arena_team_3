import math

import pixmap_resource_manager as prm

from transform import SimBody
from weapons import TankCannonWeapon, weapon_classes
from util import Vector, draw_img_with_rot, painter_transform_with_rot
from globals import GameInfo, Fonts
from constants import FIXED_DELTA_TIME, MAX_ROBOT_HEALTH, DEBUG_MODE, ROBOT_COLLISION_SOUND_SPEED_FACTOR
from constants import MIN_SOUND_DELAY_FRAMES, RESPAWN_DELAY
from robot_AI import RobotAI
from sound_manager import SoundManager
from arena import TileType
from animation import Animation
from effects import get_effect_from_data_list

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPolygon
    from PyQt5.QtCore import QPoint


robot_texture_path = "textures/moving/tanks/"


class RobotInfo:
    def __init__(self, robot):
        self.robot_body = robot.sim_body.as_tuples()
        self.player_id = robot.robot_id
        self.next_bullet_id = robot.next_bullet_id
        self.health = robot.health
        self.weapon_class_id = robot.weapon.weapon_type.id
        self.last_shot_frame = robot.weapon.last_shot_frame
        self.player_name = robot.player_name
        self.last_position = robot.last_position.as_tuple()
        self.effects = [e.get_data_list() for e in robot.effects]
        self.effect_data = robot.effect_data
        self.input = robot.input
        self.kills = robot.kills
        self.is_dead = robot.is_dead
        self.last_death_frame = robot.last_death_frame

    def set_robot_values(self, robot, physics_frame=0):
        robot.robot_id = self.player_id
        robot.next_bullet_id = self.next_bullet_id
        robot.player_name = self.player_name
        robot.sim_body.set_tuples(self.robot_body)
        robot.extrapolation_body.set(robot.sim_body)
        robot.revert_effects()
        robot.effects = [get_effect_from_data_list(e, robot.world_sim) for e in self.effects]
        robot.effect_data = self.effect_data
        robot.health = self.health
        robot.kills = self.kills
        if robot.weapon is None or robot.weapon.weapon_type.id != self.weapon_class_id:
            weapon_class = weapon_classes[self.weapon_class_id]
            robot.weapon = weapon_class()
        robot.weapon.last_shot_frame = self.last_shot_frame
        robot.last_position = Vector(self.last_position[0], self.last_position[1])
        robot.forward_velocity_goal = 0
        robot.last_death_frame = self.last_death_frame
        if robot.physics_body is None:
            robot.create_physics_body()
        robot.set_physics_body()
        if not robot.has_ai:
            robot.input = self.input
        if self.is_dead:
            if robot.last_death_frame == physics_frame:
                robot.die()
            robot.is_dead = True


class Robot:
    size = Vector(32, 32)
    turret_texture_center_offset = Vector(0, 10)

    def __init__(self, world_sim, robot_id=-1, is_player=False, has_ai=True, should_respawn=False,
                 position=Vector(0, 0), rotation=0, player_name=""):
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

        self.max_velocity = GameInfo.robot_max_velocity
        self.max_ang_velocity = GameInfo.robot_max_ang_velocity
        self.max_accel = GameInfo.robot_max_accel
        self.max_ang_accel = GameInfo.robot_max_ang_accel

        self.sim_body = SimBody(position=position, rotation=rotation,
                                max_velocity=self.max_velocity, max_ang_velocity=self.max_ang_velocity,
                                max_accel=self.max_accel, max_ang_accel=self.max_ang_accel)
        self.extrapolation_body = self.sim_body.copy()

        self.effects = []
        self.effect_data = {}

        self.is_player = is_player
        self.has_ai = has_ai

        self.input = None

        self.size = Robot.size.copy()

        self.real_velocity = Vector(0, 0)
        self.collider_push = Vector(0, 0)

        self.last_position = position.copy()
        self.forward_velocity_goal = 0

        self.last_collision_sound_frame = 0

        self._body_texture = None
        self._turret_texture = None

        self.world_sim = world_sim
        self.physics_world = world_sim.physics_world

        self.physics_body = None
        self.create_physics_body()

        self.weapon = TankCannonWeapon(self.world_sim)
        self.damage_factor = 1
        self.bullet_resistance_factor = 1

        self.max_health = MAX_ROBOT_HEALTH
        self.health = self.max_health
        self.to_remove = False
        self.is_dead = False
        self.last_death_frame = 0

        self.kills = 0

        self.should_respawn = should_respawn
        self.robot_ai = None
        if has_ai:
            self.robot_ai = RobotAI(self)

    @property
    def get_next_bullet_id(self):
        self.next_bullet_id += 1
        return self.next_bullet_id

    @property
    def body_texture(self):
        if self._body_texture is None:
            self._body_texture = prm.get_pixmap(robot_texture_path + "tank_red_body")
            if self.is_player:
                self._body_texture = prm.get_pixmap(robot_texture_path + "tank_blue_body")
        return self._body_texture

    @property
    def turret_texture(self):
        if self._turret_texture is None:
            self._turret_texture = prm.get_pixmap(robot_texture_path + "tank_red_turret")
            if self.is_player:
                self._turret_texture = prm.get_pixmap(robot_texture_path + "tank_blue_turret")
        return self._turret_texture

    def draw(self, qp, delta_time):
        if self.is_dead:
            return

        self.extrapolation_body.step(delta_time)

        body_texture = self.body_texture
        turret_texture = self.turret_texture
        if self.input is None:
            turret_rot = 0
        else:
            turret_rot = self.input.turret_rot

        draw_img_with_rot(qp, body_texture, body_texture.width(), body_texture.height(),
                          self.extrapolation_body.position, self.extrapolation_body.rotation)

        turret_pos = self.extrapolation_body.position.copy()
        turret_offset = Robot.turret_texture_center_offset.copy()
        turret_offset.rotate(turret_rot)
        turret_pos.add(turret_offset)

        draw_img_with_rot(qp, turret_texture, turret_texture.width(), turret_texture.height(), turret_pos, turret_rot)

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
        if self.is_dead:
            if self.world_sim.physics_frame_count >= self.last_death_frame + RESPAWN_DELAY:
                self.respawn()
            else:
                return

        if int(self.health) <= 0:
            self.health = 0
            self.die()
            return
        elif self.health > self.max_health:
            self.health = self.max_health

        self.revert_effects()

        tile_position = self.sim_body.position.copy()
        tile_position.div(GameInfo.arena_tile_size)
        tile_position.floor()
        power_up = self.world_sim.arena.power_ups.get((tile_position.x, tile_position.y))
        if power_up is not None:
            power_up.apply(self)

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
                    if self.input is None:
                        turret_rot = 0
                    else:
                        turret_rot = self.input.turret_rot
                    if not self.weapon.shoot(self, self.robot_id, self.get_next_bullet_id,
                                             self.sim_body.position, turret_rot, self.damage_factor):
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

    def create_physics_body(self):
        if self.physics_body is None:
            self.physics_body = self.physics_world.add_rect(self.sim_body.position, self.size.x, self.size.y,
                                                            rotation=self.sim_body.rotation, static=False,
                                                            user_data=self)

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
        self.collider_push = self.sim_body.position.copy()

    def refresh_from_physics(self):
        if self.physics_body is not None:
            new_pos = Vector(self.physics_body.position[0], self.physics_body.position[1])
            self.collider_push = self.collider_push.diff(new_pos)
            self.sim_body.position = new_pos

            push_vel = self.collider_push.copy()
            push_vel.mult(FIXED_DELTA_TIME)
            self.real_velocity.add(push_vel)

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

    def change_health(self, delta_health):
        self.health += delta_health

    def hit_bullet(self, damage, source_robot):
        self.change_health(-damage / self.bullet_resistance_factor)
        if int(self.health) <= 0 and source_robot is not self:
            if source_robot is not None:
                source_robot.kills += 1

    def die(self):
        if self is self.world_sim.local_player_robot:
            GameInfo.local_player_score += self.kills * GameInfo.score_per_kill

        explosion_path = "vfx/"
        if self.is_player:
            explosion_path += "tank_blue_explosion"
        else:
            explosion_path += "tank_red_explosion"
        Animation(explosion_path, self.sim_body.position, rotation=self.sim_body.rotation)
        self.is_dead = True
        self.last_death_frame = self.world_sim.physics_frame_count
        if self.should_respawn:
            self.physics_world.world.DestroyBody(self.physics_body)
            self.physics_body = None
        else:
            self.remove()

    def respawn(self):
        self.create_physics_body()
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
        last_pos_change = self.real_velocity.copy()
        last_pos_change.mult(FIXED_DELTA_TIME)
        self.last_position.sub(last_pos_change)
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
        self.turret_rot = 0

    def copy(self):
        player_input = PlayerInput()
        player_input.up = self.up
        player_input.down = self.down
        player_input.left = self.left
        player_input.right = self.right
        player_input.shoot = self.shoot
        player_input.shoot_pressed = self.shoot_pressed
        player_input.turret_rot = self.turret_rot
        return player_input

    def to_string(self):
        return ("PlayerInput {\n  Up: " + str(self.up) + "\n  Down: " + str(self.down) + "\n  Left: "
                + str(self.left) + "\n  Right: " + str(self.right) + "\n  Shoot: " + str(self.shoot)
                + "\n  Shoot Pressed: " + str(self.shoot_pressed) + "\n Turret rotation: "
                + str(round(self.turret_rot, 2)) + "\n}")


def collide_robot(robot, other):

    normal = robot.collider_push.copy()
    pos = robot.sim_body.position.copy()

    if isinstance(other, Robot):
        normal = robot.collider_push.diff(other.collider_push)
        velocity = robot.real_velocity.diff(other.real_velocity)
        if normal.equal(Vector(0, 0)) or velocity.equal(Vector(0, 0)):
            return
        angle = velocity.angle(normal)
        mag = velocity.magnitude() * math.cos(angle)
        if (robot.world_sim.physics_frame_count > robot.last_collision_sound_frame + MIN_SOUND_DELAY_FRAMES
                and abs(mag) > robot.max_velocity * ROBOT_COLLISION_SOUND_SPEED_FACTOR):
            robot.last_collision_sound_frame = robot.world_sim.physics_frame_count
            SoundManager.instance.play_sfx("collision_tank_tank", pos=pos)
    elif isinstance(other, TileType) and other.has_collision:
        if normal.equal(Vector(0, 0) or robot.real_velocity.equal(Vector(0, 0))):
            return
        angle = robot.real_velocity.angle(normal)
        mag = robot.real_velocity.magnitude() * math.cos(angle)
        if (robot.world_sim.physics_frame_count > robot.last_collision_sound_frame + MIN_SOUND_DELAY_FRAMES
                and abs(mag) > robot.max_velocity * ROBOT_COLLISION_SOUND_SPEED_FACTOR):
            robot.last_collision_sound_frame = robot.world_sim.physics_frame_count
            SoundManager.instance.play_sfx("collision_tank_wall", pos=pos)
