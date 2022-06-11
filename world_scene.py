from world_sim import SPWorldSim, OnlineWorldSim, ServerWorldSim
from constants import Scene, ARENA_SIZE, DEBUG_MODE
from networking import ClientPacket
from PyQt5.QtGui import QPainter, QPolygon, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint


class WorldScene(QWidget):
    def __init__(self, parent, size, sim_class):
        super().__init__(parent)

        self.main_widget = parent

        self.size = size

        self.world_sim = sim_class()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, self.size, self.size)
        self.show()

    def clean_mem(self):
        self.world_sim.clean_mem()

    def keyPressEvent(self, event):
        if self.world_sim.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.world_sim.player_input.up = True
        elif event.key() == Qt.Key_S:
            self.world_sim.player_input.down = True
        elif event.key() == Qt.Key_A:
            self.world_sim.player_input.left = True
        elif event.key() == Qt.Key_D:
            self.world_sim.player_input.right = True
        elif event.key() == Qt.Key_Space:
            self.world_sim.player_input.shoot = True
            self.world_sim.player_input.shoot_pressed = True
        elif event.key() == Qt.Key_Escape:
            self.parentWidget().switch_scene(Scene.MAIN_MENU)
        else:
            return
        event.accept()

    def keyReleaseEvent(self, event):
        if self.world_sim.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.world_sim.player_input.up = False
        elif event.key() == Qt.Key_S:
            self.world_sim.player_input.down = False
        elif event.key() == Qt.Key_A:
            self.world_sim.player_input.left = False
        elif event.key() == Qt.Key_D:
            self.world_sim.player_input.right = False
        elif event.key() == Qt.Key_Space:
            self.world_sim.player_input.shoot = False
        else:
            return
        event.accept()

    def paintEvent(self, event):
        self.world_sim.update_world()

        qp = QPainter(self)
        qp.setFont(QFont("sans serif", 12))
        qp.setPen(Qt.red)

        self.world_sim.arena.draw(qp)

        # TODO: Maybe use less delta_time if physics can't keep up, to still extrapolate correctly
        for bullet in self.world_sim.bullets:
            bullet.draw(qp, self.world_sim.extrapolation_delta_time)
        for robot in self.world_sim.robots:
            robot.draw(qp, self.world_sim.extrapolation_delta_time)

        # debugging physics shapes
        if DEBUG_MODE:
            for body in self.world_sim.physics_world.world.bodies:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    vertices = [(body.transform * v) for v in shape.vertices]
                    vertices = [(v[0], ARENA_SIZE - v[1]) for v in vertices]
                    poly = QPolygon()
                    for vert in vertices:
                        poly.append(QPoint(round(vert[0]), round(vert[1])))
                    qp.drawPolygon(poly)

        qp.drawText(QPoint(5, 20), str(round(self.world_sim.fps)))

        qp.end()


class SPWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, SPWorldSim)


class OnlineWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, OnlineWorldSim)

    def clean_mem(self):
        super().clean_mem()

        for i in range(2):
            self.world_sim.udp_socket.send_packet(None, ClientPacket(
                creation_time=(self.world_sim.curr_time_ns + 1000000), disconnect=True))


class ServerWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, ServerWorldSim)
        self.world_sim.player = self.world_sim.create_player()
        self.world_sim.player.input = self.world_sim.player_input
