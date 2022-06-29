import time

from robot import Robot, PlayerInput
from json_interface import load_map
from physics import PhysicsWorld
from util import Vector, get_main_path, get_delta_time_s
from globals import GameInfo
from constants import ARENA_SIZE, FIXED_DELTA_TIME, FIXED_DELTA_TIME_NS, MAX_FIXED_TIMESTEPS


class WorldSim:
    def __init__(self):
        self.robot_class = Robot

        self.player_id = -1

        self.physics_world = PhysicsWorld()
        self.arena = None
        self.robots = []
        self.bullets = []
        self.player_input = PlayerInput()

        self.init_arena(ARENA_SIZE)

        self.physics_frame_count = 0

        self.curr_time_ns = time.time_ns()
        self.physics_world_time_ns = 0
        self.world_start_time_ns = self.curr_time_ns
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

    def create_player(self, robot_id=-1, position=Vector(ARENA_SIZE / 2, ARENA_SIZE / 2)):
        player = Robot(self, robot_id=robot_id, is_player=True, has_ai=False,
                       position=position, player_name=GameInfo.local_player_name)
        self.robots.append(player)
        return player

    def create_enemy_robot(self, robot_id=-1, position=Vector(ARENA_SIZE / 2, ARENA_SIZE / 2), has_ai=True):
        enemy = Robot(self, robot_id=robot_id, has_ai=has_ai, position=position)
        self.robots.append(enemy)
        return enemy

    def clear_dead_bullets(self):
        dead_bullets = []
        for bullet in self.bullets:
            if bullet.to_destroy:
                dead_bullets.append(bullet)
        for dead in dead_bullets:
            dead.physics_world.world.DestroyBody(dead.physics_body)
            self.bullets.remove(dead)
        dead_bullets.clear()

    def clear_dead_robots(self):
        dead_robots = []
        for robot in self.robots:
            if robot.to_remove:
                dead_robots.append(robot)
        for dead in dead_robots:
            self.robots.remove(dead)
        dead_robots.clear()

    def fixed_update(self, delta_time):
        for bullet in self.bullets:
            bullet.update(delta_time)

        for robot in self.robots:
            robot.update(delta_time)

        self.physics_world.world.Step(delta_time, 0, 4)

        for robot in self.robots:
            robot.refresh_from_physics()

        self.clear_dead_bullets()
        self.clear_dead_robots()

        self.physics_frame_count += 1
        self.physics_world_time_ns = FIXED_DELTA_TIME_NS * self.physics_frame_count

    def update_times(self):
        last_world_time_ns = self.curr_world_time_ns
        self.curr_time_ns = time.time_ns()
        self.curr_world_time_ns = self.curr_time_ns - self.world_start_time_ns
        self.delta_time = get_delta_time_s(self.curr_world_time_ns, last_world_time_ns)
        self.extrapolation_delta_time = self.delta_time

    def calc_fps(self):
        self._frames_since_last_show += 1
        last_fps_show_delta = get_delta_time_s(self.curr_time_ns, self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = self.curr_time_ns

    def update_world(self):
        self.update_times()

        for i in range(MAX_FIXED_TIMESTEPS):
            last_fixed_timestep_delta_time_ns = self.curr_world_time_ns - self.physics_world_time_ns
            if last_fixed_timestep_delta_time_ns < FIXED_DELTA_TIME_NS:
                break
            self.fixed_update(FIXED_DELTA_TIME)
            self.extrapolation_delta_time = get_delta_time_s(self.curr_world_time_ns,
                                                             self.physics_frame_count * FIXED_DELTA_TIME_NS)

        self.calc_fps()


class SPWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.player = self.create_player()
        self.player.input = self.player_input
        self.create_enemy_robot(position=Vector(250, 250))
        self.create_enemy_robot(position=Vector(250, 750))
        self.create_enemy_robot(position=Vector(750, 250))
        self.create_enemy_robot(position=Vector(750, 750))
