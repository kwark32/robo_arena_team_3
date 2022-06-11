import time

from robot import Robot, PlayerInput, set_robot_values
from weapons import set_bullet_values
from json_interface import load_map
from physics import PhysicsWorld
from util import Vector, get_main_path, get_delta_time_s, limit
from networking import UDPClient, UDPServer, RobotInfo, BulletInfo, ClientPacket, StatePacket
from constants import ARENA_SIZE, FIXED_DELTA_TIME, FIXED_DELTA_TIME_NS, MAX_FIXED_TIMESTEPS
from constants import CLIENT_DISCONNECT_TIMEOUT_NS, MAX_EXTRAPOLATION_STEPS


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
        player = Robot(self, robot_id=robot_id, is_player=True, has_ai=False, position=position)
        self.robots.append(player)
        return player

    def create_enemy_robot(self, robot_id=-1, position=Vector(ARENA_SIZE / 2, ARENA_SIZE / 2), has_ai=True):
        enemy = Robot(self, robot_id=robot_id, has_ai=has_ai, position=position)
        self.robots.append(enemy)
        return enemy

    def fixed_update(self, delta_time):
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
            if robot.to_remove:
                dead_robots.append(robot)
        for dead in dead_robots:
            dead.die()
            self.robots.remove(dead)
        dead_robots.clear()

        for robot in self.robots:
            robot.update(delta_time)

        self.physics_world.world.Step(delta_time, 0, 4)

        for robot in self.robots:
            robot.refresh_from_physics()

        self.physics_frame_count += 1
        self.physics_world_time_ns = FIXED_DELTA_TIME_NS * self.physics_frame_count

    def update_world(self):
        last_world_time_ns = self.curr_world_time_ns
        self.curr_time_ns = time.time_ns()
        self.curr_world_time_ns = self.curr_time_ns - self.world_start_time_ns
        self.delta_time = get_delta_time_s(self.curr_world_time_ns, last_world_time_ns)
        self.extrapolation_delta_time = self.delta_time

        for i in range(MAX_FIXED_TIMESTEPS):
            last_fixed_timestep_delta_time_ns = self.curr_world_time_ns - self.physics_world_time_ns
            if last_fixed_timestep_delta_time_ns < FIXED_DELTA_TIME_NS:
                break
            self.fixed_update(FIXED_DELTA_TIME)
            self.extrapolation_delta_time = get_delta_time_s(self.curr_world_time_ns,
                                                             self.physics_frame_count * FIXED_DELTA_TIME_NS)

        self._frames_since_last_show += 1
        last_fps_show_delta = get_delta_time_s(self.curr_time_ns, self._last_fps_show_time)
        if last_fps_show_delta > 0.5:
            self.fps = self._frames_since_last_show / last_fps_show_delta
            self._frames_since_last_show = 0
            self._last_fps_show_time = self.curr_time_ns


class SPWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.player = self.create_player()
        self.player.input = self.player_input
        self.create_enemy_robot(position=Vector(250, 250))
        self.create_enemy_robot(position=Vector(250, 750))
        self.create_enemy_robot(position=Vector(750, 250))
        self.create_enemy_robot(position=Vector(750, 750))


class OnlineWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.local_player_robot = None
        self.previous_inputs = []
        self.udp_socket = UDPClient()
        self.last_packet_physics_frame = 0

        self.received_first_packet = False

    def fixed_update(self, delta_time):
        self.previous_inputs.append((self.player_input.copy(), self.physics_frame_count))

        if self.player_id == -1 or self.player_input is None:
            self.udp_socket.send_packet(None, ClientPacket(creation_time=self.curr_time_ns))
        else:
            packet = ClientPacket(creation_time=self.curr_time_ns, player_input=self.player_input)
            self.udp_socket.send_packet(None, packet)

        new_packets = []
        while self.udp_socket.get_packet_available():
            new_packets.append(self.udp_socket.get_packet())

        if new_packets:
            last_packet = new_packets[0]
            for p in new_packets:
                if p.physics_frame >= last_packet.physics_frame:
                    last_packet = p

            if last_packet.physics_frame < self.last_packet_physics_frame:
                super().fixed_update(delta_time)
                return

            self.world_start_time_ns = last_packet.world_start_time
            self.curr_world_time_ns = self.curr_time_ns - self.world_start_time_ns
            delta_packet_physics_frames = last_packet.physics_frame - self.last_packet_physics_frame
            self.last_packet_physics_frame = last_packet.physics_frame
            self.physics_frame_count = self.last_packet_physics_frame
            self.physics_world_time_ns = self.physics_frame_count * FIXED_DELTA_TIME_NS

            # Set all variables from last packet
            self.player_id = last_packet.player_id

            # Set robots
            for new_robot_info in last_packet.robots:
                existing_robot = None
                for robot in self.robots:
                    if robot.robot_id == new_robot_info.player_id:
                        existing_robot = robot
                        break

                if existing_robot is None:
                    if self.player_id == new_robot_info.player_id:
                        self.local_player_robot = self.create_player(robot_id=self.player_id)
                        self.local_player_robot.input = self.player_input
                        existing_robot = self.local_player_robot
                    else:
                        existing_robot = self.create_enemy_robot(robot_id=new_robot_info.player_id, has_ai=False)

                set_robot_values(existing_robot, new_robot_info)

            if len(self.robots) > len(last_packet.robots):
                dead_robots = []
                for robot in self.robots:
                    contained = False
                    for new_robot_info in last_packet.robots:
                        if robot.robot_id == new_robot_info.player_id:
                            contained = True
                            break
                    if not contained:
                        dead_robots.append(robot)
                for dead in dead_robots:
                    dead.remove()
                    self.robots.remove(dead)
                dead_robots.clear()

            # Set bullets
            for new_bullet_info in last_packet.bullets:
                existing_bullet = None
                for bullet in self.bullets:
                    if bullet.bullet_id == new_bullet_info.bullet_id:
                        existing_bullet = bullet
                        break

                if existing_bullet is None:
                    existing_bullet = new_bullet_info.bullet_class(self)

                set_bullet_values(existing_bullet, new_bullet_info)

            if len(self.bullets) > len(last_packet.bullets):
                dead_bullets = []
                for bullet in self.bullets:
                    contained = False
                    for new_bullet_info in last_packet.bullets:
                        if bullet.bullet_id == new_bullet_info.bullet_id:
                            contained = True
                            break
                    if not contained:
                        dead_bullets.append(bullet)
                for dead in dead_bullets:
                    dead.physics_world.world.DestroyBody(dead.physics_body)
                    self.bullets.remove(dead)
                dead_bullets.clear()

            # Extrapolate by realtime diff between server and local physics frame
            if self.received_first_packet:
                prev_inputs_length = len(self.previous_inputs)
                for i in range(prev_inputs_length):
                    if self.previous_inputs[0][1] <= last_packet.physics_frame:
                        self.previous_inputs.pop(0)
                    else:
                        break
                if delta_packet_physics_frames >= prev_inputs_length:
                    self.previous_inputs.clear()

                extrapolation_count = int(get_delta_time_s(self.curr_world_time_ns, self.physics_world_time_ns)
                                          / FIXED_DELTA_TIME)
                extrapolation_count = limit(extrapolation_count, 0, MAX_EXTRAPOLATION_STEPS)

                if extrapolation_count:
                    extrapolation_start_frame = self.physics_frame_count
                    prev_inputs_length = len(self.previous_inputs)
                    frame_inputs = []
                    input_index = 0
                    for i in range(extrapolation_count):
                        while (input_index < prev_inputs_length
                               and self.previous_inputs[input_index][1] < extrapolation_start_frame + i):
                            input_index += 1
                        if input_index < prev_inputs_length:
                            frame_inputs.append(self.previous_inputs[input_index])
                        else:
                            frame_inputs.append(PlayerInput())

                    for i in range(extrapolation_count):
                        self.local_player_robot.input = frame_inputs[i]
                        super().fixed_update(FIXED_DELTA_TIME)

                    self.local_player_robot.input = self.player_input

            self.received_first_packet = True

        else:
            super().fixed_update(delta_time)


class ServerWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.udp_socket = UDPServer()

    def fixed_update(self, delta_time):
        self.udp_socket.get_client_packets()

        disconnected_clients = []
        for key in self.udp_socket.clients:
            client = self.udp_socket.clients[key]
            if (client.last_rx_packet.creation_time + CLIENT_DISCONNECT_TIMEOUT_NS < self.curr_time_ns
                    or client.last_rx_packet.disconnect):
                disconnected_clients.append(client)
            else:
                existing_robot = None
                for robot in self.robots:
                    if robot.robot_id == client.player_id:
                        existing_robot = robot
                        break
                if existing_robot is None:
                    existing_robot = self.create_enemy_robot(robot_id=client.player_id, has_ai=False)
                    client.robot = existing_robot
                existing_robot.input = client.last_rx_packet.player_input
        for disconnected in disconnected_clients:
            if disconnected.robot is not None:
                disconnected.robot.remove()
            self.udp_socket.clients.pop(disconnected.address)
        disconnected_clients.clear()

        super().fixed_update(delta_time)

        # TODO: maybe not build robot and bullet info lists fresh every frame
        robot_info_list = []
        for robot in self.robots:
            robot_info_list.append(RobotInfo(robot))
        bullet_info_list = []
        for bullet in self.bullets:
            bullet_info_list.append(BulletInfo(bullet))

        state_packet = StatePacket(creation_time=self.curr_time_ns, world_start_time=self.world_start_time_ns,
                                   physics_frame=self.physics_frame_count, robots=robot_info_list,
                                   bullets=bullet_info_list)

        for key in self.udp_socket.clients:
            client = self.udp_socket.clients[key]
            state_packet.player_id = client.player_id
            self.udp_socket.send_packet(client, state_packet)
