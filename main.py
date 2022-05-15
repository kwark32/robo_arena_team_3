import sys

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from arena import Arena, Tile, TileTypes


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.arena = Arena()

        self.init_ui()
        self.init_arena()

    def init_ui(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)
        self.setWindowTitle("Robo Arena")
        self.show()

    def init_arena(self):
        tile_count = self.arena.tile_count
        for i in range(tile_count):
            for j in range(tile_count):
                self.arena.tiles[i][j] = Tile(TileTypes.WALL_TILE)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.size().height() > 1 and self.size().height() > 1:
            self.arena.draw(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    window.setWindowTitle("Robo Arena")  # get rid of var not used flake8 error
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
