from PyQt5.QtGui import QPixmap, QColor
from util import Vector, get_main_path, is_point_inside_rect
from constants import Menu


button_texture_path = get_main_path() + "/textures/ui/main_menu_buttons/"


# absolute base class
class UIElement:
    def __init__(self, main_widget, position):
        self.element_type = None
        if isinstance(self, Button):
            self.element_type = Button

        self.main_widget = main_widget
        self.position = position

        self.is_selected = False

        self._top_left_corner = Vector(0, 0)
        self._bottom_right_corner = Vector(0, 0)

    @property
    def top_left_corner(self):
        return self._top_left_corner

    @property
    def bottom_right_corner(self):
        return self._bottom_right_corner

    def draw(self, qp):
        pass

    def click(self):
        pass


# base class
class Button(UIElement):
    def __init__(self, main_widget, position):
        super().__init__(main_widget, position)

        self.button_type = type(self)
        if self.button_type is Button:
            print("ERROR: Button base class should not be instantiated!")

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


class Menu:
    def __init__(self, main_widget, size, main_menu_scene):
        self.main_widget = main_widget
        self.size = size
        self.main_menu_scene = main_menu_scene

        self.selected_element = None

        self.elements = []

    def click_element(self):
        if self.selected_element is not None:
            self.selected_element.click()

    def update_ui(self, mouse_pos):
        self.selected_element = None
        for element in self.elements:
            if is_point_inside_rect(mouse_pos, element.top_left_corner, element.bottom_right_corner):
                element.is_selected = True
                self.selected_element = element
            else:
                element.is_selected = False

    def draw(self, qp):
        for element in self.elements:
            element.draw(qp)
