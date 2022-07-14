import sys

from globals import GameInfo

headless_args = []
for arg in sys.argv:
    if arg == "--headless":
        headless_args.append(arg)
        GameInfo.is_headless = True
for arg in headless_args:
    sys.argv.remove(arg)
headless_args.clear()

if not GameInfo.is_headless:
    from globals import Scene, Fonts
    from constants import WINDOW_SIZE
    from main_menu_scene import MainMenuScene
    from world_scene import SPWorldScene, OnlineWorldScene, ServerWorldScene
    from PyQt5.QtGui import QFont, QColor
    from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
    from PyQt5.QtCore import Qt

    class ArenaWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.running = True

            self.active_scene = None

            self.init_window()

            self.switch_scene(Scene.MAIN_MENU)

        def init_window(self):
            self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

            geometry_rect = self.frameGeometry()
            center_point = QDesktopWidget().availableGeometry().center()
            geometry_rect.moveCenter(center_point)
            self.move(geometry_rect.topLeft())

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
            elif scene == Scene.SP_WORLD:
                self.active_scene = SPWorldScene(self, WINDOW_SIZE)
            elif scene == Scene.ONLINE_WORLD:
                self.active_scene = OnlineWorldScene(self, WINDOW_SIZE)
            elif scene == Scene.SERVER_WORLD:
                self.active_scene = ServerWorldScene(self, WINDOW_SIZE)

else:
    from server_world_sim import ServerWorldSim


def main():
    if not GameInfo.is_headless:
        app = QApplication(sys.argv)
        window = ArenaWindow()
        window.setWindowTitle("Robo Arena")
        window.show()

        Fonts.fps_font = QFont("Noto Sans", 10)
        Fonts.fps_color = Qt.red
        Fonts.text_field_font = QFont("Noto Sans", 16)
        Fonts.text_field_color = Qt.darkCyan
        Fonts.text_field_default_color = Qt.gray
        Fonts.name_tag_font = QFont("Noto Sans", 11)
        Fonts.name_tag_color = QColor(200, 200, 200)  # QColor(225, 50, 225)

        while window.running:  # main loop
            app.processEvents()
            window.update()

        sys.exit(0)

    else:
        world_sim = ServerWorldSim()
        while True:
            world_sim.update_world()


if __name__ == '__main__':
    main()
