from world_sim import WorldSim
from networking import UDPServer, StatePacket
from constants import CLIENT_DISCONNECT_TIMEOUT_NS
from robot import RobotInfo
from weapons import BulletInfo


class ServerWorldSim(WorldSim):
    def __init__(self):
        super().__init__()

        self.udp_socket = UDPServer()

    def clean_mem(self):
        self.udp_socket.close()

    def fixed_update(self, delta_time):
        self.udp_socket.curr_time_ns = self.curr_time_ns

        self.udp_socket.get_client_packets()

        disconnected_clients = []
        for key in self.udp_socket.clients:
            client = self.udp_socket.clients[key]
            if client.last_rx_packet is None:
                continue
            if (client.last_rx_packet.receive_time + CLIENT_DISCONNECT_TIMEOUT_NS < self.curr_time_ns
                    or client.last_rx_packet.disconnect):
                disconnected_clients.append(client)
            else:
                existing_robot = None
                for robot in self.robots:
                    if robot.robot_id == client.player_id:
                        existing_robot = robot
                        break
                if existing_robot is None:
                    existing_robot = self.create_enemy_robot(robot_id=client.player_id, has_ai=False,
                                                             player_name=client.player_name)
                    client.robot = existing_robot
                existing_robot.input = client.last_rx_packet.player_input
        for disconnected in disconnected_clients:
            if disconnected.robot is not None:
                disconnected.robot.die()
                disconnected.robot.remove()
            self.udp_socket.clients.pop(disconnected.address)
        disconnected_clients.clear()

        self.clear_dead_robots()

        super().fixed_update(delta_time)

        # TODO: maybe not build robot and bullet info lists fresh every frame
        robot_info_list = []
        for robot in self.robots:
            robot_info_list.append(RobotInfo(robot))
        bullet_info_list = []
        for bullet in self.bullets:
            bullet_info_list.append(BulletInfo(bullet))

        state_packet = StatePacket(creation_time=self.curr_time_ns,
                                   physics_frame=self.physics_frame_count, robots=robot_info_list,
                                   bullets=bullet_info_list)

        for key in self.udp_socket.clients:
            if client.last_rx_packet is not None:
                client = self.udp_socket.clients[key]
                state_packet.player_id = client.player_id
                state_packet.client_rtt_start = client.last_rx_packet.creation_time
                self.udp_socket.send_packet(client, state_packet)
