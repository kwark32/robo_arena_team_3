import time
import socket
import select
import pickle


server_ip = "127.0.0.1"
port = 54345
server_ip_port = server_ip, port
buffer_size = 4096


def byte_address_to_str(address):
    return str(address[0]) + "." + str(address[1]) + "." + str(address[2]) + "." + str(address[3])


class RobotInfo:
    def __init__(self, robot_body, player_id=0, player_name="Player"):
        self.robot_body = robot_body
        self.player_id = player_id
        self.player_name = player_name


class BulletInfo:
    def __init__(self, bullet_body, bullet_class, from_player_id=0):
        self.bullet_body = bullet_body
        self.bullet_class = bullet_class
        self.from_player_id = from_player_id


class Packet:
    def __init__(self, creation_time=0):
        self.creation_time = creation_time
        if self.creation_time == 0:
            self.creation_time = time.time_ns()

    class StatePacket:
        def __init__(self, creation_time=0, physics_frame=0, player_id=0, robots=None, bullets=None):
            super().__init__(creation_time=creation_time)
            self.physics_frame = physics_frame
            self.player_id = player_id
            self.robots = robots
            if self.robots is None:
                self.robots = []
            self.bullets = bullets
            if self.bullets is None:
                self.bullets = []

    class ClientPacket:
        def __init__(self, creation_time=0, player_input=None, player_name="Player"):
            super().__init__(creation_time=creation_time)
            self.player_input = player_input
            self.player_name = player_name


class Client:
    def __init__(self, address, player_id, player_name="Player"):
        self.address = address
        self.player_id = player_id
        self.player_name = player_name
        self.last_rx_packet = None


class UDPSocket:
    def __init__(self):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_socket_list = [self.udp_socket]

    def get_packet_available(self):
        read_sockets, write_sockets, error_sockets = select.select(self.udp_socket_list, [], [], 0)
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

    def get_packet(self):
        client_address, client_packet = super().get_packet()
        if client_address is None:
            return None, None
        str_address = byte_address_to_str(client_address)
        client = self.clients[str_address]
        return client, client_packet

    def send_packet(self, client, state_packet):
        super().send_packet(client.address, state_packet)


class UDPClient(UDPSocket):
    def __init__(self):
        super().__init__()

    def get_packet(self):
        server_address, state_packet = super().get_packet()
        return state_packet

    def send_packet(self, client, client_packet):
        super().send_packet(server_ip_port, client_packet)
