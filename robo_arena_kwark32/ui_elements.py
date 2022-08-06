import math

import pixmap_resource_manager as prm

from os import path
from util import Vector, is_point_inside_rect, rad_to_deg, limit
from globals import Fonts, GameInfo
from constants import CARET_BLINK_RATE_NS
from camera import CameraState

if not GameInfo.is_headless:
    from PyQt5.QtCore import QPoint, Qt
    from PyQt5.QtGui import QFontMetricsF, QPen
    from PyQt5.QtWidgets import QApplication


ui_element_texture_path = path.join("textures", "ui", "menu")


# absolute base class
class UIElement:
    """Base class for UI elements, includes transform, texture & input handling."""
    selected_edge_top_right = None

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
            UIElement.selected_edge_top_right, selected_edge_size = self.load_image("selected_edge_top_right")

        self.main_widget = main_widget
        self.position = position.copy()
        self.menu = menu

        self.is_selected = False
        self.is_selectable = True
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
            filename = path.join(ui_element_texture_path, self.element_class.name)
        else:
            filename = path.join(ui_element_texture_path, name)
        texture = prm.get_pixmap(filename)
        size = Vector(texture.width(), texture.height())
        if size.x == 0 or size.y == 0:
            print("ERROR: texture for " + self.element_class.name
                  + " has 0 size or is missing at " + filename + ".png!")
        if name is None:
            self._texture = texture
            self._texture_size = size
        return texture, size

    def draw(self, qp):
        """Draws the element with selection brackets if selected & should draw selection."""
        if self.is_selected and self.draw_selected:
            edge_offset = Vector(-15, 15)
            pos_rots = [(Vector(self.bottom_right_corner.x, self.top_left_corner.y), 0),
                        (Vector(self.bottom_right_corner.x, self.bottom_right_corner.y), math.pi / 2),
                        (Vector(self.top_left_corner.x, self.bottom_right_corner.y), math.pi),
                        (Vector(self.top_left_corner.x, self.top_left_corner.y), -math.pi / 2)]
            edge_image = UIElement.selected_edge_top_right
            edge_size = Vector(edge_image.width(), edge_image.height())

            for pos, rot in pos_rots:
                qp.save()
                pos.add(edge_offset)
                qp.translate(pos.x + CameraState.x_offset, pos.y)
                qp.rotate(rad_to_deg(rot))
                qp.drawPixmap(round(-edge_size.x / 2),
                              round(-edge_size.y / 2), edge_image)
                edge_offset.rotate(math.pi / 2)
                qp.restore()

        qp.drawPixmap(round(self.top_left_corner.x + CameraState.x_offset), round(self.top_left_corner.y), self.texture)

    def mouse_drag(self, position):
        pass

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
class Slider(UIElement):
    """Shows a header text & slider that can be dragged with the mouse dynamically."""
    header_offset_y = -30
    image_border = 10

    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.slider_type = type(self)
        if self.slider_type is Slider:
            print("ERROR: Slider base class should not be instantiated!")

        self.header_text = self.slider_type.header_text
        self.min_value = self.slider_type.min_value
        self.max_value = self.slider_type.max_value
        self.snap_step = self.slider_type.snap_step
        self.snap = self.slider_type.snap

        self.value = self.min_value

        self.fill_texture = None
        self.fill_size = 0

        self.font_metrics = QFontMetricsF(Fonts.text_field_font)
        self.header_offset_x = -(self.font_metrics.width(self.slider_type.header_text) / 2)

    def draw(self, qp):
        qp.setFont(Fonts.text_field_font)
        qp.setPen(QPen(Fonts.text_field_color, 6))
        qp.drawText(QPoint(round(self.position.x + CameraState.x_offset + self.header_offset_x),
                           round(self.position.y + Slider.header_offset_y)), self.slider_type.header_text)

        qp.drawPixmap(round(self.top_left_corner.x + CameraState.x_offset), round(self.top_left_corner.y), self.texture)

        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        qp.drawPixmap(round(self.top_left_corner.x + CameraState.x_offset), round(self.top_left_corner.y),
                      self.fill_texture, 0, 0, round(percentage * self.fill_size + Slider.image_border), 0)

    def load_image(self, name=None):
        texture, size = super().load_image(name="slider_empty")
        self._texture = texture
        self._texture_size = size
        texture, size = super().load_image(name=(self.slider_type.name + "_fill"))
        self.fill_texture = texture
        self.fill_size = size.x - Slider.image_border * 2
        if not self._texture_size.equal(size):
            print("ERROR: Fill texture has different size as empty slider texture!")

    def mouse_drag(self, position):
        """Updates the slider while the mouse drags it."""
        pos_range = self.texture_size.x - Slider.image_border * 2
        pos_start = self.top_left_corner.x + Slider.image_border

        mouse_pos = round(position.x - pos_start)
        percentage = limit(mouse_pos, 0, pos_range) / pos_range

        self.value = percentage * (self.max_value - self.min_value) + self.min_value

        if self.snap:
            self.value = round(self.value / self.snap_step) * self.snap_step

        self.value_changed()

    def value_changed(self):
        pass


# base class
class TextField(UIElement):
    """Shows a text field that can be written into with keyboard input."""
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
            qp.drawText(QPoint(round(self.top_left_corner.x + CameraState.x_offset + self.text_offset.x),
                               round(self.top_left_corner.y + self.text_offset.y)), draw_text)
        else:
            qp.setPen(QPen(Fonts.text_field_default_color, 6))
            qp.drawText(QPoint(round(self.top_left_corner.x + CameraState.x_offset + self.text_offset.x),
                               round(self.top_left_corner.y + self.text_offset.y)), self.placeholder_text)

    def key_press(self, key):
        """Adds the pressed key's character to the current text if valid."""
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
                if not self.add_character(c, use_shift=False):
                    break
        else:
            self.add_character(character)
        
        return True

    def add_character(self, character, use_shift=True):
        """Adds the character (can change capital based on shift press) to the current text if valid."""
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
    """Implements just the click input."""
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.button_type = type(self)
        if self.button_type is Button:
            print("ERROR: Button base class should not be instantiated!")


# base class
class UIImage(UIElement):
    """Image element, ignoring all input & selection."""
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.is_selectable = False
        self.draw_selected = False


# base class
class UIText(UIElement):
    """Text element without image, ignoring all inputs & selection."""
    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.is_selectable = False
        self.draw_selected = False

        self.left_align = False

        self.font = Fonts.ui_text_font
        self.font_color = Fonts.text_field_color
        self.font_metrics = QFontMetricsF(self.font)

        self.text = ""

    def draw(self, qp):
        if self.left_align:
            text_width = 0
        else:
            text_width = self.font_metrics.width(self.text)

        qp.setFont(self.font)
        qp.setPen(QPen(self.font_color, 6))
        qp.drawText(round(self.position.x - (text_width / 2) + CameraState.x_offset), round(self.position.y), self.text)


# base class
class Checkbox(UIElement):
    """Checkbox element implementing a toggle on click with additional toggled filler texture."""
    header_offset_y = -60

    def __init__(self, main_widget, position, menu):
        super().__init__(main_widget, position, menu)

        self.checkbox_type = type(self)
        if self.checkbox_type is Checkbox:
            print("ERROR: Checkbox base class should not be instantiated!")

        self.draw_selected = False

        self.fill_texture = None

        self.font = Fonts.text_field_font
        self.font_color = Fonts.text_field_color
        self.font_metrics = QFontMetricsF(self.font)

        if self.checkbox_type.left_align:
            self.header_offset_x = 0
        else:
            self.header_offset_x = -(self.font_metrics.width(self.checkbox_type.header_text) / 2)

        self.checked = False

    def draw(self, qp):
        qp.setFont(self.font)
        qp.setPen(QPen(self.font_color, 6))
        qp.drawText(round(self.position.x + self.header_offset_x + CameraState.x_offset),
                    round(self.position.y + Checkbox.header_offset_y), self.checkbox_type.header_text)
        qp.drawPixmap(round(self.top_left_corner.x + CameraState.x_offset), round(self.top_left_corner.y), self.texture)
        if self.checked:
            qp.drawPixmap(round(self.top_left_corner.x + CameraState.x_offset),
                          round(self.top_left_corner.y), self.fill_texture)

    def load_image(self, name=None):
        self._texture, self._texture_size = super().load_image(name="checkbox")
        self.fill_texture, size = super().load_image(name="checkbox_fill")
        if not self._texture_size.equal(size):
            print("ERROR: Fill texture has different size as empty checkbox texture!")

    def click(self):
        self.checked = not self.checked


class Menu:
    """Base class for all menus containing UI elements, has interface to forward input and calculate selection."""
    def __init__(self, main_widget, size, main_menu_scene, bg_texture_name):
        self.main_widget = main_widget
        self.size = size.copy()
        self.main_menu_scene = main_menu_scene

        self.elements = []
        self.selected_element = None
        self.drag_element = None
        self.dragging = False

        self.bg_pixmap = None
        if bg_texture_name is not None:
            self.bg_pixmap = prm.get_pixmap(path.join(ui_element_texture_path, bg_texture_name))

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

    def mouse_drag(self, position):
        if self.drag_element is not None:
            self.drag_element.mouse_drag(position)

    def escape_pressed(self):
        pass

    def update_ui(self, mouse_pos, curr_time_ns):
        """Updates the current selection (if not currently dragging a slider)."""
        if not self.dragging:
            self.selected_element = None
            for element in self.elements:
                if element.is_selectable:
                    if is_point_inside_rect(mouse_pos, element.top_left_corner, element.bottom_right_corner):
                        element.update_selected(curr_time_ns)
                        self.selected_element = element
                    elif element.is_selected:
                        element.unselect()

    def draw(self, qp):
        """Draws the background and all UI elements."""
        # draw static menu background
        if self.bg_pixmap is not None:
            qp.save()
            qp.resetTransform()
            scale = CameraState.scale.x
            if CameraState.scale.x < CameraState.scale.y:
                scale = CameraState.scale.y
            qp.scale(scale, scale)
            qp.drawPixmap(QPoint(), self.bg_pixmap)
            qp.restore()

        for element in self.elements:
            element.draw(qp)
