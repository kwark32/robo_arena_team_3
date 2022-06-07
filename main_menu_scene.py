import time

from PyQt5.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from util import Vector, get_main_path, ns_to_s, is_point_inside_rect
from constants import DEBUG_MODE, Scene


button_texture_path = get_main_path() + "/textures/ui/main_menu_buttons/"


# base class
class Button:
    def __init__(self, main_widget, position):
        self.button_type = type(self)
        if self.button_type is Button:
            print("ERROR: Button base class should not be instantiated!")

        self.main_widget = main_widget

        self.position = position
        self._texture = None
        self._texture_size = None

        self.is_selected = False

        self._top_left_corner = None
        self._bottom_right_corner = None

    @property
    def texture(self):
        if self._texture is None:
            self.load_image()
        return self._texture

    @property
    def texture_size(self):
        if self._texture_size is None:
            self.load_image()
        return self._texture_size

    @property
    def top_left_corner(self):
        if self._top_left_corner is None:
            half_texture_size = self.texture_size.copy()
            half_texture_size.div(2)
            self._top_left_corner = self.position.copy()
            self._top_left_corner.sub(half_texture_size)
            self._top_left_corner.round()
        return self._top_left_corner

    @property
    def bottom_right_corner(self):
        if self._bottom_right_corner is None:
            half_texture_size = self.texture_size.copy()
            half_texture_size.div(2)
            self._bottom_right_corner = self.position.copy()
            self._bottom_right_corner.add(half_texture_size)
            self._bottom_right_corner.round()
        return self._bottom_right_corner

    def load_image(self):
        filename = button_texture_path + self.button_type.name + ".png"
        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.name
                  + " has 0 size or is missing at " + filename + "!")

    def draw(self, qp):
        if self.is_selected:
            qp.fillRect(self.top_left_corner.x, self.top_left_corner.y,
                        self.texture_size.x, self.texture_size.y, QColor(80, 80, 80))

        qp.drawPixmap(self.top_left_corner.x, self.top_left_corner.y, self.texture)

    def click(self):
        pass


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
        self.main_widget.switch_scene(Scene.ONLINE_WORLD)


class MainMenuScene(QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.parent = parent

        self.size = size

        self.buttons = []
        self.selected_button = None
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

        self.buttons.append(ExitButton(self.parentWidget(), Vector(self.size / 2, 800)))
        self.buttons.append(SingleplayerButton(self.parentWidget(), Vector(self.size / 2, 350)))
        self.buttons.append(LocalMultiplayerButton(self.parentWidget(), Vector(self.size / 2, 500)))
        self.buttons.append(OnlineMultiplayerButton(self.parentWidget(), Vector(self.size / 2, 600)))

        self.show()

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

    def update_ui(self):
        curr_time_ns = time.time_ns()
        # delta_time = ns_to_s(curr_time_ns - self._last_frame_time_ns)
        self._last_frame_time_ns = curr_time_ns

        self.selected_button = None
        for button in self.buttons:
            if is_point_inside_rect(self.mouse_position, button.top_left_corner, button.bottom_right_corner):
                button.is_selected = True
                self.selected_button = button
            else:
                button.is_selected = False

        if self.is_clicking:
            self.is_clicking = False
            if self.selected_button is not None:
                self.selected_button.click()

        if DEBUG_MODE:
            self._frames_since_last_show += 1
            last_fps_show_delta = ns_to_s(curr_time_ns - self._last_fps_show_time)
            if last_fps_show_delta > 0.5:
                self.fps = self._frames_since_last_show / last_fps_show_delta
                self._frames_since_last_show = 0
                self._last_fps_show_time = curr_time_ns

    def paintEvent(self, event):
        self.update_ui()

        qp = QPainter(self)
        qp.setFont(QFont("sans serif", 12))
        qp.setPen(Qt.red)

        qp.fillRect(0, 0, self.size, self.size, QColor(50, 50, 50))

        qp.setFont(QFont("sans serif", 85))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(210, 210), "Robo Arena")
        # draw static menu background
        # qp.drawPixmap(QPoint(), <menu background pixmap>)

        for button in self.buttons:
            button.draw(qp)

        if DEBUG_MODE:
            qp.setFont(QFont("sans serif", 12))
            qp.setPen(Qt.red)
            qp.drawText(QPoint(5, 20), str(round(self.fps)))

        qp.end()
