import sys

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from arena import Arena, Tile, TileTypes
from robot import Robot
from util import Vector


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.arena = Arena()

        self.robot = None

        self.initUI()
        self.init_arena()
        self.init_robots()

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)
        self.setWindowTitle("Robo Arena")
        self.show()

    def init_arena(self):
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
        self.robot.velocity.x = 10.0
        print(self.robot.position.x)
        print("\n")

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.size().height() > 1 and self.size().height() > 1:
            self.arena.draw(qp)
            self.robot.update()
            self.robot.draw(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.show()  # get rid of var not used flake8 error
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
