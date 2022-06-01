import sys

from PyQt5.QtWidgets import QWidget, QApplication
from enum import IntEnum
from scenes import WorldScene


# global constants
ARENA_SIZE = 1000


class Scene(IntEnum):
    WORLD = 0


class ArenaWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.running = True

        self.active_scene = None

        self.init_ui()

        self.switch_scene(Scene.WORLD)

    def init_ui(self):
        self.setGeometry(0, 0, ARENA_SIZE, ARENA_SIZE)

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def keyPressEvent(self, event):
        if self.active_scene is not None:
            self.active_scene.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.active_scene is not None:
            self.active_scene.keyReleaseEvent(event)

    def switch_scene(self, scene):
        if scene == Scene.WORLD:
            self.active_scene = WorldScene(self, ARENA_SIZE)


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
