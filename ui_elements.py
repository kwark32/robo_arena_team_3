import math
import clipboard

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPixmap, QFontMetricsF, QPen
from util import Vector, get_main_path, is_point_inside_rect, draw_img_with_rot
from globals import Fonts
from constants import CARET_BLINK_RATE_NS


ui_element_texture_path = get_main_path() + "/textures/ui/main_menu/"


# absolute base class
class UIElement:
    selected_edge_top_right = None
    selected_edge_size = None

    def __init__(self, main_widget, position, menu):
        self.element_class = type(self)

        self.element_type = UIElement
        if isinstance(self, Button):
            self.element_type = Button
        if isinstance(self, TextField):
            self.element_type = TextField
        if isinstance(self, UIImage):
            self.element_type = UIImage

        if UIElement.selected_edge_top_right is None:
            UIElement.selected_edge_top_right, UIElement.selected_edge_size = self.load_image("selected_edge_top_right")

        self.main_widget = main_widget
        self.position = position.copy()
        self.menu = menu

        self.is_selected = False
        self.draw_selected = True

        self.update_time_ns = 0

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

    def load_image(self, name=None):
        if name is None:
            filename = ui_element_texture_path + self.element_class.name + ".png"
        else:
            filename = ui_element_texture_path + name + ".png"
        texture = QPixmap(filename)
        size = Vector(texture.width(), texture.height())
        if size.x == 0 or size.y == 0:
            print("ERROR: texture for " + self.element_class.name
                  + " has 0 size or is missing at " + filename + "!")
        if name is None:
            self._texture = texture
            self._texture_size = size
        return texture, size

    def draw(self, qp):
        if self.is_selected and self.draw_selected:
            edge_size = UIElement.selected_edge_size
            edge_offset = Vector(-15, 15)
            pos_rots = [(Vector(self.bottom_right_corner.x, self.top_left_corner.y), 0),
                        (Vector(self.bottom_right_corner.x, self.bottom_right_corner.y), math.pi / 2),
                        (Vector(self.top_left_corner.x, self.bottom_right_corner.y), math.pi),
                        (Vector(self.top_left_corner.x, self.top_left_corner.y), -math.pi / 2)]
            for pos, rot in pos_rots:
                pos.add(edge_offset)
                draw_img_with_rot(qp, UIElement.selected_edge_top_right, edge_size.x, edge_size.y, pos, rot)
                edge_offset.rotate(math.pi / 2)

        qp.drawPixmap(self.top_left_corner.x, self.top_left_corner.y, self.texture)

    def update_selected(self, curr_time_ns):
        self.is_selected = True
        self.update_time_ns = curr_time_ns

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

        self.font_metrics = QFontMetricsF(Fonts.text_field_font)

        self.text_offset = text_offset.copy()
        self.max_text_length = max_text_length

        self.caret = False

        self.last_caret_switch_time = 0

        self.text = ""
        self.placeholder_text = ""

    def draw(self, qp):
        super().draw(qp)

        draw_text = self.text
        if self.caret:
            draw_text += "|"

        qp.setFont(Fonts.text_field_font)

        if len(self.text) > 0 or self.is_selected:
            qp.setPen(QPen(Fonts.text_field_color, 6))
            qp.drawText(QPoint(self.top_left_corner.x + self.text_offset.x,
                               self.top_left_corner.y + self.text_offset.y), draw_text)
        else:
            qp.setPen(QPen(Fonts.text_field_default_color, 6))
            qp.drawText(QPoint(self.top_left_corner.x + self.text_offset.x,
                               self.top_left_corner.y + self.text_offset.y), self.placeholder_text)

    def key_press(self, key):
        character = chr(0)
        if int(key) < 256:
            character = chr(int(key))
        elif key == Qt.Key_Backspace:
            character = chr(8)

        pasted_text = None
        if character == 'V' and self.menu.ctrl_key_pressed:
            pasted_text = clipboard.paste()

        if pasted_text is not None:
            for c in pasted_text:
                if not self.add_character(c, use_shift=False):
                    break
        else:
            self.add_character(character)

        return True

    def add_character(self, character, use_shift=True):
        char = None
        if (character == ' ' or character == '-' or character == '.' or '0' <= character <= '9'
                or 'a' <= character.lower() <= 'z' or character == '_'):
            char = character
            if not self.menu.shift_key_pressed and use_shift:
                char = char.lower()

        backspace = (character == chr(8))

        if char is not None:
            if self.get_text_width(add_str=str(char)) <= self.max_text_length:
                self.text += char
            else:
                print("WARN: Max text width for this TextField is " + str(self.max_text_length)
                      + "px (would be " + str(self.get_text_width(add_str=str(char))) + ")!")
                return False

            self.set_caret(True)

        if backspace:
            if len(self.text) > 0:
                self.text = self.text[:-1]
            self.set_caret(True)

        return True

    def update_selected(self, curr_time_ns):
        super().update_selected(curr_time_ns)

        if self.update_time_ns >= self.last_caret_switch_time + CARET_BLINK_RATE_NS:
            self.set_caret(not self.caret)

    def unselect(self):
        super().unselect()

        self.set_caret(False)

    def set_caret(self, value):
        self.caret = value
        self.last_caret_switch_time = self.update_time_ns

    def get_text_width(self, add_str=""):
        return self.font_metrics.width(self.text + add_str)


# base class
class Button(UIElement):
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.button_type = type(self)
        if self.button_type is Button:
            print("ERROR: Button base class should not be instantiated!")


# base class
class UIImage(UIElement):
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.draw_selected = False


class Menu:
    def __init__(self, main_widget, size, main_menu_scene, bg_texture_name):
        self.main_widget = main_widget
        self.size = size.copy()
        self.main_menu_scene = main_menu_scene

        self.elements = []
        self.selected_element = None

        self.bg_pixmap = QPixmap(ui_element_texture_path + bg_texture_name + ".png")

        self.shift_key_pressed = False
        self.ctrl_key_pressed = False

    def click_element(self):
        if self.selected_element is not None:
            self.selected_element.click()

    def key_press_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.escape_pressed()
            event.accept()
        elif event.key() == Qt.Key_Shift:
            self.shift_key_pressed = True
        elif event.key() == Qt.Key_Control:
            self.ctrl_key_pressed = True
        elif self.selected_element is not None:
            if not self.selected_element.key_press(event.key()):
                return
        else:
            return
        event.accept()

    def key_release_event(self, event):
        if event.key() == Qt.Key_Shift:
            self.shift_key_pressed = False
        elif event.key() == Qt.Key_Control:
            self.ctrl_key_pressed = False
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
