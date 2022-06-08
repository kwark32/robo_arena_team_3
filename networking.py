import time
import socket
import select
import pickle


server_ip = "127.0.0.1"
port = 54345
server_ip_port = server_ip, port
buffer_size = 4096


class RobotInfo:
    def __init__(self, robot):
        self.robot_body = robot.sim_body
        self.player_id = robot.robot_id
        self.health = robot.health
        self.weapon_class = robot.weapon.weapon_type
        self.last_shot_frame = robot.weapon.last_shot_frame
        self.player_name = robot.player_name
        self.last_position = robot.last_position
        self.forward_velocity_goal = robot.forward_velocity_goal


class BulletInfo:
    def __init__(self, bullet):
        self.bullet_id = bullet.bullet_id
        self.bullet_body = bullet.sim_body
        self.bullet_class = bullet.bullet_type
        self.from_player_id = bullet.source_id


class Packet:
    def __init__(self, creation_time=0):
        self.creation_time = creation_time
        if self.creation_time == 0:
            self.creation_time = time.time_ns()


class StatePacket(Packet):
    def __init__(self, creation_time=0, world_start_time=0, physics_frame=0, player_id=0, robots=None, bullets=None):
        super().__init__(creation_time=creation_time)
        self.world_start_time = world_start_time
        self.physics_frame = physics_frame
        self.player_id = player_id
        self.robots = robots
        if self.robots is None:
            self.robots = []
        self.bullets = bullets
        if self.bullets is None:
            self.bullets = []


class ClientPacket(Packet):
    def __init__(self, creation_time=0, player_input=None, player_name="Player"):
        super().__init__(creation_time=creation_time)
        self.player_input = player_input
        self.player_name = player_name
        self.disconnect = False


class Client:
    next_player_id = 0

    def __init__(self, address, player_id=-1, player_name="Player"):
        self.address = address
        self.player_id = player_id
        if player_id == -1:
            self.player_id = Client.next_player_id
            Client.next_player_id += 1
        self.player_name = player_name
        self.last_rx_packet = None


class UDPSocket:
    def __init__(self):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._udp_socket_list = [self.udp_socket]

    def get_packet_available(self):
        read_sockets, write_sockets, error_sockets = select.select(self._udp_socket_list, [], [], 0)
        return len(read_sockets) > 0

    def get_packet(self):
        bytes_address_tuple = self.udp_socket.recvfrom(buffer_size)

        message = bytes_address_tuple[0]
        address = bytes_address_tuple[1]

        packet = pickle.loads(message)

        return address, packet

    def send_packet(self, address, packet):
        self.udp_socket.sendto(pickle.dumps(packet), address)


class UDPServer(UDPSocket):
    def __init__(self):
        super().__init__()

        self.udp_socket.bind((server_ip, port))
        self.clients = {}  # client dict: address (str) -> client

    def get_client_packets(self):
        while self.get_packet_available():
            address, packet = self.get_packet()
            client = self.clients.get(address)
            if client is None or packet.disconnect:
                client = Client(address)
                self.clients[address] = client
            if client.last_rx_packet is None or packet.creation_time >= client.last_rx_packet.creation_time:
                client.last_rx_packet = packet

    def send_packet(self, client, state_packet):
        super().send_packet(client.address, state_packet)


class UDPClient(UDPSocket):
    def __init__(self):
        super().__init__()

    def get_packet(self):
        server_address, state_packet = super().get_packet()
        return state_packet

    def send_packet(self, server, client_packet):
        super().send_packet(server_ip_port, client_packet)
