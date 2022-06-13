from constants import FIXED_DELTA_TIME


class RobotEffect:
    def __init__(self, duration):
        self.duration = duration

    def apply(self, robot, delta_time=0):
        self.duration -= delta_time

    def revert(self, robot):
        pass


class EarthTileEffect(RobotEffect):
    slow_down = 30

    def __init__(self, duration=0):
        super().__init__(duration)

    def apply(self, robot, delta_time=(FIXED_DELTA_TIME / 2)):
        super().apply(robot)

        robot.sim_body.max_velocity -= EarthTileEffect.slow_down

    def revert(self, robot):
        robot.sim_body.max_velocity = robot.max_velocity
