from os import path
from globals import GameInfo
from util import get_data_path

if not GameInfo.is_headless:
    from PyQt5.QtGui import QPixmap


loaded_pixmaps = {}


def get_pixmap(name, copy=False):
    """Caches pixmap and only returns a reference to the needed pixmap to avoid duplicate memory usage."""
    pixmap = loaded_pixmaps.get(name)

    if pixmap is None:
        pixmap = QPixmap(path.join(get_data_path(), name + ".png"))
        loaded_pixmaps[name] = pixmap

    if copy:
        pixmap = pixmap.copy(pixmap.rect())

    return pixmap
