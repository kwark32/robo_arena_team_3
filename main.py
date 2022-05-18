import math
import sys

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt
from arena import Arena, Tile, TileTypes
from robot import Robot
from util import Vector
from json_interface import load_map


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.running = True

        self.arena = None
        self.robot = None

        self.initUI()
        self.init_arena()
        self.init_robots()

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.robot.velocity.y = -self.robot.move_speed
        elif event.key() == Qt.Key_S:
            self.robot.velocity.y = self.robot.move_speed
        elif event.key() == Qt.Key_D:
            self.robot.velocity.x = self.robot.move_speed
        elif event.key() == Qt.Key_A:
            self.robot.velocity.x = -self.robot.move_speed
        event.accept()
        if math.fabs(self.robot.velocity.x) > 0\
                or math.fabs(self.robot.velocity.y) > 0:
            self.robot.rotation = math.atan2(self.robot.velocity.x,
                                             -self.robot.velocity.y)
        else:
            self.robot.rotation = 0

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.robot.velocity.y = 0
        elif event.key() == Qt.Key_S:
            self.robot.velocity.y = 0
        elif event.key() == Qt.Key_D:
            self.robot.velocity.x = 0
        elif event.key() == Qt.Key_A:
            self.robot.velocity.x = 0
        event.accept()
        if math.fabs(self.robot.velocity.x) > 0\
                or math.fabs(self.robot.velocity.y) > 0:
            self.robot.rotation = math.atan2(self.robot.velocity.x,
                                             -self.robot.velocity.y)
        else:
            self.robot.rotation = 0

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)
        self.setWindowTitle("Robo Arena")
        self.show()

    def init_arena(self):
        self.arena = Arena()
        tile_count = self.arena.tile_count
        for i in range(tile_count):
            for j in range(tile_count):
                self.arena.tiles[i][j] = Tile(TileTypes.WALL_TILE)
        for i in range(1, self.arena.tile_count - 1):
            for j in range(1, self.arena.tile_count - 1):
                self.arena.tiles[i][j] = Tile(TileTypes.GROUND_TILE)
        for i in range(5, 10):
            for j in range(10, 20):
                self.arena.tiles[i][j] = Tile(TileTypes.WATER_TILE)
        for i in range(15, 20):
            for j in range(10, 20):
                self.arena.tiles[i][j] = Tile(TileTypes.FIRE_TILE)
        for i in range(25, 30):
            for j in range(10, 20):
                self.arena.tiles[i][j] = Tile(TileTypes.EARTH_TILE)
        for i in range(35, 40):
            for j in range(10, 20):
                self.arena.tiles[i][j] = Tile(TileTypes.AIR_TILE)
        for i in range(45, 50):
            for j in range(10, 20):
                self.arena.tiles[i][j] = Tile(TileTypes.PORTAL_TILE)

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
    load_map("./test_map.json")

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
