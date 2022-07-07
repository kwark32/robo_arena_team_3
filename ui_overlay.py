from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFontMetricsF
from util import get_main_path, Vector
from globals import Fonts
from constants import PLAYER_NAME_OFFSET, HEALTH_BAR_OFFSET


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
            if robot.player_name != "":
                text_width = self.name_tag_font_metrics.width(robot.player_name)
                pos_x = round(robot.extrapolation_body.position.x + PLAYER_NAME_OFFSET.x - (text_width / 2))
                pos_y = round(robot.extrapolation_body.position.y + PLAYER_NAME_OFFSET.y)
                qp.drawText(pos_x, pos_y, robot.player_name)

    def draw_health_bar(self, qp, robot):
        health_fill = round((robot.health / robot.max_health) * self.health_bar_size.x)
        x_pos = round(robot.extrapolation_body.position.x + HEALTH_BAR_OFFSET.x - (self.health_bar_bg_size.x / 2))
        y_pos = round(robot.extrapolation_body.position.y + HEALTH_BAR_OFFSET.y - (self.health_bar_bg_size.y / 2))
        qp.drawPixmap(x_pos, y_pos, self.health_bar_bg)
        if health_fill > 0:
            qp.drawPixmap(x_pos, y_pos, self.health_bar, 0, 0, health_fill, 0)
