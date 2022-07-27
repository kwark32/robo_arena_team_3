from globals import GameInfo
from util import get_main_path

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


loaded_pixmaps = {}


def get_pixmap(name, copy=False):
    pixmap = loaded_pixmaps.get(name)

    if pixmap is None:
        pixmap = QPixmap(get_main_path() + name + ".png")
        loaded_pixmaps[name] = pixmap

    if copy:
        pixmap = pixmap.copy(pixmap.rect())

    return pixmap
