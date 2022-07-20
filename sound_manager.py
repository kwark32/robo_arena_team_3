from util import get_main_path, Vector
from globals import Settings, GameInfo
from constants import HALF_FALLOFF_DIST

if not GameInfo.is_headless:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtMultimedia import QSoundEffect


sfx_path = get_main_path() + "/sounds/sfx/"
music_path = get_main_path() + "/sounds/music/"


class SFXManager:
    instance = None

    def __init__(self):
        self.sounds = {}

    def play_sound(self, name, pos=None):
        if pos is not None:
            pos = pos.copy()

        sound = None
        sound_list = self.sounds.get(name)
        if sound_list is None:
            sound = self.load_sound(name)
            self.sounds[name] = [(sound, pos)]
        else:
            for s in sound_list:
                if not s[0].isPlaying():
                    sound = s[0]
                    break
            if sound is None:
                sound = self.load_sound(name)
                self.sounds[name].append((sound, pos))

        sound.setVolume(Settings.instance.master_volume * Settings.instance.sfx_volume)
        sound.play()

    def load_sound(self, name):
        sound = QSoundEffect()
        sound.setSource(QUrl.fromLocalFile(sfx_path + name + ".wav"))
        sound.setVolume(0)
        return sound

    def set_volumes(self, pos):
        if pos is None:
            pos = Vector(0, 0)

        for key in self.sounds:
            sound_list = self.sounds[key]
            for sound in sound_list:
                sound_pos = sound[1]
                sound = sound[0]

                if not sound.isPlaying():
                    continue

                if sound_pos is not None:
                    dist = pos.dist(sound_pos)
                    volume = 1 / (dist / HALF_FALLOFF_DIST + 1)
                else:
                    volume = 1
                sound.setVolume(Settings.instance.master_volume * Settings.instance.sfx_volume * volume)


class HeadlessSFX(SFXManager):
    def play_sound(self, name, pos=None):
        pass

    def load_sound(self, name):
        pass

    def set_volumes(self, pos):
        pass
