import sys

from globals import GameInfo, Settings
from camera import CameraState
from util import get_main_path, Vector
from sound_manager import SoundManager, HeadlessSound

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
    from main_menu_scene import MainMenuScene
    from world_scene import SPWorldScene, OnlineWorldScene, ServerWorldScene
    from PyQt5.QtGui import QFont, QColor, QFontDatabase
    from PyQt5.QtWidgets import QOpenGLWidget, QApplication, QDesktopWidget
    from PyQt5.QtCore import Qt, QResource

    class ArenaWindow(QOpenGLWidget):
        def __init__(self):
            super().__init__()

            self.running = True
            self.frame_drawn = True

            self.active_scene = None

            self.init_window()

            self.switch_scene(Scene.MAIN_MENU)

        def init_window(self):
            geometry = QDesktopWidget().screenGeometry()

            # Use main monitor size:
            main_window_size = Vector(geometry.size().width(), geometry.size().height())
            # Always use exact reference size:
            #  main_window_size = GameInfo.window_reference_size

            GameInfo.window_size = main_window_size
            CameraState.scale = Vector(main_window_size.x / GameInfo.window_reference_size.x,
                                       main_window_size.y / GameInfo.window_reference_size.y)
            # Adjust scaling to height:
            CameraState.scale_factor = CameraState.scale.y

            CameraState.x_offset = (CameraState.scale.x - CameraState.scale.y) * GameInfo.window_reference_size.x * 0.5

            self.setFixedSize(main_window_size.x, main_window_size.y)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            geometry_rect = self.frameGeometry()
            geometry_rect.moveCenter(geometry.center())
            self.move(geometry_rect.topLeft())
            self.setWindowTitle("Robo Arena")
            self.setFocusPolicy(Qt.StrongFocus)
            self.show()

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

        def focusInEvent(self, event):
            self.focused = True

        def focusOutEvent(self, event):
            self.focused = False

        def switch_scene(self, scene):
            if self.active_scene is not None:
                self.active_scene.clean_mem()
                self.active_scene.hide()
                self.active_scene.deleteLater()
                self.active_scene = None
            if scene == Scene.MAIN_MENU:
                self.active_scene = MainMenuScene(self, GameInfo.window_size)
            elif scene == Scene.SP_WORLD:
                self.active_scene = SPWorldScene(self, GameInfo.window_size)
            elif scene == Scene.ONLINE_WORLD:
                self.active_scene = OnlineWorldScene(self, GameInfo.window_size)
            elif scene == Scene.SERVER_WORLD:
                self.active_scene = ServerWorldScene(self, GameInfo.window_size)

        def paintEvent(self, event):
            self.frame_drawn = True
            if self.active_scene is not None:
                self.active_scene.paintEvent(event)

else:
    from server_world_sim import ServerWorldSim


def main():
    if not GameInfo.is_headless:
        GameInfo.window_reference_size = Vector(1920, 1080)
        GameInfo.window_size = GameInfo.window_reference_size.copy()
        GameInfo.main_path = get_main_path()

        app = QApplication(sys.argv)

        QResource.registerResource(get_main_path() + "/resources.rcc")

        Settings.instance = Settings()
        SoundManager.instance = SoundManager()

        window = ArenaWindow()

        press_start_font_id = QFontDatabase.addApplicationFont(get_main_path()
                                                               + "/fonts/press_start_2p/PressStart2P-Regular.ttf")
        press_start_font_str = QFontDatabase.applicationFontFamilies(press_start_font_id)[0]

        Fonts.fps_font = QFont(press_start_font_str)
        Fonts.fps_font.setPixelSize(15)
        Fonts.fps_color = QColor(189, 38, 7)
        Fonts.text_field_font = QFont(press_start_font_str)
        Fonts.text_field_font.setPixelSize(46)
        Fonts.text_field_color = QColor(189, 38, 7)
        Fonts.text_field_default_color = QColor(75, 10, 10)
        Fonts.name_tag_font = QFont(press_start_font_str)
        Fonts.name_tag_font.setPixelSize(12)
        Fonts.name_tag_color = QColor(200, 200, 200)  # QColor(225, 50, 225)

        while window.running:  # main loop
            app.processEvents()
            window.update()
            if not window.frame_drawn:
                if window.active_scene.world_sim is not None:
                    window.active_scene.world_sim.update_world()
            window.frame_drawn = False

        sys.exit(0)

    else:
        Settings.instance = Settings()
        SoundManager.instance = HeadlessSound()

        world_sim = ServerWorldSim()
        while True:
            world_sim.update_world()


if __name__ == '__main__':
    main()
