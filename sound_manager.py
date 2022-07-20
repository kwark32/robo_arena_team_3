from util import get_main_path
from globals import Settings, GameInfo

if not GameInfo.is_headless:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtMultimedia import QSoundEffect


sfx_path = get_main_path() + "/sounds/sfx/"
music_path = get_main_path() + "/sounds/music/"


class SFXManager:
    instance = None

    def __init__(self):
        self.sounds = {}

    def play_sound(self, name):
        sound = None
        sound_list = self.sounds.get(name)
        if sound_list is None:
            sound = self.load_sound(name)
            self.sounds[name] = [sound]
        else:
            for s in sound_list:
                if not s.isPlaying():
                    sound = s
                    break
            if sound is None:
                sound = self.load_sound(name)
                self.sounds[name].append(sound)

        sound.play()

    def load_sound(self, name):
        sound = QSoundEffect()
        sound.setSource(QUrl.fromLocalFile(sfx_path + name + ".wav"))
        sound.setVolume(Settings.instance.master_volume)
        return sound


class HeadlessSFX(SFXManager):
    def play_sound(self, name):
        pass

    def load_sound(self, name):
        pass
