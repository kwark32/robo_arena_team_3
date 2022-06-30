from constants import FIXED_DELTA_TIME


class RobotEffect:
    def __init__(self, duration):
        self.effect_class = type(self)
        self.duration = duration

    def apply(self, robot, delta_time=0):
        self.duration -= delta_time

    def revert(self, robot):
        pass


class SpeedEffect(RobotEffect):
    speed_gain = 0
    ang_speed_gain = 0

    def __init__(self, duration=(FIXED_DELTA_TIME / 2)):  # duration: half physics frame (gets applied 1 frame)
        super().__init__(duration)

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

    def __init__(self, duration=(FIXED_DELTA_TIME / 2)):  # duration: half physics frame (gets applied 1 frame)
        super().__init__(duration=duration)

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        if robot.health < robot.max_health / 2:
            robot.take_damage(self.effect_class.damage_per_second * delta_time)


class FireTileEffect(SpeedEffect):
    speed_gain = 60
    ang_speed_gain = 2
    damage_per_second = 100

    def __init__(self, duration=(FIXED_DELTA_TIME / 2)):  # duration: half physics frame (gets applied 1 frame)
        super().__init__(duration=duration)

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.take_damage(self.effect_class.damage_per_second * delta_time)


class HoleTileEffect(StunEffect):
    rotation = 8

    def __init__(self, duration=4):
        super().__init__(duration=duration)

        self.start_rotation = None

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        if self.start_rotation is None:
            self.start_rotation = robot.sim_body.rotation

        robot.sim_body.rotation += self.effect_class.rotation * delta_time * delta_time

        if self.duration <= 0:
            robot.take_damage(1000)

    def revert(self, robot):
        if self.start_rotation is not None:
            robot.sim_body.rotation = self.start_rotation


class LavaTileEffect(SpeedEffect):
    speed_gain = -90
    ang_speed_gain = -3
    damage_per_second = 400

    def __init__(self, duration=(FIXED_DELTA_TIME / 2)):  # duration: half physics frame (gets applied 1 frame)
        super().__init__(duration=duration)

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.take_damage(self.effect_class.damage_per_second * delta_time)
