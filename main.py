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
        self.robots = []                                # changed robot to robots

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
        if self.player_input is None:                   # added condition so stuff is only done when there is an input
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
        if self.player_input is None:                   # added condition so stuff is only done when there is an input
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
        map_path = dirname(abspath(__file__))
        map_path += "/test_map.json"
        self.arena = load_map(map_path)

    def init_robots(self):
        self.robots.append(Robot(is_player=True, position=Vector(500, 500)))        # set is_player to True, made robots a list
        self.robots.append(Robot(is_player=True, position=Vector(250, 250)))        # instanciating more robots
        self.robots.append(Robot(is_player=True, position=Vector(250, 750)))
        self.robots.append(Robot(is_player=True, position=Vector(750, 250)))
        self.robots.append(Robot(is_player=True, position=Vector(750, 750)))
        self.player_input = self.robots[0].input                                    # for now all robots are players
        self.robots[1].input = self.player_input
        self.robots[2].input = self.player_input
        self.robots[3].input = self.player_input
        self.robots[4].input = self.player_input

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        for robot in self.robots:                   # update now for all robots
            robot.update()
        if self.size().width() > 1 and self.size().height() > 1:
            self.arena.draw(qp)
            for robot in self.robots:                   # draw now for all robots
                robot.draw(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.show()  # get rid of var not used flake8 error
    while window.running:  # main loop
                                                # deleted window.robot.update()
        window.update()
        app.processEvents()

    sys.exit(0)


if __name__ == '__main__':
    main()
