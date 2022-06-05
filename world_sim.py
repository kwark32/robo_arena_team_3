import time

from robot import Robot
from json_interface import load_map
from physics import PhysicsWorld
from combat import Bullets
from util import Vector, get_main_path, ns_to_s
from constants import ARENA_SIZE


class WorldSim:
    def __init__(self):
        Bullets.robot_class = Robot

        self.physics_world = PhysicsWorld()
        self.arena = None
        self.robots = []
        self.player_input = None

        self.init_arena(ARENA_SIZE)
        self.init_robots()

        self.world_start_time_ns = time.time_ns()

        self._last_frame_time_ns = time.time_ns()
        self._frames_since_last_show = 0
        self._last_fps_show_time = time.time_ns()
        self.fps = 0

    def clean_mem(self):
        Bullets.bullet_list.clear()

    def init_arena(self, size):
        map_path = get_main_path() + "/test_map.json"
        self.arena = load_map(map_path, size, physics_world=self.physics_world)

    def init_robots(self):
        self.robots.append(Robot(is_player=True, position=Vector(500, 500), physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(250, 250), physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(250, 750), physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(750, 250), physics_world=self.physics_world))
        self.robots.append(Robot(is_player=False, position=Vector(750, 750), physics_world=self.physics_world))

        for robot in self.robots:
            if robot.is_player:
                self.player_input = robot.input
                break

    def update_world(self):
        curr_time_ns = time.time_ns()
        delta_time = ns_to_s(curr_time_ns - self._last_frame_time_ns)
        curr_world_time = ns_to_s(curr_time_ns - self.world_start_time_ns)
        self._last_frame_time_ns = curr_time_ns

        self._frames_since_last_show += 1
        last_fps_show_delta = ns_to_s(curr_time_ns - self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = curr_time_ns

        dead_bullets = []
        for bullet in Bullets.bullet_list:
            if bullet.to_destroy:
                dead_bullets.append(bullet)
        for dead in dead_bullets:
            dead.physics_world.world.DestroyBody(dead.physics_body)
            Bullets.bullet_list.remove(dead)
        dead_bullets.clear()

        for bullet in Bullets.bullet_list:
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

        # maybe delta_time instead of 0.016 (~1/60th s)
        self.physics_world.world.Step(0.016, 0, 4)

        for robot in self.robots:
            robot.refresh_from_physics()
