import sys
import time
import socket
import select
import pickle

from globals import GameInfo
from constants import SIMULATED_PING_NS


i = 0
for arg in sys.argv:
    if arg == "--ip":
        if len(sys.argv) > i + 1:
            GameInfo.server_ip = sys.argv[i + 1]
            break
    i += 1


class Packet:
    def __init__(self, creation_time=0):
        self.creation_time = creation_time
        if self.creation_time == 0:
            self.creation_time = time.time_ns()
        self.receive_time = 0


class StatePacket(Packet):
    def __init__(self, creation_time=0, world_start_time=0, physics_frame=0, player_id=0, robots=None, bullets=None):
        super().__init__(creation_time=creation_time)
        self.world_start_time = world_start_time
        self.client_rtt_start = 0
        self.physics_frame = physics_frame
        self.player_id = player_id
        self.robots = robots
        if self.robots is None:
            self.robots = []
        self.bullets = bullets
        if self.bullets is None:
            self.bullets = []

    def to_string(self):
        ret = ("{\n  rtt start time: " + str(self.client_rtt_start) + "\n  physics frame: " + str(self.physics_frame)
               + "\n  player ID: " + str(self.player_id) + "\n  robot IDs: {")
        for robot in self.robots:
            ret += str(robot.player_id) + ", "
        if len(self.robots) > 0:
            ret = ret[:-2]
        ret += "}\n  bullet IDs: {"
        for bullet in self.bullets:
            ret += "(" + str(bullet.source_id) + ", " + str(bullet.bullet_id) + ")" + ", "
        if len(self.bullets) > 0:
            ret = ret[:-2]
        ret += "}\n}"
        return ret


class ClientPacket(Packet):
    def __init__(self, creation_time=0, player_input=None, player_name="", disconnect=False):
        super().__init__(creation_time=creation_time)
        self.player_input = player_input
        self.player_name = player_name
        self.disconnect = disconnect

    def to_string(self):
        p_input = "None"
        if self.player_input is not None:
            p_input = self.player_input.to_string()
        return ("{\n  input: " + p_input + "\n  name: "
                + self.player_name + "\n  disconnect: " + str(self.disconnect) + "\n}")


class Client:
    def __init__(self, address, player_id=-1, player_name=""):
        self.address = address
        self.player_id = player_id
        if player_id < 0:
            self.player_id = GameInfo.next_player_id
            GameInfo.next_player_id += 1

        self.player_name = player_name
        self.last_rx_packet = None
        self.robot = None


class UDPSocket:
    def __init__(self):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self._udp_socket_list = [self.udp_socket]

        self._buffered_message_address = None

        self.curr_time_ns = 0

    def get_packet_available(self):
        read_sockets, write_sockets, error_sockets = select.select(self._udp_socket_list, [], [], 0)
        return len(read_sockets) > 0 or self._buffered_message_address is not None

    def get_packet(self):
        buffer_count = 0
        if self._buffered_message_address is not None:
            bytes_address_tuple = self._buffered_message_address
            self._buffered_message_address = None
            buffer_count = bytes_address_tuple[0][1] - 1
        else:
            bytes_address_tuple = self.udp_socket.recvfrom(GameInfo.buffer_size)
            buffer_count = bytes_address_tuple[0][1] - 1

        packet_id = bytes_address_tuple[0][0]
        message = bytes_address_tuple[0][2:]
        address = bytes_address_tuple[1]

        while buffer_count > 0 and self.get_packet_available():
            bytes_address_tuple = self.udp_socket.recvfrom(GameInfo.buffer_size)
            new_packet_id = bytes_address_tuple[0][0]
            if new_packet_id == packet_id and address == bytes_address_tuple[1]:
                message += bytes_address_tuple[0][2:]
                buffer_count -= 1
            else:
                self._buffered_message_address = bytes_address_tuple
                break

        return address, message

    def send_packet(self, address, packet):
        dump = pickle.dumps(packet)
        size = len(dump)
        header_size = 2
        buffer_count = int(size / (GameInfo.buffer_size - header_size))
        if size % (GameInfo.buffer_size - header_size) > 0:
            buffer_count += 1
        packet_header = bytes([(packet.creation_time >> 20) % 256, buffer_count])
        while size > 0:
            to_send = packet_header
            if size > GameInfo.buffer_size - header_size:
                to_send += dump[:(GameInfo.buffer_size - header_size)]
                dump = dump[(GameInfo.buffer_size - header_size):]
                size -= GameInfo.buffer_size - header_size
            else:
                to_send += dump
                size = 0
            self.udp_socket.sendto(to_send, address)

    def close(self):
        self.udp_socket.close()


class UDPServer(UDPSocket):
    def __init__(self):
        super().__init__()
        self.packets_in = []
        self.packets_out = []

        self.udp_socket.bind(("", GameInfo.port))
        self.clients = {}  # client dict: address (str) -> client

    def update_socket(self):
        # Check get list
        address, packet = None, None
        # TODO: < should be <=, but that causes stuttering
        while (len(self.packets_in) > 0
               and self.packets_in[0][1].receive_time + int(SIMULATED_PING_NS >> 1) < self.curr_time_ns):
            address, packet = self.packets_in.pop(0)

        if address and packet:
            packet.receive_time = self.curr_time_ns
            client = self.clients.get(address)
            if client is None and not packet.disconnect:
                client = Client(address, player_name=packet.player_name)
                self.clients[address] = client
            if client is not None:
                if client.last_rx_packet is None or packet.creation_time >= client.last_rx_packet.creation_time:
                    client.last_rx_packet = packet

        # Check send list
        # TODO: < should be <=, but that causes stuttering
        while (len(self.packets_out) > 0
               and self.packets_out[0][1].creation_time + int(SIMULATED_PING_NS >> 1) < self.curr_time_ns):
            pkt = self.packets_out.pop(0)
            super().send_packet(pkt[0], pkt[1])

    def get_client_packets(self):
        while self.get_packet_available():
            address, message = self.get_packet()
            packet = pickle.loads(message)
            packet.receive_time = self.curr_time_ns
            # print("received client packet:\n" + packet.to_string() + "\n")

            self.packets_in.append((address, packet))
            self.update_socket()

    def send_packet(self, client, state_packet):
        self.packets_out.append((client.address, state_packet))
        self.update_socket()


class UDPClient(UDPSocket):
    def __init__(self):
        super().__init__()

    def get_packet(self):
        server_address, message = super().get_packet()
        state_packet = pickle.loads(message)
        state_packet.receive_time = self.curr_time_ns
        return state_packet

    def send_packet(self, server, client_packet):
        super().send_packet((GameInfo.server_ip, GameInfo.port), client_packet)
