import time

from PyQt5.QtGui import QPainter, QPolygon
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from world_sim import SPWorldSim
from client_world_sim import OnlineWorldSim
from server_world_sim import ServerWorldSim
from globals import Scene, Fonts, GameInfo
from camera import CameraState
from constants import DEBUG_MODE
from ui_overlay import UIOverlay
from util import painter_transform_with_rot, Vector
from sound_manager import SoundManager, music_names
from animation import Animation


class WorldScene(QOpenGLWidget):
    def __init__(self, parent, size, sim_class):
        super().__init__(parent)

        self.main_widget = parent

        self.size = size.copy()

        self.world_sim = sim_class()
        self.world_sim.world_scene = self

        self.animations = []
        Animation.world_scene = self

        self.ui_overlay = UIOverlay()

        self.init_ui()

        SoundManager.instance.play_music(music_names[1], once=True)
        SoundManager.instance.play_random_music = True

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
        qp.fillRect(event.rect(), Qt.black)
        qp.restore()

        self.world_sim.arena.draw(qp)

        # TODO: Maybe use less delta_time if physics can't keep up, to still extrapolate correctly (SP only)
        for bullet in self.world_sim.bullets:
            bullet.draw(qp, self.world_sim.extrapolation_delta_time)
        for robot in self.world_sim.robots:
            robot.draw(qp, self.world_sim.extrapolation_delta_time)

        ended_anims = []
        for anim in self.animations:
            if not anim.draw(qp, self.world_sim.physics_frame_count):
                ended_anims.append(anim)
        for ended in ended_anims:
            self.animations.remove(ended)

        self.ui_overlay.draw_name_tags(qp, self.world_sim.robots)
        if self.world_sim.local_player_robot is not None and not self.world_sim.local_player_robot.is_dead:
            self.ui_overlay.draw_health_bar(qp, self.world_sim.local_player_robot)

        # debugging physics shapes
        if DEBUG_MODE:
            painter_transform_with_rot(qp, Vector(0, 0), 0)
            qp.setPen(Fonts.fps_color)
            for body in self.world_sim.physics_world.world.bodies:
                for fixture in body.fixtures:
                    shape = fixture.shape
                    vertices = [(body.transform * v) for v in shape.vertices]
                    vertices = [(v[0], v[1]) for v in vertices]
                    poly = QPolygon()
                    for vert in vertices:
                        poly.append(QPoint(round(vert[0]), round(vert[1])))
                    qp.drawPolygon(poly)
            qp.restore()

        qp.setFont(Fonts.fps_font)
        qp.setPen(Fonts.fps_color)
        qp.drawText(QPoint(5, 20), str(round(self.world_sim.fps)) + "fps")
        qp.drawText(QPoint(95, 20), str(self.world_sim.frame_time_ms) + "ms")

        qp.end()

        self.world_sim.frame_times_since_ms += (time.time_ns() - self.world_sim.curr_time_ns) / 1000000


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
