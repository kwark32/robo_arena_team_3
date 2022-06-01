import sys

from PyQt5.QtWidgets import QWidget, QApplication


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.running = True

        self.active_scene = None

        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, self.arena.size, self.arena.size)

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def paintEvent(self, event):
        if self.active_scene is not None:
            self.active_scene.paintEvent(event)


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
