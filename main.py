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
        self.robot = None

        self.player_input = None

        self.init_arena()
        self.init_robots()

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)
        self.setWindowTitle("Robo Arena")
        self.show()

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def keyPressEvent(self, event):
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
        self.robot = Robot(position=Vector(500, 500))
        self.player_input = self.robot.input

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.size().width() > 1 and self.size().height() > 1:
            self.arena.draw(qp)
            self.robot.draw(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.show()  # get rid of var not used flake8 error
    while window.running:  # main loop
        window.robot.update()
        window.update()
        app.processEvents()

    sys.exit(0)


if __name__ == '__main__':
    main()
