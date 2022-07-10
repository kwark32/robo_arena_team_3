from world_sim import WorldSim
from robot import PlayerInput
from util import limit, lerp
from networking import UDPClient, ClientPacket
from globals import GameInfo
from constants import FIXED_DELTA_TIME, FIXED_DELTA_TIME_NS, MAX_EXTRAPOLATION_STEPS, TIME_SYNC_LERP_AMOUNT


class OnlineWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        GameInfo.local_player_id = -1

        self.previous_inputs = []
        self.udp_socket = UDPClient()
        self.server_world_start_time_ns = 0
        self.last_packet_physics_frame = 0
        self.server_client_latency_ns = 0

        self.received_first_packet = False

    def set_robots(self, robots):
        for new_robot_info in robots:
            existing_robot = None
            for robot in self.robots:
                if robot.robot_id == new_robot_info.player_id:
                    existing_robot = robot
                    break

            if existing_robot is None:
                if GameInfo.local_player_id == new_robot_info.player_id:
                    self.local_player_robot = self.create_player(robot_id=new_robot_info.player_id)
                    self.local_player_robot.input = self.player_input
                    existing_robot = self.local_player_robot
                else:
                    existing_robot = self.create_enemy_robot(has_ai=False, robot_id=new_robot_info.player_id)

            new_robot_info.set_robot_values(existing_robot)

        if len(self.robots) > len(robots):
            dead_robots = []
            for robot in self.robots:
                contained = False
                for new_robot_info in robots:
                    if robot.robot_id == new_robot_info.player_id:
                        if new_robot_info.died:
                            robot.die()
                        contained = True
                        break
                if not contained:
                    dead_robots.append(robot)
            for dead in dead_robots:
                dead.remove()
                self.robots.remove(dead)
                if dead is self.local_player_robot:
                    self.local_player_robot = None
            dead_robots.clear()

    def set_bullets(self, bullets):
        for new_bullet_info in bullets:
            existing_bullet = None
            for bullet in self.bullets:
                if bullet.bullet_id == new_bullet_info.bullet_id:
                    existing_bullet = bullet
                    break

            if existing_bullet is None:
                existing_bullet = new_bullet_info.bullet_class(self)

            new_bullet_info.set_bullet_values(existing_bullet)

        if len(self.bullets) > len(bullets):
            dead_bullets = []
            for bullet in self.bullets:
                contained = False
                for new_bullet_info in bullets:
                    if bullet.bullet_id == new_bullet_info.bullet_id:
                        contained = True
                        break
                if not contained:
                    dead_bullets.append(bullet)
            for dead in dead_bullets:
                # print("removing bullet " + str(dead.bullet_id) + " from robot " + str(dead.source_id))
                dead.physics_world.world.DestroyBody(dead.physics_body)
                self.bullets.remove(dead)
            dead_bullets.clear()

    def extrapolate(self, packet_frame, extrapolation_count):
        if self.local_player_robot is not None:
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
                        frame_inputs.append(self.previous_inputs[input_index][0].copy())
                    else:
                        frame_inputs.append(PlayerInput())

                # print("extrapolation count: " + str(extrapolation_count))
                for i in range(extrapolation_count):
                    GameInfo.current_frame_seed = self.server_world_start_time_ns + self.physics_frame_count
                    self.local_player_robot.input = frame_inputs[i]
                    super().fixed_update(FIXED_DELTA_TIME)
                    # self.physics_frame_count += 1
                    # self.physics_world_time_ns = FIXED_DELTA_TIME_NS * self.physics_frame_count

                self.local_player_robot.input = self.player_input

            i = len(self.previous_inputs) - 1
            while i >= 0:
                if self.previous_inputs[i][1] < packet_frame:
                    self.previous_inputs.pop(i)
                i -= 1

    def fixed_update(self, delta_time):
        # print(self.curr_time_ns - self.udp_socket.curr_time_ns)
        self.udp_socket.curr_time_ns = self.curr_time_ns

        GameInfo.current_frame_seed = self.server_world_start_time_ns + self.physics_frame_count

        if self.local_player_robot is not None:
            input_delay_frames = round(self.server_client_latency_ns / FIXED_DELTA_TIME_NS)
            if len(self.previous_inputs) <= MAX_EXTRAPOLATION_STEPS * 2 and self.player_input is not None:
                self.previous_inputs.append((self.player_input.copy(), self.physics_frame_count + input_delay_frames))

            input_to_use = self.player_input
            for player_input in self.previous_inputs:
                if player_input[1] > self.physics_frame_count - input_delay_frames:
                    input_to_use = player_input[0]
                    break
            self.local_player_robot.input = input_to_use

        if self.local_player_robot is None or self.player_input is None:
            packet = ClientPacket(creation_time=self.curr_time_ns, player_name=GameInfo.local_player_name)
        else:
            packet = ClientPacket(creation_time=self.curr_time_ns, player_input=self.player_input,
                                  player_name=GameInfo.local_player_name)
        # print("sending packet on frame " + str(self.physics_frame_count))
        self.udp_socket.send_packet(None, packet)

        self.player_input.shoot_pressed = False

        new_packets = []
        while self.udp_socket.get_packet_available():
            new_packets.append(self.udp_socket.get_packet())

        if new_packets:
            last_packet = new_packets[0]
            for packet in new_packets:
                if packet.physics_frame >= last_packet.physics_frame:
                    last_packet = packet

            if last_packet.physics_frame < self.last_packet_physics_frame:
                # print("received older packet")
                super().fixed_update(delta_time)
                return

            self.server_world_start_time_ns = last_packet.world_start_time

            self.server_client_latency_ns = (last_packet.receive_time - last_packet.client_rtt_start) >> 1
            # self.server_client_latency_ns = 200000000
            # print("latency ms: " + str(round(self.server_client_latency_ns / 1000000)))
            new_wst = (self.curr_time_ns - last_packet.physics_frame * FIXED_DELTA_TIME_NS
                       - self.server_client_latency_ns)
            if self.local_player_robot is None:
                self.world_start_time_ns = new_wst
            else:
                self.world_start_time_ns = lerp(self.world_start_time_ns, new_wst, TIME_SYNC_LERP_AMOUNT)
            self.curr_world_time_ns = self.curr_time_ns - self.world_start_time_ns
            self.last_packet_physics_frame = last_packet.physics_frame
            physics_frames_ahead = self.physics_frame_count - self.last_packet_physics_frame
            if physics_frames_ahead < 0:
                physics_frames_ahead = 0
            # print("physics frames ahead: " + str(physics_frames_ahead))
            self.physics_frame_count = self.last_packet_physics_frame
            self.physics_world_time_ns = self.physics_frame_count * FIXED_DELTA_TIME_NS

            # Set all variables from last packet
            GameInfo.local_player_id = last_packet.player_id
            self.set_robots(last_packet.robots)
            self.set_bullets(last_packet.bullets)

            self.extrapolate(self.last_packet_physics_frame, physics_frames_ahead + 1)

            # print("got packet")

        else:
            # print("no packet")
            super().fixed_update(delta_time)
