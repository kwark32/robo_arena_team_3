import time

from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from ui_elements import Button, Menu
from util import Vector, ns_to_s, is_point_inside_rect
from constants import DEBUG_MODE, Scene, Menu


class MainMenu(Menu):
    class ExitButton(Button):
        name = "exit"

        def click(self):
            self.main_widget.running = False

    class SingleplayerButton(Button):
        name = "singleplayer"

        def click(self):
            self.main_widget.switch_scene(Scene.SP_WORLD)

    class LocalMultiplayerButton(Button):
        name = "local_multiplayer"

        def click(self):
            print("Local multiplayer button clicked!")
            print("TODO: Move host button to separate (and implement local multiplayer)")
            self.main_widget.switch_scene(Scene.SERVER_WORLD)

    class OnlineMultiplayerButton(Button):
        name = "online_multiplayer"

        def click(self):
            self.main_widget.switch_scene(Scene.ONLINE_WORLD)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene)

        self.elements.append(MainMenu.ExitButton(main_widget, Vector(self.size / 2, 800)))
        self.elements.append(MainMenu.SingleplayerButton(main_widget, Vector(self.size / 2, 350)))
        self.elements.append(MainMenu.OnlineMultiplayerButton(main_widget, Vector(self.size / 2, 500)))
        self.elements.append(MainMenu.LocalMultiplayerButton(main_widget, Vector(self.size / 2, 600)))


class MainMenuScene(QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.main_widget = self.parentWidget()

        self.parent = parent
        self.size = size

        self.active_menu = MainMenu(self.main_widget, self.size)
        self.is_clicking = False

        self.init_ui()

        self.mouse_position = Vector(0, 0)

        self._last_frame_time_ns = time.time_ns()
        self._frames_since_last_show = 0
        self._last_fps_show_time = time.time_ns()
        self.fps = 0

    def init_ui(self):
        self.setGeometry(0, 0, self.size, self.size)
        self.setMouseTracking(True)
        self.show()

    def switch_menu(self, menu):
        self.active_menu = None
        if menu == Menu.MAIN_MENU:
            self.active_menu = MainMenu(self.main_widget, self.size)
        elif menu == Menu.ONLINE_OPTIONS:
            # self.active_menu = OnlineOptions(self.main_widget, self.size)
            pass
        elif menu == Menu.SETTINGS:
            # self.active_menu = Settings(self.main_widget, self.size)
            pass

    def clean_mem(self):
        pass

    def mouseMoveEvent(self, event):
        self.mouse_position.x = event.x()
        self.mouse_position.y = event.y()
        event.accept()

    def mousePressEvent(self, event):
        self.mouse_position.x = event.x()
        self.mouse_position.y = event.y()
        if event.button() == Qt.LeftButton:
            self.is_clicking = True

    def paintEvent(self, event):
        curr_time_ns = time.time_ns()
        # delta_time = ns_to_s(curr_time_ns - self._last_frame_time_ns)
        self._last_frame_time_ns = curr_time_ns

        if self.is_clicking:
            self.active_menu.click_element()
            self.is_clicking = False

        self.active_menu.update_ui(self.mouse_position)

        if DEBUG_MODE:
            self._frames_since_last_show += 1
            last_fps_show_delta = ns_to_s(curr_time_ns - self._last_fps_show_time)
            if last_fps_show_delta > 0.5:
                self.fps = self._frames_since_last_show / last_fps_show_delta
                self._frames_since_last_show = 0
                self._last_fps_show_time = curr_time_ns

        qp = QPainter(self)
        qp.setFont(QFont("sans serif", 12))
        qp.setPen(Qt.red)

        qp.fillRect(0, 0, self.size, self.size, QColor(50, 50, 50))

        qp.setFont(QFont("sans serif", 85))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(210, 210), "Robo Arena")
        # draw static menu background
        # qp.drawPixmap(QPoint(), <menu background pixmap>)

        self.active_menu.draw(qp)

        if DEBUG_MODE:
            qp.setFont(QFont("sans serif", 12))
            qp.setPen(Qt.red)
            qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()
