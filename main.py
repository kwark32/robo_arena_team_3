import sys

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication


class ArenaWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 1000, 1000)
        self.setWindowTitle('RoboArena')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        # self.drawPoints(qp)
        qp.end()


def main():
    app = QApplication(sys.argv)
    window = ArenaWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
