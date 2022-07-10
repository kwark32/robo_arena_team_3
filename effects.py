from constants import FIXED_DELTA_TIME
import random


class RobotEffect:
    def __init__(self, duration):
        self.effect_class = type(self)
        self.duration = duration
        self.world_sim = None

    def apply(self, robot, delta_time=0):
        self.duration -= delta_time

    def revert(self, robot):
        pass

    def get_effect_info(self):
        copy = self.copy()
        copy.world_sim = None
        return copy

    def copy(self):
        return self.effect_class(self.duration)


class SpeedEffect(RobotEffect):
    speed_gain = 0
    ang_speed_gain = 0

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.sim_body.max_velocity += self.effect_class.speed_gain
        robot.sim_body.max_ang_velocity += self.effect_class.ang_speed_gain

    def revert(self, robot):
        robot.sim_body.max_velocity = robot.max_velocity
        robot.sim_body.max_ang_velocity = robot.max_ang_velocity


class StunEffect(SpeedEffect):
    speed_gain = -1000000
    ang_speed_gain = -1000000


class EarthTileEffect(SpeedEffect):
    speed_gain = -30
    ang_speed_gain = -1


class WaterTileEffect(SpeedEffect):
    speed_gain = -60
    ang_speed_gain = -2
    damage_per_second = 200

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        if robot.health < robot.max_health / 2:
            robot.take_damage(self.effect_class.damage_per_second * delta_time)


class FireTileEffect(SpeedEffect):
    speed_gain = 60
    ang_speed_gain = 2
    damage_per_second = 100

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.take_damage(self.effect_class.damage_per_second * delta_time)


class HoleTileEffect(StunEffect):
    rotation = 8

    def __init__(self, duration):
        super().__init__(4)

        self.start_rotation = None

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        if self.start_rotation is None:
            self.start_rotation = robot.sim_body.rotation

        robot.sim_body.rotation += self.effect_class.rotation * delta_time * delta_time

        if self.duration <= 0:
            robot.take_damage(1000)

    def revert(self, robot):
        super().revert(robot)
        if self.start_rotation is not None:
            robot.sim_body.rotation = self.start_rotation

    def copy(self):
        copy = super().copy()

        copy.start_rotation = self.start_rotation
        return copy


class LavaTileEffect(SpeedEffect):
    speed_gain = -90
    ang_speed_gain = -3
    damage_per_second = 400

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.take_damage(self.effect_class.damage_per_second * delta_time)


class Portal1TileEffect(RobotEffect):
    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        apply_portal_effect(self.world_sim, robot, portal_type_1=True)


class Portal2TileEffect(RobotEffect):
    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        apply_portal_effect(self.world_sim, robot, portal_type_1=False)


def apply_portal_effect(world_sim, robot, portal_type_1=True):
    portal_type = 2
    if portal_type_1:
        portal_type = 1

    last_tp_frame = robot.effect_data.get(("PortalTileEffect", "last_tp_frame"))
    if last_tp_frame is None:
        last_tp_frame = -0
    last_tp_type = robot.effect_data.get(("PortalTileEffect", "last_tp_type"))
    if last_tp_type is None:
        last_tp_type = not portal_type_1

    if world_sim.physics_frame_count > last_tp_frame + 1 or portal_type == last_tp_type:
        if portal_type_1:
            portals = world_sim.arena.portal_2_tiles
        else:
            portals = world_sim.arena.portal_1_tiles
        portal = random.choice(portals)
        pos = portal.copy()
        pos.mult(world_sim.arena.tile_size)
        pos.add_scalar(world_sim.arena.tile_size / 2)
        robot.set_position(pos)

        robot.effect_data[("PortalTileEffect", "last_tp_type")] = portal_type

    robot.effect_data[("PortalTileEffect", "last_tp_frame")] = world_sim.physics_frame_count
