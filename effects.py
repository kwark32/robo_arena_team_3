# imports


class RobotEffect:
    def __init__(self, duration):
        self.duration = duration

    def apply_effect(self, robot, delta_time=0):
        self.duration -= delta_time


class EarthTileEffect(RobotEffect):
    slow_down = 30

    def __init__(self, duration=0):
        super().__init__(duration)

    def apply_effect(self, robot, delta_time=0):
        super().apply_effect(robot)

        robot.sim_body.max_velocity -= EarthTileEffect.slow_down
