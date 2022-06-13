from constants import FIXED_DELTA_TIME


class RobotEffect:
    def __init__(self, duration):
        self.duration = duration

    def apply(self, robot, delta_time=0):
        self.duration -= delta_time

    def revert(self, robot):
        pass


class EarthTileEffect(RobotEffect):
    slowdown = 60
    ang_slowdown = 2

    def __init__(self, duration=(FIXED_DELTA_TIME / 2)):
        super().__init__(duration)

    def apply(self, robot, delta_time=0):
        super().apply(robot, delta_time=delta_time)

        robot.sim_body.max_velocity -= EarthTileEffect.slowdown
        robot.sim_body.max_ang_velocity -= EarthTileEffect.ang_slowdown

    def revert(self, robot):
        robot.sim_body.max_velocity = robot.max_velocity
        robot.sim_body.max_ang_velocity = robot.max_ang_velocity

