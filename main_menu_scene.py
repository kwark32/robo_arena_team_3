from ui_elements import Button, Menu, TextField, UIImage, Slider, Checkbox
from util import Vector, ns_to_s
from globals import GameInfo, Scene, Menus, Fonts, Settings
from camera import CameraState
from constants import DEBUG_MODE, MAX_PLAYER_NAME_LENGTH, MAX_SERVER_IP_LENGTH
from sound_manager import SoundManager, music_names
from ui_overlay import OverlayWidget

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPainter
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt, QPoint


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
            self.menu.main_menu_scene.switch_menu("online_options")

    class SettingsButton(Button):
        name = "settings"

        def click(self):
            self.menu.main_menu_scene.switch_menu("settings")

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
            self.menu.main_menu_scene.switch_menu("main_menu")

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

            if Settings.instance.player_name != "":
                self.text = Settings.instance.player_name

        def add_character(self, character, use_shift=True):
            super().add_character(character, use_shift=use_shift)

            Settings.instance.player_name = self.text
            Settings.instance.save()

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

            if Settings.instance.ip_address != "":
                self.text = Settings.instance.ip_address

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
                ret = super().add_character(character, use_shift=False)

                Settings.instance.ip_address = self.text
                Settings.instance.save()

                return ret

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
        self.main_menu_scene.switch_menu("main_menu")


class SettingsMenu(Menu):
    class BackButton(Button):
        name = "back"

        def click(self):
            self.menu.main_menu_scene.switch_menu("main_menu")

    class FullscreenCheckbox(Checkbox):
        name = "fullscreen"
        header_text = "Fullscreen"
        left_align = False

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.checked = Settings.instance.fullscreen

        def click(self):
            super().click()

            Settings.instance.fullscreen = self.checked
            Settings.instance.save()

            self.main_widget.update_fullscreen()

    class MasterVolumeSlider(Slider):
        name = "master_volume"
        header_text = "Master Volume"
        min_value = 0
        max_value = 1
        snap_step = 0.01
        snap = True

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.value = Settings.instance.master_volume

        def value_changed(self):
            Settings.instance.master_volume = self.value
            Settings.instance.save()

    class SFXVolumeSlider(Slider):
        name = "sfx_volume"
        header_text = "SFX Volume"
        min_value = 0
        max_value = 1
        snap_step = 0.01
        snap = True

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.value = Settings.instance.sfx_volume

        def value_changed(self):
            Settings.instance.sfx_volume = self.value
            Settings.instance.save()

    class MusicVolumeSlider(Slider):
        name = "music_volume"
        header_text = "Music Volume"
        min_value = 0
        max_value = 1
        snap_step = 0.01
        snap = True

        def __init__(self, main_widget, position, menu):
            super().__init__(main_widget, position, menu)

            self.value = Settings.instance.music_volume

        def value_changed(self):
            Settings.instance.music_volume = self.value
            Settings.instance.save()

    def __init__(self, main_widget, size, main_menu_scene):
        super().__init__(main_widget, size, main_menu_scene, "black_bg")

        self.elements.append(SettingsMenu.FullscreenCheckbox(main_widget,
                                                             Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                    GameInfo.window_size.y / 2
                                                                    / CameraState.scale.y - 335), self))

        self.elements.append(SettingsMenu.MasterVolumeSlider(main_widget,
                                                             Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                    GameInfo.window_size.y / 2
                                                                    / CameraState.scale.y - 185), self))
        self.elements.append(SettingsMenu.SFXVolumeSlider(main_widget,
                                                          Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                 GameInfo.window_size.y / 2
                                                                 / CameraState.scale.y - 35), self))
        self.elements.append(SettingsMenu.MusicVolumeSlider(main_widget,
                                                            Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                                   GameInfo.window_size.y / 2
                                                                   / CameraState.scale.y + 115), self))
        self.elements.append(SettingsMenu.BackButton(main_widget,
                                                     Vector(GameInfo.window_size.x / 2 / CameraState.scale.x,
                                                            GameInfo.window_size.y / 2
                                                            / CameraState.scale.y + 425), self))

    def escape_pressed(self):
        self.main_menu_scene.switch_menu("main_menu")


Menus.menus["main_menu"] = MainMenu
Menus.menus["online_options"] = OnlineOptions
Menus.menus["settings"] = SettingsMenu


class MainMenuScene(OverlayWidget):
    def __init__(self, parent):
        super().__init__(parent)

        CameraState.position = None

        self.switch_menu("main_menu")

        SoundManager.instance.play_music(music_names[0], once=False)
        SoundManager.instance.play_random_music = False

    def paintEvent(self, event):
        # TODO: Look into why this strange fix is needed
        if not hasattr(self, "first") or self.first or not self.main_widget.running:
            self.first = False
            return

        qp = QPainter(self)
        qp.scale(CameraState.scale_factor, CameraState.scale_factor)
        qp.setRenderHint(QPainter.Antialiasing)

        super().draw(qp)

        SoundManager.instance.update_sound()

        if DEBUG_MODE:
            self._frames_since_last_show += 1
            last_fps_show_delta = ns_to_s(self.curr_time_ns - self._last_fps_show_time)
            if last_fps_show_delta > 0.5:
                self.fps = self._frames_since_last_show / last_fps_show_delta
                self._frames_since_last_show = 0
                self._last_fps_show_time = self.curr_time_ns
            qp.setFont(Fonts.fps_font)
            qp.setPen(Fonts.fps_color)
            qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()
