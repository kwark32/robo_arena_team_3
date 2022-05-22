import sys

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from robot import Robot
from util import Vector, get_main_path
from json_interface import load_map
from arena import init_tile_dict


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        init_tile_dict()

        self.running = True

        self.arena = None
        self.robots = []

        self.player_input = None

        self.init_arena()
        self.init_robots()

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def keyPressEvent(self, event):
        if self.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.player_input.up = True
        elif event.key() == Qt.Key_S:
            self.player_input.down = True
        elif event.key() == Qt.Key_A:
            self.player_input.left = True
        elif event.key() == Qt.Key_D:
            self.player_input.right = True
        event.accept()

    def keyReleaseEvent(self, event):
        if self.player_input is None:
            return
        if event.key() == Qt.Key_W:
            self.player_input.up = False
        elif event.key() == Qt.Key_S:
            self.player_input.down = False
        elif event.key() == Qt.Key_A:
            self.player_input.left = False
        elif event.key() == Qt.Key_D:
            self.player_input.right = False
        event.accept()

    def init_arena(self):
        map_path = get_main_path() + "/test_map.json"
        self.arena = load_map(map_path)

    def init_robots(self):
        self.robots.append(Robot(is_player=True, position=Vector(500, 500)))
        self.robots.append(Robot(is_player=False, position=Vector(250, 250)))
        self.robots.append(Robot(is_player=False, position=Vector(250, 750)))
        self.robots.append(Robot(is_player=False, position=Vector(750, 250)))
        self.robots.append(Robot(is_player=False, position=Vector(750, 750)))
        self.player_input = self.robots[0].input

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        for robot in self.robots:
            robot.update()
        if self.size().width() > 1 and self.size().height() > 1:
            self.arena.draw(qp)
            for robot in self.robots:
                robot.draw(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.setWindowTitle("Robo Arena")
    window.show()
    while window.running:  # main loop
        window.update()
        app.processEvents()

    sys.exit(0)


if __name__ == '__main__':
    main()
