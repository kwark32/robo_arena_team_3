import time

from robot import Robot
from json_interface import load_map
from physics import PhysicsWorld
from util import Vector, get_main_path, get_delta_time_s, ns_to_s
from constants import ARENA_SIZE, FIXED_DELTA_TIME, FIXED_DELTA_TIME_NS, MAX_FIXED_TIMESTEPS


class WorldSim:
    def __init__(self):
        self.robot_class = Robot

        self.physics_world = PhysicsWorld()
        self.arena = None
        self.robots = []
        self.bullets = []
        self.player_input = None

        self.init_arena(ARENA_SIZE)

        self.physics_world_time_ns = 0
        self.world_start_time_ns = time.time_ns()
        self.curr_world_time_ns = 0
        self.delta_time = 0
        self.extrapolation_delta_time = 0

        self._frames_since_last_show = 0
        self._last_fps_show_time = self.world_start_time_ns
        self.fps = 0

    def clean_mem(self):
        pass

    def init_arena(self, size):
        map_path = get_main_path() + "/test_map.json"
        self.arena = load_map(map_path, size, physics_world=self.physics_world)

    def init_player(self, position=Vector(500, 500)):
        player = Robot(is_player=True, has_ai=False, position=Vector(500, 500), world_sim=self)
        self.robots.append(player)
        return player

    def init_ai_robots(self):
        self.robots.append(Robot(position=Vector(250, 250), world_sim=self))
        self.robots.append(Robot(position=Vector(250, 750), world_sim=self))
        self.robots.append(Robot(position=Vector(750, 250), world_sim=self))
        self.robots.append(Robot(position=Vector(750, 750), world_sim=self))

    def fixed_update(self, delta_time, curr_world_time):
        dead_bullets = []
        for bullet in self.bullets:
            if bullet.to_destroy:
                dead_bullets.append(bullet)
        for dead in dead_bullets:
            dead.physics_world.world.DestroyBody(dead.physics_body)
            self.bullets.remove(dead)
        dead_bullets.clear()

        for bullet in self.bullets:
            bullet.update(delta_time)

        dead_robots = []
        for robot in self.robots:
            if robot.is_dead:
                dead_robots.append(robot)
        for dead in dead_robots:
            dead.die()
            self.robots.remove(dead)
        dead_robots.clear()

        for robot in self.robots:
            robot.update(delta_time, curr_world_time)

        self.physics_world.world.Step(delta_time, 0, 4)

        for robot in self.robots:
            robot.refresh_from_physics()

    def update_world(self):
        last_world_time_ns = self.curr_world_time_ns
        curr_time_ns = time.time_ns()
        self.curr_world_time_ns = curr_time_ns - self.world_start_time_ns
        self.delta_time = get_delta_time_s(self.curr_world_time_ns, last_world_time_ns)
        self.extrapolation_delta_time = self.delta_time

        for i in range(MAX_FIXED_TIMESTEPS):
            last_fixed_timestep_delta_time_ns = self.curr_world_time_ns - self.physics_world_time_ns
            if last_fixed_timestep_delta_time_ns < FIXED_DELTA_TIME_NS:
                break
            self.fixed_update(FIXED_DELTA_TIME, ns_to_s(self.physics_world_time_ns))
            self.physics_world_time_ns += FIXED_DELTA_TIME_NS
            self.extrapolation_delta_time = 0

        self._frames_since_last_show += 1
        last_fps_show_delta = get_delta_time_s(curr_time_ns, self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = curr_time_ns


class SPWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.player = self.init_player()
        self.player_input = self.player.input
        self.init_ai_robots()


class OnlineWorldSim(WorldSim):
    def __init__(self):
        super().__init__()


class ServerWorldSim(WorldSim):
    def __init__(self):
        super().__init__()
