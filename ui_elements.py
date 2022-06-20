import time

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPixmap, QColor, QFont
from util import Vector, get_main_path, is_point_inside_rect
from constants import CARET_BLINK_RATE_NS


ui_element_texture_path = get_main_path() + "/textures/ui/main_menu/"


# absolute base class
class UIElement:
    def __init__(self, main_widget, position, menu):
        self.element_class = type(self)

        self.element_type = UIElement
        if isinstance(self, Button):
            self.element_type = Button
        if isinstance(self, TextField):
            self.element_type = TextField

        self.main_widget = main_widget
        self.position = position.copy()
        self.menu = menu

        self.is_selected = False

        self._top_left_corner = None
        self._bottom_right_corner = None

        self._texture = None
        self._texture_size = None

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
        filename = ui_element_texture_path + self.element_class.name + ".png"
        self._texture = QPixmap(filename)
        self._texture_size = Vector(self._texture.width(), self._texture.height())
        if self._texture_size.x == 0 or self._texture_size.y == 0:
            print("ERROR: texture for " + self.element_class.name
                  + " has 0 size or is missing at " + filename + "!")

    def draw(self, qp):
        if self.is_selected:
            qp.fillRect(self.top_left_corner.x, self.top_left_corner.y,
                        self.texture_size.x, self.texture_size.y, QColor(80, 80, 80))

        qp.drawPixmap(self.top_left_corner.x, self.top_left_corner.y, self.texture)

    def update_selected(self, curr_time_ns):
        self.is_selected = True

    def unselect(self):
        self.is_selected = False

    def click(self):
        pass

    def key_press(self, key):
        return False


# base class
class TextField(UIElement):
    def __init__(self, main_widget, position, menu, text_offset=Vector(0, 0), max_text_length=-1):
        super().__init__(main_widget, position, menu)

        self.text_field_type = type(self)
        if self.text_field_type is TextField:
            print("ERROR: TextField base class should not be instantiated!")

        self.text_offset = text_offset.copy()
        self.max_text_length = max_text_length

        self.caret = 0

        self.last_caret_switch_time = 0

        self.text = ""

    def draw(self, qp):
        super().draw(qp)

        qp.setFont(QFont("sans serif", 25))
        qp.setPen(Qt.darkCyan)
        qp.drawText(QPoint(self.top_left_corner.x + self.text_offset.x,
                           self.top_left_corner.y + self.text_offset.y), self.text)

    def key_press(self, key):
        keycode = int(key)
        if 0 <= self.max_text_length <= (len(self.text) - self.caret) and not key == Qt.Key_Backspace:
            print("WARN: Max text length for this TextField is " + str(self.max_text_length) + "!")
            return True

        caret = self.caret != 0
        if caret:
            self.remove_caret()

        if (keycode == 32 or keycode == 45 or 48 <= keycode <= 57
                or 65 <= keycode <= 90 or keycode == 95):
            new_char = chr(keycode)
            if not self.menu.shift_key_pressed:
                new_char = new_char.lower()
            self.text += new_char
            self.set_caret(True)
        elif key == Qt.Key_Backspace:
            self.text = self.text[:-1]
            self.set_caret(True)

        if caret:
            self.add_caret()

        return True

    def update_selected(self, curr_time_ns):
        super().update_selected(curr_time_ns)

        if curr_time_ns >= self.last_caret_switch_time + CARET_BLINK_RATE_NS:
            self.set_caret(self.caret == 0)

    def unselect(self):
        super().unselect()

        self.set_caret(False)

    def set_caret(self, value):
        change = value != (self.caret != 0)
        if value:
            self.caret = 1
            if change:
                self.add_caret()
        else:
            self.caret = 0
            if change:
                self.remove_caret()

        self.last_caret_switch_time = time.time_ns()

    def add_caret(self):
        self.text += "|"

    def remove_caret(self):
        self.text = self.text[:-1]


# base class
class Button(UIElement):
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.button_type = type(self)
        if self.button_type is Button:
            print("ERROR: Button base class should not be instantiated!")


class Menu:
    def __init__(self, main_widget, size, main_menu_scene):
        self.main_widget = main_widget
        self.size = size
        self.main_menu_scene = main_menu_scene

        self.elements = []
        self.selected_element = None

        self.bg_pixmap = None

        self.shift_key_pressed = False

    def click_element(self):
        if self.selected_element is not None:
            self.selected_element.click()

    def key_press_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.escape_pressed()
            event.accept()
        elif event.key() == Qt.Key_Shift:
            self.shift_key_pressed = True
        elif self.selected_element is not None:
            if not self.selected_element.key_press(event.key()):
                return
        else:
            return
        event.accept()

    def key_release_event(self, event):
        if event.key() == Qt.Key_Shift:
            self.shift_key_pressed = False
        else:
            return
        event.accept()

    def escape_pressed(self):
        pass

    def update_ui(self, mouse_pos, curr_time_ns):
        self.selected_element = None
        for element in self.elements:
            if is_point_inside_rect(mouse_pos, element.top_left_corner, element.bottom_right_corner):
                element.update_selected(curr_time_ns)
                self.selected_element = element
            elif element.is_selected:
                element.unselect()

    def draw(self, qp):
        # draw static menu background
        if self.bg_pixmap is not None:
            qp.drawPixmap(QPoint(), self.bg_pixmap)

        for element in self.elements:
            element.draw(qp)
