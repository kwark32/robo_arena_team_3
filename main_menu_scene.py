import time

from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from ui_elements import Button, Menu, TextField
from util import Vector, ns_to_s
from constants import DEBUG_MODE, Scene, Menus, MAX_PLAYER_NAME_LENGTH


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

    class OnlineMultiplayerButton(Button):
        name = "online_multiplayer"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.ONLINE_OPTIONS)

    class SettingsButton(Button):
        name = "settings"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.SETTINGS)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene)

        self.elements.append(MainMenu.ExitButton(main_widget, Vector(self.size / 2, 850), self))
        self.elements.append(MainMenu.SingleplayerButton(main_widget, Vector(self.size / 2, 300), self))
        self.elements.append(MainMenu.OnlineMultiplayerButton(main_widget, Vector(self.size / 2, 425), self))
        self.elements.append(MainMenu.LocalMultiplayerButton(main_widget, Vector(self.size / 2, 525), self))
        self.elements.append(MainMenu.SettingsButton(main_widget, Vector(self.size / 2, 675), self))

    def escape_pressed(self):
        self.main_widget.running = False

    def draw(self, qp):
        qp.setFont(QFont("sans serif", 75))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(245, 150), "Robo Arena")
        # draw static menu background
        # qp.drawPixmap(QPoint(), <menu background pixmap>)

        super().draw(qp)


class OnlineOptions(Menu):
    class BackButton(Button):
        name = "back"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    class PlayerNameField(TextField):
        name = "player_name"

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene)

        self.elements.append(OnlineOptions.BackButton(main_widget, Vector(self.size / 2, 850), self))
        self.elements.append(OnlineOptions.PlayerNameField(main_widget, Vector(self.size / 2, 500),
                                                           self, text_offset=Vector(255, 50),
                                                           max_text_length=MAX_PLAYER_NAME_LENGTH))

    def escape_pressed(self):
        self.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    def draw(self, qp):
        qp.setFont(QFont("sans serif", 60))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(185, 150), "Online Multiplayer")
        # draw static menu background
        # qp.drawPixmap(QPoint(), <menu background pixmap>)

        super().draw(qp)


class Settings(Menu):
    class BackButton(Button):
        name = "back"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene)

        self.elements.append(Settings.BackButton(main_widget, Vector(self.size / 2, 850), self))

    def escape_pressed(self):
        self.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    def draw(self, qp):
        qp.setFont(QFont("sans serif", 75))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(315, 150), "Settings")

        # TODO: Set correct bg pixmap

        super().draw(qp)


class MainMenuScene(QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.main_widget = self.parentWidget()

        self.parent = parent
        self.size = size

        self.active_menu = MainMenu(self.main_widget, self.size, self)
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
        if menu == Menus.MAIN_MENU:
            self.active_menu = MainMenu(self.main_widget, self.size, self)
        elif menu == Menus.ONLINE_OPTIONS:
            self.active_menu = OnlineOptions(self.main_widget, self.size, self)
        elif menu == Menus.SETTINGS:
            self.active_menu = Settings(self.main_widget, self.size, self)

    def clean_mem(self):
        pass

    def keyPressEvent(self, event):
        if self.active_menu is not None:
            self.active_menu.key_press_event(event)

    def keyReleaseEvent(self, event):
        if self.active_menu is not None:
            self.active_menu.key_release_event(event)

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

        self.active_menu.update_ui(self.mouse_position, curr_time_ns)

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

        self.active_menu.draw(qp)

        if DEBUG_MODE:
            qp.setFont(QFont("sans serif", 12))
            qp.setPen(Qt.red)
            qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()
