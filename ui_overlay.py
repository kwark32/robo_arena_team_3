from util import get_main_path, Vector, painter_transform_with_rot, is_object_on_screen
from globals import Fonts, GameInfo
from constants import PLAYER_NAME_OFFSET, HEALTH_BAR_OFFSET

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtGui import QFontMetricsF


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
            if robot.is_dead:
                continue
            if robot.player_name != "":
                text_width = self.name_tag_font_metrics.width(robot.player_name)
                pos = Vector(0, 0)
                pos.x = round(robot.extrapolation_body.position.x + PLAYER_NAME_OFFSET.x)
                pos.y = round(robot.extrapolation_body.position.y + PLAYER_NAME_OFFSET.y)
                if is_object_on_screen(pos, radius=120):
                    painter_transform_with_rot(qp, pos, 0)
                    qp.drawText(round(-text_width / 2), 0, robot.player_name)
                    qp.restore()

    def draw_health_bar(self, qp, robot):
        health_fill = round((robot.health / robot.max_health) * self.health_bar_size.x)
        pos = Vector(0, 0)
        pos.x = round(robot.extrapolation_body.position.x + HEALTH_BAR_OFFSET.x)
        pos.y = round(robot.extrapolation_body.position.y + HEALTH_BAR_OFFSET.y)
        if is_object_on_screen(pos):
            painter_transform_with_rot(qp, pos, 0)
            qp.drawPixmap(round(-self.health_bar_bg_size.x / 2), round(-self.health_bar_bg_size.y / 2),
                          self.health_bar_bg)
            if health_fill > 0:
                qp.drawPixmap(round(-self.health_bar_bg_size.x / 2), round(-self.health_bar_bg_size.y / 2),
                              self.health_bar, 0, 0, health_fill, 0)
            qp.restore()
