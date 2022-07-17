from PyQt5.QtGui import QPainter, QPolygon
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from world_sim import SPWorldSim
from client_world_sim import OnlineWorldSim
from server_world_sim import ServerWorldSim
from globals import Scene, Fonts, GameInfo
from camera import CameraState
from constants import DEBUG_MODE
from ui_overlay import UIOverlay


class WorldScene(QWidget):
    def __init__(self, parent, size, sim_class):
        super().__init__(parent)

        self.main_widget = parent

        self.size = size.copy()

        self.world_sim = sim_class()

        self.ui_overlay = UIOverlay()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, self.size.x, self.size.y)
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
        qp.scale(CameraState.scale_factor, CameraState.scale_factor)
        qp.setRenderHint(QPainter.Antialiasing)

        qp.save()
        qp.resetTransform()
        scale = CameraState.scale.x
        if CameraState.scale.x < CameraState.scale.y:
            scale = CameraState.scale.y
        qp.scale(scale, scale)
        qp.fillRect(0, 0, GameInfo.window_reference_size.x, GameInfo.window_reference_size.y, Qt.black)
        qp.restore()

        self.world_sim.arena.draw(qp)

        # TODO: Maybe use less delta_time if physics can't keep up, to still extrapolate correctly (SP only)
        for bullet in self.world_sim.bullets:
            bullet.draw(qp, self.world_sim.extrapolation_delta_time)
        for robot in self.world_sim.robots:
            robot.draw(qp, self.world_sim.extrapolation_delta_time)

        self.ui_overlay.draw_name_tags(qp, self.world_sim.robots)
        if self.world_sim.local_player_robot is not None:
            self.ui_overlay.draw_health_bar(qp, self.world_sim.local_player_robot)

        # debugging physics shapes
        if DEBUG_MODE:
            qp.setPen(Fonts.fps_color)
            for body in self.world_sim.physics_world.world.bodies:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    vertices = [(body.transform * v) for v in shape.vertices]
                    vertices = [(v[0], self.world_sim.arena.size - v[1]) for v in vertices]
                    poly = QPolygon()
                    for vert in vertices:
                        poly.append(QPoint(round(vert[0]), round(vert[1])))
                    qp.drawPolygon(poly)

        qp.setFont(Fonts.fps_font)
        qp.setPen(Fonts.fps_color)
        qp.drawText(QPoint(5, 20), str(round(self.world_sim.fps)))

        qp.end()


class SPWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, SPWorldSim)


class OnlineWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, OnlineWorldSim)


class ServerWorldScene(WorldScene):
    def __init__(self, parent, size):
        super().__init__(parent, size, ServerWorldSim)

        self.world_sim.local_player_robot = self.world_sim.create_player(robot_id=GameInfo.local_player_id)
        self.world_sim.local_player_robot.input = self.world_sim.player_input
