import time

from util import get_main_path, Vector, painter_transform_with_rot, is_object_on_screen
from globals import Fonts, GameInfo, Scene, Menus
from constants import PLAYER_NAME_OFFSET, HEALTH_BAR_OFFSET
from ui_elements import Menu, Button, UIImage, UIText
from camera import CameraState

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap, QFontMetricsF
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QOpenGLWidget


overlay_texture_path = get_main_path() + "/textures/ui/overlay/"


class UIOverlay:
    def __init__(self):
        self.name_tag_font_metrics = QFontMetricsF(Fonts.name_tag_font)

        self.health_bar = QPixmap(overlay_texture_path + "health-bar.png")
        self.health_bar_size = Vector(self.health_bar.width(), self.health_bar.height())
        self.health_bar_bg = QPixmap(overlay_texture_path + "health-bar-bg.png")
        self.health_bar_bg_size = Vector(self.health_bar_bg.width(), self.health_bar_bg.height())

    def draw_name_tags(self, qp, robots):
        qp.setFont(Fonts.name_tag_font)
        qp.setPen(Fonts.name_tag_color)
        for robot in robots:
            if robot.is_dead:
                continue
            if robot.player_name != "":
                text_width = self.name_tag_font_metrics.width(robot.player_name)
                pos = Vector(0, 0)
                pos.x = round(robot.extrapolation_body.position.x + PLAYER_NAME_OFFSET.x)
                pos.y = round(robot.extrapolation_body.position.y + PLAYER_NAME_OFFSET.y)
                if is_object_on_screen(pos, radius=120):
                    painter_transform_with_rot(qp, pos, 0)
                    qp.drawText(round(-text_width / 2), 0, robot.player_name)
                    qp.restore()

    def draw_health_bar(self, qp, robot):
        health_fill = round((robot.health / robot.max_health) * self.health_bar_size.x)
        pos = Vector(0, 0)
        pos.x = round(robot.extrapolation_body.position.x + HEALTH_BAR_OFFSET.x)
        pos.y = round(robot.extrapolation_body.position.y + HEALTH_BAR_OFFSET.y)
        if is_object_on_screen(pos):
            painter_transform_with_rot(qp, pos, 0)
            qp.drawPixmap(round(-self.health_bar_bg_size.x / 2), round(-self.health_bar_bg_size.y / 2),
                          self.health_bar_bg)
            if health_fill > 0:
                qp.drawPixmap(round(-self.health_bar_bg_size.x / 2), round(-self.health_bar_bg_size.y / 2),
                              self.health_bar, 0, 0, health_fill, 0)
            qp.restore()


class GameOverMenu(Menu):
    class Image(UIImage):
        name = "game_over_image"

    class Score(UIText):
        name = "score"

    class Restart(Button):
        name = "singleplayer"

        def click(self):
            self.main_widget.switch_scene(Scene.SP_WORLD)

    class ExitButton(Button):
        name = "exit"

        def click(self):
            self.main_widget.switch_scene(Scene.MAIN_MENU)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene, None)

        center_pos = Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                            GameInfo.window_size.y / 2 / CameraState.scale.y)

        pos = center_pos.copy()
        pos.y -= 332
        self.elements.append(GameOverMenu.Image(main_widget, pos, self))

        pos = center_pos.copy()
        pos.y -= 0
        self.player_score = GameOverMenu.Score(main_widget, pos, self)
        self.elements.append(self.player_score)

        pos = center_pos.copy()
        pos.y += 178
        self.elements.append(GameOverMenu.Restart(main_widget, pos, self))

        pos = center_pos.copy()
        pos.y += 425
        self.elements.append(GameOverMenu.ExitButton(main_widget, pos, self))

        self.player_score.text = "Score: " + str(GameInfo.local_player_score)


Menus.menus["game_over_menu"] = GameOverMenu


class OverlayWidget(QOpenGLWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.first = True

        self.main_widget = parent
        self.size = size.copy()

        self.mouse_position = Vector(0, 0)

        self.curr_time_ns = time.time_ns()

        self._frames_since_last_show = 0
        self._last_fps_show_time = 0
        self.fps = 0

        self.active_menu = None
        self.is_clicking = False

        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, self.size.x, self.size.y)
        self.setMouseTracking(True)
        self.show()

    def switch_menu(self, menu_name):
        self.active_menu = None
        menu_class = Menus.menus.get(menu_name)
        if menu_class is not None:
            self.active_menu = menu_class(self.main_widget, GameInfo.window_size, self)

    def clean_mem(self):
        pass

    def keyPressEvent(self, event):
        if self.active_menu is not None:
            self.active_menu.key_press_event(event)

    def keyReleaseEvent(self, event):
        if self.active_menu is not None:
            self.active_menu.key_release_event(event)

    def mouseMoveEvent(self, event):
        self.mouse_position.x = event.x() / CameraState.scale.x
        self.mouse_position.y = event.y() / CameraState.scale.y
        if self.active_menu is not None and self.active_menu.drag_element is not None:
            self.active_menu.dragging = True
            self.active_menu.mouse_drag(self.mouse_position)
        event.accept()

    def mousePressEvent(self, event):
        self.mouse_position.x = event.x() / CameraState.scale.x
        self.mouse_position.y = event.y() / CameraState.scale.y
        if event.button() == Qt.LeftButton:
            self.is_clicking = True
            if self.active_menu is not None:
                if self.active_menu.drag_element is None:
                    self.active_menu.drag_element = self.active_menu.selected_element
                    self.active_menu.mouse_drag(self.mouse_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.active_menu is not None:
                self.active_menu.dragging = False
                self.active_menu.drag_element = None

    def draw(self, qp):
        self.curr_time_ns = time.time_ns()

        if self.active_menu is not None:
            if self.is_clicking:
                self.active_menu.click_element()
                self.is_clicking = False

            self.active_menu.update_ui(self.mouse_position, self.curr_time_ns)

            self.active_menu.draw(qp)
