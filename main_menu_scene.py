import time

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
from PyQt5.QtCore import Qt, QPoint
from ui_elements import Button, Menu, TextField, UIImage
from util import Vector, ns_to_s
from globals import GameInfo, Scene, Menus, Fonts
from camera import CameraState
from constants import DEBUG_MODE, MAX_PLAYER_NAME_LENGTH, MAX_SERVER_IP_LENGTH


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

    class Logo(UIImage):
        name = "logo"

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene, "black_bg")

        self.elements.append(MainMenu.Logo(main_widget,
                                           Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                  GameInfo.window_size.y / 2
                                                  / CameraState.scale.y - 430), self))

        self.elements.append(MainMenu.SingleplayerButton(main_widget,
                                                         Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                GameInfo.window_size.y / 2
                                                                / CameraState.scale.y - 235), self))
        self.elements.append(MainMenu.OnlineMultiplayerButton(main_widget,
                                                              Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                     GameInfo.window_size.y / 2
                                                                     / CameraState.scale.y - 70), self))
        self.elements.append(MainMenu.LocalMultiplayerButton(main_widget,
                                                             Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                    GameInfo.window_size.y / 2
                                                                    / CameraState.scale.y + 95), self))

        self.elements.append(MainMenu.SettingsButton(main_widget,
                                                     Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                            GameInfo.window_size.y / 2
                                                            / CameraState.scale.y + 260), self))

        self.elements.append(MainMenu.ExitButton(main_widget,
                                                 Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                        GameInfo.window_size.y / 2
                                                        / CameraState.scale.y + 425), self))

    def escape_pressed(self):
        self.main_widget.running = False


class OnlineOptions(Menu):
    class BackButton(Button):
        name = "back"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    class PlayerNameHeader(UIImage):
        name = "player_name_header"

    class ServerIpHeader(UIImage):
        name = "server_ip_header"

    class PlayerNameField(TextField):
        name = "player_name"

        def __init__(self, main_widget, position, menu, max_text_length=-1):
            super().__init__(main_widget, position, menu,
                             text_offset=Vector(35, 90), max_text_length=MAX_PLAYER_NAME_LENGTH)

            self.placeholder_text = GameInfo.placeholder_name
            if GameInfo.local_player_name != GameInfo.placeholder_name:
                self.text = GameInfo.local_player_name

    class ServerIPField(TextField):
        name = "server_ip"

        def __init__(self, main_widget, position, menu, max_text_length=-1):
            super().__init__(main_widget, position, menu,
                             text_offset=Vector(35, 90), max_text_length=MAX_SERVER_IP_LENGTH)

            self.placeholder_text = GameInfo.default_ip
            if GameInfo.server_ip != GameInfo.default_ip:
                self.text = GameInfo.server_ip

            self.dot_count = 0
            self.number_counts = [0, 0, 0, 0]

        def key_press(self, key):
            character = chr(0)
            if int(key) < 256:
                character = chr(int(key))
            elif key == Qt.Key_Backspace:
                character = chr(8)

            pasted_text = None
            if character == 'V' and self.menu.ctrl_key_pressed:
                pasted_text = QApplication.clipboard().text()

            if pasted_text is not None:
                for c in pasted_text:
                    if not self.add_character(c):
                        break
            else:
                self.add_character(character)

        def add_character(self, character, use_shift=False):
            valid_input = True
            if character == chr(8):
                if len(self.text) > 0:
                    last = self.text[-1]
                    if last == '.':
                        self.dot_count -= 1
                    elif ord('0') <= ord(last) <= ord('9'):
                        self.number_counts[self.dot_count] -= 1

            elif character == '.' and self.dot_count < 3 and self.number_counts[self.dot_count] > 0:
                self.dot_count += 1

            elif ('0' <= character <= '9'
                  and self.number_counts[self.dot_count] < 3
                  and (self.number_counts[self.dot_count] == 0
                       or int(self.text[-self.number_counts[self.dot_count]:]) * 10
                       + ord(character) - ord('0') <= 255)):
                self.number_counts[self.dot_count] += 1

            else:
                valid_input = False

            if valid_input:
                return super().add_character(character, use_shift=False)

            return False

    class JoinButton(Button):
        name = "join"

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.player_name_field = None
            self.server_ip_field = None

        def click(self):
            if self.player_name_field is not None and len(self.player_name_field.text) > 0:
                GameInfo.local_player_name = self.player_name_field.text
            else:
                GameInfo.local_player_name = GameInfo.placeholder_name

            if self.server_ip_field is not None and len(self.server_ip_field.text) > 0:
                GameInfo.server_ip = self.server_ip_field.text
            else:
                GameInfo.server_ip = GameInfo.default_ip

            self.main_widget.switch_scene(Scene.ONLINE_WORLD)

    class HostButton(Button):
        name = "host"

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.player_name_field = None
            self.server_ip_field = None

        def click(self):
            if self.player_name_field is not None and len(self.player_name_field.text) > 0:
                GameInfo.local_player_name = self.player_name_field.text
            else:
                GameInfo.local_player_name = GameInfo.placeholder_name

            if self.server_ip_field is not None and len(self.server_ip_field.text) > 0:
                GameInfo.server_ip = self.server_ip_field.text
            else:
                GameInfo.server_ip = GameInfo.default_ip

            self.main_widget.switch_scene(Scene.SERVER_WORLD)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene, "black_bg")

        self.elements.append(OnlineOptions.PlayerNameHeader(main_widget,
                                                            Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                   GameInfo.window_size.y / 2
                                                                   / CameraState.scale.y - 385), self))
        player_name_field = OnlineOptions.PlayerNameField(main_widget,
                                                          Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                 GameInfo.window_size.y / 2
                                                                 / CameraState.scale.y - 235), self)
        self.elements.append(player_name_field)
        self.elements.append(OnlineOptions.ServerIpHeader(main_widget,
                                                          Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                 GameInfo.window_size.y / 2
                                                                 / CameraState.scale.y - 55), self))
        server_ip_field = OnlineOptions.ServerIPField(main_widget,
                                                      Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                             GameInfo.window_size.y / 2
                                                             / CameraState.scale.y + 95), self)
        self.elements.append(server_ip_field)

        join_button = OnlineOptions.JoinButton(main_widget,
                                               Vector(GameInfo.window_size.x / 2 / CameraState.scale.x - 220,
                                                      GameInfo.window_size.y / 2
                                                      / CameraState.scale.y + 260), self)
        join_button.player_name_field = player_name_field
        join_button.server_ip_field = server_ip_field
        self.elements.append(join_button)

        host_button = OnlineOptions.HostButton(main_widget,
                                               Vector(GameInfo.window_size.x / 2 / CameraState.scale.x + 220,
                                                      GameInfo.window_size.y / 2
                                                      / CameraState.scale.y + 260), self)
        host_button.player_name_field = player_name_field
        host_button.server_ip_field = server_ip_field
        self.elements.append(host_button)

        self.elements.append(OnlineOptions.BackButton(main_widget,
                                                      Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                             GameInfo.window_size.y / 2
                                                             / CameraState.scale.y + 425), self))

    def escape_pressed(self):
        self.main_menu_scene.switch_menu(Menus.MAIN_MENU)


class Settings(Menu):
    class BackButton(Button):
        name = "back"

        def click(self):
            self.menu.main_menu_scene.switch_menu(Menus.MAIN_MENU)

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene, "black_bg")

        self.elements.append(Settings.BackButton(main_widget,
                                                 Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                        GameInfo.window_size.y / 2 + 425), self))

    def escape_pressed(self):
        self.main_menu_scene.switch_menu(Menus.MAIN_MENU)


class MainMenuScene(QOpenGLWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.main_widget = self.parentWidget()

        self.parent = parent
        self.size = size

        self.mouse_position = Vector(0, 0)

        self.world_sim = None

        self._last_frame_time_ns = time.time_ns()
        self._frames_since_last_show = 0
        self._last_fps_show_time = time.time_ns()
        self.fps = 0

        self.active_menu = MainMenu(self.main_widget, self.size, self)
        self.is_clicking = False

        self.init_ui()

        self.first = True

    def init_ui(self):
        self.setGeometry(0, 0, self.size.x, self.size.y)
        self.setMouseTracking(True)
        self.show()

    def switch_menu(self, menu):
        self.active_menu = None
        if menu == Menus.MAIN_MENU:
            self.active_menu = MainMenu(self.main_widget, GameInfo.window_size, self)
        elif menu == Menus.ONLINE_OPTIONS:
            self.active_menu = OnlineOptions(self.main_widget, GameInfo.window_size, self)
        elif menu == Menus.SETTINGS:
            self.active_menu = Settings(self.main_widget, GameInfo.window_size, self)

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
        event.accept()

    def mousePressEvent(self, event):
        self.mouse_position.x = event.x() / CameraState.scale.x
        self.mouse_position.y = event.y() / CameraState.scale.y
        if event.button() == Qt.LeftButton:
            self.is_clicking = True

    def paintEvent(self, event):
        # TODO: Look into why this strange fix is needed
        if not hasattr(self, "first") or self.first or not self.main_widget.running:
            self.first = False
            return

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
        qp.scale(CameraState.scale_factor, CameraState.scale_factor)
        qp.setRenderHint(QPainter.Antialiasing)

        self.active_menu.draw(qp)

        if DEBUG_MODE:
            qp.setFont(Fonts.fps_font)
            qp.setPen(Fonts.fps_color)
            qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()
