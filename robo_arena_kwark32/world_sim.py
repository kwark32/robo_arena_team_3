import time
import random

from robot import Robot, PlayerInput
from arena_converter import load_map
from physics import PhysicsWorld
from util import Vector, get_delta_time_s
from globals import GameInfo, Settings
from constants import FIXED_DELTA_TIME, FIXED_DELTA_TIME_NS, MAX_FIXED_TIMESTEPS, FIXED_FPS, GAME_OVER_DELAY
from constants import FRAMES_PER_POWER_UP
from camera import CameraState
from sound_manager import SoundManager


class WorldSim:
    """Base class for all mode-specific game simulations."""
    def __init__(self):
        self.robot_class = Robot

        self.world_scene = None

        self.physics_world = PhysicsWorld()
        self.arena = None
        self.robots = []
        self.local_player_robot = None
        self.bullets = []
        self.player_input = PlayerInput()

        self.init_arena()

        self.physics_frame_count = 0

        self.curr_time_ns = time.time_ns()
        self.physics_world_time_ns = 0
        self.world_start_time_ns = self.curr_time_ns
        self.curr_world_time_ns = 0
        self.delta_time = 0
        self.extrapolation_delta_time = 0
        self.catchup_frame = False

        self._frames_since_last_show = 0
        self._last_fps_show_time = self.world_start_time_ns
        self.fps = 0
        self.frame_times_since_ms = 0
        self.frame_time_ms = 0

        self.did_fixed_update = False

    def clean_mem(self):
        CameraState.position = None

    def init_arena(self):
        self.arena = load_map(GameInfo.active_arena, physics_world=self.physics_world)
        self.arena.world_sim = self

    def create_player(self, robot_id=-1, position=None, player_name=None, should_respawn=False):
        if player_name is None:
            player_name = GameInfo.local_player_name
        if position is None:
            position = Vector(self.arena.size.x / 2, self.arena.size.y / 2)
        player = Robot(self, robot_id=robot_id, is_player=True, has_ai=False, should_respawn=should_respawn,
                       position=position, player_name=player_name)
        self.robots.append(player)
        return player

    def create_enemy_robot(self, robot_id=-1, position=None, has_ai=True, player_name="", should_respawn=False):
        if position is None:
            position = Vector(self.arena.size.x / 2, self.arena.size.y / 2)
        enemy = Robot(self, robot_id=robot_id, has_ai=has_ai, position=position,
                      player_name=player_name, should_respawn=should_respawn)
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
            if dead is self.local_player_robot:
                self.local_player_robot = None
        dead_robots.clear()

    def fixed_update(self, delta_time, catchup_frame=False):
        """Update all bullets, robots etc with a fixed delta time."""
        self.did_fixed_update = True

        self.catchup_frame = catchup_frame
        SoundManager.instance.catchup_frame = catchup_frame

        random.seed(GameInfo.current_frame_seed)

        if self.physics_frame_count % FRAMES_PER_POWER_UP == 0:
            self.arena.place_power_up(delta_time)

        for bullet in self.bullets:
            bullet.update(delta_time)

        for robot in self.robots:
            robot.update(delta_time)

        self.physics_world.world.Step(delta_time, 0, 4)

        for robot in self.robots:
            robot.refresh_from_physics()

        self.physics_world.do_collisions()

        if not catchup_frame:
            pos = CameraState.position
            if self.local_player_robot is not None:
                pos = self.local_player_robot.sim_body.position
            if pos is not None:
                pos = pos.copy()
            SoundManager.instance.update_sound(pos)

            if self.world_scene is not None and self.world_scene.score_board is not None:
                self.world_scene.score_board.set_scores(self.robots)

        self.clear_dead_bullets()
        self.clear_dead_robots()

        self.physics_frame_count += 1
        self.physics_world_time_ns = FIXED_DELTA_TIME_NS * self.physics_frame_count

        SoundManager.instance.catchup_frame = False
        self.catchup_frame = False

    def update_times(self):
        """Calculate current frame times."""
        last_world_time_ns = self.curr_world_time_ns
        self.curr_time_ns = time.time_ns()
        self.curr_world_time_ns = self.curr_time_ns - self.world_start_time_ns
        self.delta_time = get_delta_time_s(self.curr_world_time_ns, last_world_time_ns)
        self.extrapolation_delta_time = self.delta_time

    def calc_fps(self):
        self._frames_since_last_show += 1
        last_fps_show_delta = get_delta_time_s(self.curr_time_ns, self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.frame_time_ms = round(self.frame_times_since_ms / self._frames_since_last_show, 2)
            self.frame_times_since_ms = 0

            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = self.curr_time_ns

    def update_world(self):
        """Updates the world, only calling fixed_update when it is due."""
        self.did_fixed_update = False

        self.update_times()

        iterations = 0
        for i in range(MAX_FIXED_TIMESTEPS):
            last_fixed_timestep_delta_time_ns = self.curr_world_time_ns - self.physics_world_time_ns
            if last_fixed_timestep_delta_time_ns < FIXED_DELTA_TIME_NS:
                break
            # print("last fixed delta ms: " + str(round(last_fixed_timestep_delta_time_ns / 1000000)))
            iterations += 1
            self.fixed_update(FIXED_DELTA_TIME)
            self.extrapolation_delta_time = get_delta_time_s(self.curr_world_time_ns,
                                                             self.physics_frame_count * FIXED_DELTA_TIME_NS)
        # print("iterations: " + str(iterations))

        if self.local_player_robot is not None:
            if CameraState.position is None:
                CameraState.position = self.local_player_robot.extrapolation_body.position.copy()
            else:
                CameraState.position.lerp_to(self.local_player_robot.extrapolation_body.position,
                                             CameraState.lerp_per_sec * self.delta_time)

        self.calc_fps()

    def set_seed(self):
        """Sets the random seed for the current frame, to be in sync with the server (deterministic)"""
        GameInfo.current_frame_seed = self.world_start_time_ns + self.physics_frame_count


class SPWorldSim(WorldSim):
    """Game simulation for singleplayer."""
    def __init__(self):
        super().__init__()

        self.local_player_robot = self.create_player(player_name="")
        self.local_player_robot.input = self.player_input

        GameInfo.local_player_score = 0
        GameInfo.local_player_score_is_highscore = False

        self.player_die_frame = None

        self.last_enemy_spawn_frame = 0
        self.enemy_spawn_delay = 20 * FIXED_FPS

        self.spawn_random_enemy()

        # self.create_enemy_robot(position=Vector(self.arena.size.x / 2 - 800, self.arena.size.y / 2 - 800))
        # self.create_enemy_robot(position=Vector(self.arena.size.x / 2 + 800, self.arena.size.y / 2 - 800))
        # self.create_enemy_robot(position=Vector(self.arena.size.x / 2 - 800, self.arena.size.y / 2 + 800))
        # self.create_enemy_robot(position=Vector(self.arena.size.x / 2 + 800, self.arena.size.y / 2 + 800))

    def fixed_update(self, delta_time, catchup_frame=False):
        """Fixed update additions for singleplayer."""
        self.set_seed()

        if self.physics_frame_count > self.last_enemy_spawn_frame + self.enemy_spawn_delay:
            self.spawn_random_enemy()
            self.last_enemy_spawn_frame = self.physics_frame_count
        self.enemy_spawn_delay -= 0.00008 * self.enemy_spawn_delay

        super().fixed_update(delta_time)

        if self.local_player_robot is None and self.player_die_frame is None:
            self.player_die_frame = self.physics_frame_count
            GameInfo.local_player_score += self.player_die_frame
            if GameInfo.local_player_score > Settings.instance.highscore:
                GameInfo.local_player_score_is_highscore = True
                Settings.instance.highscore = GameInfo.local_player_score
                Settings.instance.save()

        if (self.player_die_frame is not None and self.world_scene.active_menu is None
                and self.physics_frame_count > self.player_die_frame + GAME_OVER_DELAY):
            self.world_scene.switch_menu("game_over_menu")

    def spawn_random_enemy(self):
        if self.arena.tiles is None:
            return

        pos = None
        while pos is None:
            pos = Vector(random.randrange(self.arena.tile_count.x), random.randrange(self.arena.tile_count.y))
            tile = self.arena.tiles[pos.y][pos.x]
            if tile.has_collision or tile.name == "hole" or tile.name == "lava" or tile.name.startswith("portal_"):
                pos = None
                continue
            pos.mult(GameInfo.arena_tile_size)
            pos.add_scalar(GameInfo.arena_tile_size / 2)
            pos.round()

        self.create_enemy_robot(position=pos)
