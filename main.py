import math
import sys

from os.path import dirname, abspath
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from robot import Robot
from util import Vector
from json_interface import load_map


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.running = True

        self.arena = None
        self.robot = None

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
            self.robot.accel.y = -self.robot.max_accel
        elif event.key() == Qt.Key_S:
            self.robot.accel.y = self.robot.max_accel
        elif event.key() == Qt.Key_D:
            self.robot.accel.x = self.robot.max_accel
        elif event.key() == Qt.Key_A:
            self.robot.accel.x = -self.robot.max_accel
        event.accept()
        self.robot.ang_accel = 0
        self.robot.ang_velocity = 0
        if math.fabs(self.robot.velocity.x) > 0\
                or math.fabs(self.robot.velocity.y) > 0:
            self.robot.rotation = math.atan2(self.robot.velocity.x,
                                             -self.robot.velocity.y)
        else:
            self.robot.rotation = 0

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.robot.accel.y = 0
        elif event.key() == Qt.Key_S:
            self.robot.accel.y = 0
        elif event.key() == Qt.Key_D:
            self.robot.accel.x = 0
        elif event.key() == Qt.Key_A:
            self.robot.accel.x = 0
        event.accept()
        if math.fabs(self.robot.velocity.x) > 0\
                or math.fabs(self.robot.velocity.y) > 0:
            self.robot.rotation = math.atan2(self.robot.velocity.x,
                                             -self.robot.velocity.y)
        else:
            self.robot.rotation = 0

    def init_arena(self):
        map_path = dirname(abspath(__file__))
        map_path += "/test_map.json"
        self.arena = load_map(map_path)

    def init_robots(self):
        self.robot = Robot(position=Vector(500, 500))

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
