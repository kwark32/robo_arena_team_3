import random

# from util import get_main_path, Vector
from globals import Settings, GameInfo
from constants import HALF_FALLOFF_DIST, MAX_AUDIO_DIST, SFX_AUDIO_SOURCES

if not GameInfo.is_headless:
    from PyQt5.QtCore import QUrl
    from PyQt5.QtMultimedia import QSoundEffect


sfx_path = "qrc:" + "/sounds/sfx/"
music_path = "qrc:" + "/sounds/music/"

music_names = ["soundtrack-1_normal", "soundtrack-2_boss"]
music_volume_factors = {"soundtrack-1_normal": 0.6, "soundtrack-2_boss": 1}


class SoundManager:
    instance = None

    def __init__(self):
        self.sounds = []
        self.listener_pos = None

        self.music = None
        self.play_random_music = False
        self.playing_music_name = ""

    def update_sound(self, listener_pos=None):
        self.listener_pos = listener_pos
        self.set_sound_volumes()

        if self.play_random_music and self.music is None:
            random_state = random.getstate()
            next_music = random.choice(music_names)
            self.play_music(next_music)
            random.setstate(random_state)

    def play_sfx(self, name, pos=None):
        if pos is not None:
            pos = pos.copy()

        if len(self.sounds) >= SFX_AUDIO_SOURCES:
            return

        sound = QSoundEffect()
        sound.setSource(QUrl(sfx_path + name + ".wav"))
        sound.setVolume(self.get_sound_volume(pos=pos))
        sound.play()
        self.sounds.append((sound, pos))

    def play_music(self, name, once=True):
        self.playing_music_name = name

        if self.music is not None:
            self.music.stop()
            self.music = None

        self.music = QSoundEffect()
        self.music.setSource(QUrl(music_path + name + ".wav"))
        if once:
            self.music.setLoopCount(1)
        else:
            self.music.setLoopCount(QSoundEffect.Infinite)
        self.music.setVolume(self.get_sound_volume(sfx_volume=False))
        self.music.play()

    def set_sound_volumes(self):
        if self.music is not None and self.music.isPlaying():
            self.music.setVolume(self.get_sound_volume(sfx_volume=False))
        elif self.music is not None:
            self.music.stop()
            self.music = None

        stopped = []
        for sound in self.sounds:
            sound_pos = sound[1]
            sound = sound[0]

            if not sound.isPlaying():
                stopped.append((sound, sound_pos))
                continue

            sound.setVolume(self.get_sound_volume(pos=sound_pos))

        for s in stopped:
            s[0].stop()
            self.sounds.remove(s)

    def get_sound_volume(self, sfx_volume=True, pos=None):
        if sfx_volume:
            volume_setting = Settings.instance.master_volume * Settings.instance.sfx_volume
        else:
            volume_setting = Settings.instance.master_volume * Settings.instance.music_volume
            factor = music_volume_factors.get(self.playing_music_name)
            if factor is not None:
                volume_setting *= factor

        if self.listener_pos is None or pos is None:
            return volume_setting

        dist = self.listener_pos.dist(pos)
        if dist <= MAX_AUDIO_DIST:
            volume = 1 / (dist / HALF_FALLOFF_DIST + 1)
        else:
            return 0

        return volume_setting * volume


class HeadlessSound(SoundManager):
    def update_sound(self, listener_pos=None):
        pass

    def play_sfx(self, name, pos=None):
        pass

    def play_music(self, name, once=True):
        pass

    def set_sound_volumes(self, pos=None):
        pass

    def get_sound_volume(self, sfx_volume=True, pos=None):
        return 0
