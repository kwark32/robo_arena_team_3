import time

from world_sim import SPWorldSim
from client_world_sim import OnlineWorldSim
from server_world_sim import ServerWorldSim
from globals import Scene, Fonts, GameInfo
from camera import CameraState
from constants import DEBUG_MODE
from ui_overlay import UIOverlay, OverlayWidget, Scoreboard
from util import painter_transform_with_rot, Vector
from sound_manager import SoundManager, music_names
from animation import Animation

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPainter, QPolygon
    from PyQt5.QtCore import Qt, QPoint


class WorldScene(OverlayWidget):
    def __init__(self, parent):
        super().__init__(parent)

        sim_class = type(self).sim_class
        self.world_sim = sim_class()
        self.world_sim.world_scene = self

        self.animations = []
        Animation.world_scene = self

        self.ui_overlay = UIOverlay()

        self.score_board = None

        self.mouse_pressed = False
        self.space_pressed = False

        SoundManager.instance.play_music(music_names[1], once=True)
        SoundManager.instance.play_random_music = True

    def clean_mem(self):
        super().clean_mem()

        self.world_sim.clean_mem()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

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
            self.space_pressed = True
            self.world_sim.player_input.shoot = True
            self.world_sim.player_input.shoot_pressed = True
        elif event.key() == Qt.Key_Escape:
            self.main_widget.switch_scene(Scene.MAIN_MENU)
        else:
            return
        event.accept()

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)

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
            self.space_pressed = False
            if not self.mouse_pressed:
                self.world_sim.player_input.shoot = False
        else:
            return
        event.accept()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.world_sim.player_input.shoot = True
            self.world_sim.player_input.shoot_pressed = True
            event.accept()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            if not self.space_pressed:
                self.world_sim.player_input.shoot = False
            event.accept()

    def paintEvent(self, event):
        # TODO: Look into why this strange fix is needed
        if not hasattr(self, "first") or self.first or not self.main_widget.running:
            self.first = False
            return

        self.set_turret_rotation()

        self.world_sim.update_world()

        qp = QPainter(self)
        qp.fillRect(event.rect(), Qt.black)

        qp.scale(CameraState.scale_factor, CameraState.scale_factor)
        qp.setRenderHint(QPainter.Antialiasing)

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

        if CameraState.scale.x > CameraState.scale.y:
            qp.fillRect(0, 0, CameraState.x_offset, GameInfo.window_reference_size.y, Qt.black)
            qp.fillRect(GameInfo.window_reference_size.x + CameraState.x_offset, 0,
                        CameraState.x_offset, GameInfo.window_reference_size.y, Qt.black)

        super().draw(qp)

        if self.score_board is not None:
            self.score_board.draw(qp)

        qp.setFont(Fonts.fps_font)
        qp.setPen(Fonts.fps_color)
        qp.drawText(QPoint(5, 20), str(round(self.world_sim.fps)) + "fps")
        qp.drawText(QPoint(105, 20), str(self.world_sim.frame_time_ms) + "ms")

        qp.end()

        self.world_sim.frame_times_since_ms += (time.time_ns() - self.world_sim.curr_time_ns) / 1000000

    def set_turret_rotation(self):
        if self.world_sim.player_input is not None and self.world_sim.local_player_robot is not None:
            robot_pos = self.world_sim.local_player_robot.sim_body.position.copy()
            mouse_pos = self.mouse_position.copy()
            half_screen = GameInfo.window_reference_size.copy()
            half_screen.div(2)
            mouse_pos.sub(half_screen)
            if CameraState.position is not None:
                mouse_pos.add(CameraState.position)
            robot_mouse_diff = robot_pos.diff(mouse_pos)
            turret_rot = robot_mouse_diff.signed_angle()
            self.world_sim.player_input.turret_rot = turret_rot


class SPWorldScene(WorldScene):
    sim_class = SPWorldSim


class OnlineWorldScene(WorldScene):
    sim_class = OnlineWorldSim

    def __init__(self, parent):
        super().__init__(parent)

        self.score_board = Scoreboard()


class ServerWorldScene(WorldScene):
    sim_class = ServerWorldSim

    def __init__(self, parent):
        super().__init__(parent)

        self.world_sim.local_player_robot = self.world_sim.create_player(robot_id=GameInfo.local_player_id,
                                                                         should_respawn=True)
        self.world_sim.local_player_robot.input = self.world_sim.player_input

        self.score_board = Scoreboard()
