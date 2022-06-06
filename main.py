import sys

from constants import GameInfo

headless_args = []
for arg in sys.argv:
    if arg == "--headless":
        headless_args.append(arg)
        GameInfo.is_headless = True
for arg in headless_args:
    sys.argv.remove(arg)
headless_args.clear()

if not GameInfo.is_headless:
    from constants import Scene, WINDOW_SIZE
    from world_sim import WorldSim
    from main_menu_scene import MainMenuScene
    from world_scene import WorldScene
    from PyQt5.QtWidgets import QWidget, QApplication

    class ArenaWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.running = True

            self.active_scene = None

            self.init_ui()

            self.switch_scene(Scene.MAIN_MENU)

        def init_ui(self):
            self.setGeometry(0, 0, WINDOW_SIZE, WINDOW_SIZE)

        def closeEvent(self, event):
            self.running = False
            event.accept()

        def keyPressEvent(self, event):
            if self.active_scene is not None:
                self.active_scene.keyPressEvent(event)

        def keyReleaseEvent(self, event):
            if self.active_scene is not None:
                self.active_scene.keyReleaseEvent(event)

        def mouseMoveEvent(self, event):
            if self.active_scene is not None:
                self.active_scene.mouseMoveEvent(event)

        def mousePressEvent(self, event):
            if self.active_scene is not None:
                self.active_scene.mousePressEvent(event)

        def mouseReleaseEvent(self, event):
            if self.active_scene is not None:
                self.active_scene.mouseReleaseEvent(event)

        def switch_scene(self, scene):
            if self.active_scene is not None:
                self.active_scene.clean_mem()
                self.active_scene.hide()
                self.active_scene.deleteLater()
                self.active_scene = None
            if scene == Scene.MAIN_MENU:
                self.active_scene = MainMenuScene(self, WINDOW_SIZE)
            elif scene == Scene.WORLD:
                self.active_scene = WorldScene(self, WINDOW_SIZE)

else:
    from world_sim import WorldSim


def main():
    if not GameInfo.is_headless:
        app = QApplication(sys.argv)
        window = ArenaWindow()
        window.setWindowTitle("Robo Arena")
        window.show()

        while window.running:  # main loop
            window.update()
            app.processEvents()

        sys.exit(0)

    else:
        world_sim = WorldSim()
        while True:
            world_sim.update_world()


if __name__ == '__main__':
    main()
