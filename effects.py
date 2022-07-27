import random

from constants import FIXED_DELTA_TIME
from globals import GameInfo


class RobotEffect:
    id = 0

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

    def get_data_list(self, sub_list=None):
        if sub_list is None:
            sub_list = []

        sub_list.append(self.effect_class.id)
        sub_list.append(self.duration)

        return sub_list

    def set_from_data_list(self, data_list):
        pass


class SpeedEffect(RobotEffect):
    id = 1
    speed_gain = 0
    ang_speed_gain = 0

    def __init__(self, duration, speed_gain=None, ang_speed_gain=None):
        super().__init__(duration)

        self.speed_gain = speed_gain
        self.ang_speed_gain = ang_speed_gain

        if self.speed_gain is None:
            self.speed_gain = self.effect_class.speed_gain
        if self.ang_speed_gain is None:
            self.ang_speed_gain = self.effect_class.ang_speed_gain

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.sim_body.max_velocity += self.speed_gain
        robot.sim_body.max_ang_velocity += self.ang_speed_gain

    def revert(self, robot):
        robot.sim_body.max_velocity = robot.max_velocity
        robot.sim_body.max_ang_velocity = robot.max_ang_velocity

    def get_data_list(self, sub_list=None):
        sub_list = super().get_data_list(sub_list=sub_list)

        if sub_list is None:
            sub_list = []

        sub_list.append(self.speed_gain)
        sub_list.append(self.ang_speed_gain)

        return sub_list

    def set_from_data_list(self, data_list):
        if data_list is None or len(data_list) < 2:
            print("ERROR: Cannot set effect data from " + str(data_list))
            return None

        self.speed_gain = data_list.pop(0)
        self.ang_speed_gain = data_list.pop(0)


class StunEffect(SpeedEffect):
    id = 2
    speed_gain = -1000000
    ang_speed_gain = -1000000


class EarthTileEffect(SpeedEffect):
    id = 3
    speed_gain = -30
    ang_speed_gain = -1


class WaterTileEffect(SpeedEffect):
    id = 4
    speed_gain = -60
    ang_speed_gain = -2
    damage_per_second = 200

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        if robot.health < robot.max_health / 2:
            robot.change_health(-self.effect_class.damage_per_second * delta_time)


class FireTileEffect(SpeedEffect):
    id = 5
    speed_gain = 60
    ang_speed_gain = 2
    damage_per_second = 100

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.change_health(-self.effect_class.damage_per_second * delta_time)


class HoleTileEffect(StunEffect):
    id = 6
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
            robot.change_health(-1000)

    def revert(self, robot):
        super().revert(robot)
        if self.start_rotation is not None:
            robot.sim_body.rotation = self.start_rotation

    def copy(self):
        copy = super().copy()

        copy.start_rotation = self.start_rotation
        return copy

    def get_data_list(self, sub_list=None):
        sub_list = super().get_data_list(sub_list=sub_list)

        if sub_list is None:
            sub_list = []

        sub_list.append(self.start_rotation)

        return sub_list

    def set_from_data_list(self, data_list):
        if data_list is None or len(data_list) < 1:
            print("ERROR: Cannot set effect data from " + str(data_list))
            return None

        self.start_rotation = data_list.pop(0)


class LavaTileEffect(SpeedEffect):
    id = 7
    speed_gain = -90
    ang_speed_gain = -3
    damage_per_second = 400

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.change_health(-self.effect_class.damage_per_second * delta_time)


class Portal1TileEffect(RobotEffect):
    id = 8
    travel_damage_min = 50
    travel_damage_max = 150

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        apply_portal_effect(self.world_sim, robot, portal_type_1=True)


class Portal2TileEffect(RobotEffect):
    id = 9
    travel_damage_min = 50
    travel_damage_max = 150

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        apply_portal_effect(self.world_sim, robot, portal_type_1=False)


def apply_portal_effect(world_sim, robot, portal_type_1=True):
    if portal_type_1:
        travel_damage = random.randrange(Portal1TileEffect.travel_damage_min, Portal1TileEffect.travel_damage_max, 1)
    else:
        travel_damage = random.randrange(Portal2TileEffect.travel_damage_min, Portal2TileEffect.travel_damage_max, 1)

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
        pos.mult(GameInfo.arena_tile_size)
        pos.add_scalar(GameInfo.arena_tile_size / 2)
        robot.set_position(pos)

        robot.change_health(-travel_damage)

        robot.effect_data[("PortalTileEffect", "last_tp_type")] = portal_type

    robot.effect_data[("PortalTileEffect", "last_tp_frame")] = world_sim.physics_frame_count


class HealthEffect(RobotEffect):
    id = 10

    def __init__(self, duration=(FIXED_DELTA_TIME / 2), change_per_second=0, instant_change=0):
        super().__init__(duration)

        self.change_per_second = change_per_second
        self.instant_change = instant_change

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time)

        robot.change_health(self.instant_change)
        self.instant_change = 0
        robot.change_health(self.change_per_second * delta_time)

    def get_data_list(self, sub_list=None):
        sub_list = super().get_data_list(sub_list=sub_list)

        if sub_list is None:
            sub_list = []

        sub_list.append(self.change_per_second)
        sub_list.append(self.instant_change)

        return sub_list

    def set_from_data_list(self, data_list):
        if data_list is None or len(data_list) < 2:
            print("ERROR: Cannot set effect data from " + str(data_list))
            return None

        self.change_per_second = data_list.pop(0)
        self.instant_change = data_list.pop(0)


class DamageEffect(RobotEffect):
    id = 11

    def __init__(self, duration=(FIXED_DELTA_TIME / 2), damage_factor=1):
        super().__init__(duration)

        self.damage_factor = damage_factor

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time)

        robot.damage_factor *= self.damage_factor

    def revert(self, robot):
        robot.damage_factor = 1

    def get_data_list(self, sub_list=None):
        sub_list = super().get_data_list(sub_list=sub_list)

        if sub_list is None:
            sub_list = []

        sub_list.append(self.damage_factor)

        return sub_list

    def set_from_data_list(self, data_list):
        if data_list is None or len(data_list) < 1:
            print("ERROR: Cannot set effect data from " + str(data_list))
            return None

        self.damage_factor = data_list.pop(0)


class BulletResistanceEffect(RobotEffect):
    id = 12

    def __init__(self, duration=(FIXED_DELTA_TIME / 2), bullet_resistance_factor=1):
        super().__init__(duration)

        self.bullet_resistance_factor = bullet_resistance_factor

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time)

        robot.bullet_resistance_factor *= self.bullet_resistance_factor

    def revert(self, robot):
        robot.bullet_resistance_factor = 1

    def get_data_list(self, sub_list=None):
        sub_list = super().get_data_list(sub_list=sub_list)

        if sub_list is None:
            sub_list = []

        sub_list.append(self.bullet_resistance_factor)

        return sub_list

    def set_from_data_list(self, data_list):
        if data_list is None or len(data_list) < 1:
            print("ERROR: Cannot set effect data from " + str(data_list))
            return None

        self.bullet_resistance_factor = data_list.pop(0)


def get_effect_from_data_list(data_list, world_sim):
    if data_list is None or len(data_list) < 2:
        print("ERROR: Cannot set effect data from " + str(data_list))
        return None

    effect_class = effect_classes[data_list.pop(0)]
    duration = data_list.pop(0)

    effect = effect_class(duration)
    effect.world_sim = world_sim
    effect.set_from_data_list(data_list)

    return effect


effect_classes = {}
for name, obj in globals().copy().items():
    if name.endswith("Effect") and hasattr(obj, "id"):
        effect_classes[obj.id] = obj
