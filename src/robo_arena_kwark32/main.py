import sys
import time

from globals import GameInfo, Settings

headless_args = []
for arg in sys.argv:
    if arg == "--headless":
        headless_args.append(arg)
        GameInfo.is_headless = True
for arg in headless_args:
    sys.argv.remove(arg)
headless_args.clear()

if True:
    from camera import CameraState
    from util import get_main_path, Vector
    from constants import FIXED_DELTA_TIME_NS
    from sound_manager import SoundManager, HeadlessSound


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
            self.active_scene_has_world_sim = False

            self.window_geometry = None

            self.init_window()

            self.switch_scene(Scene.MAIN_MENU)

        def init_window(self):
            self.setWindowTitle("Robo Arena")
            self.setFocusPolicy(Qt.StrongFocus)
            self.setMinimumSize(640, 360)
            self.update_fullscreen()

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

        def resizeGL(self, w, h):
            self.update_window_size()
            if self.active_scene is not None:
                self.active_scene.resizeGL(w, h)

        def switch_scene(self, scene):
            if self.active_scene is not None:
                self.active_scene.clean_mem()
                self.active_scene.hide()
                self.active_scene.deleteLater()
                self.active_scene = None
            if scene == Scene.MAIN_MENU:
                self.active_scene = MainMenuScene(self)
            elif scene == Scene.SP_WORLD:
                self.active_scene = SPWorldScene(self)
            elif scene == Scene.ONLINE_WORLD:
                self.active_scene = OnlineWorldScene(self)
            elif scene == Scene.SERVER_WORLD:
                self.active_scene = ServerWorldScene(self)

            self.active_scene_has_world_sim = self.active_scene is not None and hasattr(self.active_scene, "world_sim")

        def paintEvent(self, event):
            self.frame_drawn = True
            if self.active_scene is not None:
                self.active_scene.paintEvent(event)

        def update_fullscreen(self):
            if Settings.instance.fullscreen:
                self.showFullScreen()
            else:
                self.showNormal()

            self.update_window_size()

        def update_window_size(self):
            if Settings.instance.fullscreen:
                self.window_geometry = QDesktopWidget().screenGeometry()
            else:
                self.window_geometry = self.geometry()

            main_window_size = Vector(self.window_geometry.size().width(), self.window_geometry.size().height())
            GameInfo.window_size = main_window_size
            CameraState.scale = Vector(main_window_size.x / GameInfo.window_reference_size.x,
                                       main_window_size.y / GameInfo.window_reference_size.y)
            # Adjust scaling to height:
            CameraState.scale_factor = CameraState.scale.y

            CameraState.x_offset = ((CameraState.scale.x - CameraState.scale.y) / CameraState.scale_factor
                                    * GameInfo.window_reference_size.x * 0.5)

else:
    from server_world_sim import ServerWorldSim


def main():
    if not GameInfo.is_headless:
        GameInfo.window_reference_size = Vector(1920, 1080)
        GameInfo.window_size = GameInfo.window_reference_size.copy()

        app = QApplication(sys.argv)

        QResource.registerResource(get_main_path() + "resources.rcc")

        Settings.instance = Settings(get_main_path())
        SoundManager.instance = SoundManager()

        window = ArenaWindow()

        press_start_font_id = QFontDatabase.addApplicationFont(get_main_path()
                                                               + "fonts/press_start_2p/PressStart2P-Regular.ttf")
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
        Fonts.ui_text_font = QFont(press_start_font_str)
        Fonts.ui_text_font.setPixelSize(60)
        Fonts.score_color = QColor(167, 77, 216)
        Fonts.highscore_color = QColor(10, 200, 50)
        Fonts.score_board_font = QFont(press_start_font_str)
        Fonts.score_board_font.setPixelSize(18)
        Fonts.score_board_color = QColor(200, 200, 200)

        while window.running:  # main loop
            update_graphics(app, window)
            if not window.frame_drawn:
                if window.active_scene_has_world_sim and window.active_scene.world_sim is not None:
                    update_headless(window.active_scene.world_sim)
            window.frame_drawn = False

        sys.exit(0)

    else:
        Settings.instance = Settings(get_main_path())
        SoundManager.instance = HeadlessSound()

        world_sim = ServerWorldSim()
        while True:
            update_headless(world_sim)


def update_graphics(app, window):
    window.update()
    app.processEvents()


def update_headless(world_sim):
    time_safety_margin = 2000000  # 2ms
    while time.time_ns() - (FIXED_DELTA_TIME_NS - time_safety_margin) < world_sim.curr_time_ns:
        time.sleep(0.001)  # sleep 1ms at a time

    while True:
        world_sim.update_world()
        if world_sim.did_fixed_update:
            break


if __name__ == '__main__':
    main()
