import random

from os import path
from globals import Settings, GameInfo
from constants import HALF_FALLOFF_DIST, MAX_AUDIO_DIST, SFX_AUDIO_SOURCES


sfx_path = path.join("qrc:", "sounds", "sfx")
music_path = path.join("qrc:", "sounds", "music")

music_names = ["soundtrack-1_normal", "soundtrack-2_boss"]
music_volume_factors = {"soundtrack-1_normal": 0.36, "soundtrack-2_boss": 0.75}


if not GameInfo.is_headless:
    from PyQt5.QtCore import QUrl, QObject, QThread, QMutex, pyqtSignal, pyqtSlot
    from PyQt5.QtMultimedia import QSoundEffect

    class SFXLoaderWorker(QObject):
        """Worker thread object for loading & starting sounds."""
        wake_worker = pyqtSignal()

        @pyqtSlot()
        def update(self):
            """Checks all pending sounds and loads & starts them."""
            while len(SoundManager.instance.sfx_start_list) > 0:
                SoundManager.instance.sfx_start_list_mutex.lock()
                sound, name, pos = SoundManager.instance.sfx_start_list.pop(0)
                SoundManager.instance.sfx_start_list_mutex.unlock()

                sound.setSource(QUrl(path.join(sfx_path, name + ".wav")))
                sound.setVolume(SoundManager.instance.get_sound_volume(pos=pos))
                sound.play()

                SoundManager.instance.ready_sounds_mutex.lock()
                SoundManager.instance.ready_sounds.append((sound, pos))
                SoundManager.instance.ready_sounds_mutex.unlock()

        def run(self):
            pass


class SoundManager:
    """Global class to start & manage all sounds/music."""
    instance = None

    def __init__(self):
        self.sounds = []
        self.ready_sounds = []
        self.ready_sounds_mutex = None
        self.sfx_start_list = []
        self.sfx_start_list_mutex = None

        self.listener_pos = None

        self.music = None
        self.play_random_music = False
        self.playing_music_name = ""

        self.catchup_frame = False

        if not GameInfo.is_headless:
            self.ready_sounds_mutex = QMutex()
            self.sfx_start_list_mutex = QMutex()
            self.sfx_loader_thread = QThread()
            self.sfx_loader_worker = SFXLoaderWorker()
            self.sfx_loader_worker.moveToThread(self.sfx_loader_thread)
            self.sfx_loader_worker.wake_worker.connect(self.sfx_loader_worker.update)
            self.sfx_loader_thread.start()

    def update_sound(self, listener_pos=None):
        """Moves started sound from loader/starter thread to main thread & updates volumes & music."""
        self.ready_sounds_mutex.lock()
        for i in range(len(self.ready_sounds)):
            sound = self.ready_sounds.pop(0)
            self.sounds.append(sound)
        self.ready_sounds_mutex.unlock()

        self.listener_pos = listener_pos
        self.set_sound_volumes()

        if self.play_random_music and self.music is None:
            random_state = random.getstate()
            next_music = random.choice(music_names)
            self.play_music(next_music)
            random.setstate(random_state)

    def play_sfx(self, name, pos=None):
        if self.catchup_frame:
            return

        if pos is not None:
            pos = pos.copy()

        if len(self.sounds) + len(self.sfx_start_list) >= SFX_AUDIO_SOURCES:
            return

        sound = QSoundEffect()

        self.sfx_start_list_mutex.lock()
        self.sfx_start_list.append((sound, name, pos))
        self.sfx_start_list_mutex.unlock()

        self.sfx_loader_worker.wake_worker.emit()

    def play_music(self, name, once=True):
        self.playing_music_name = name

        if self.music is not None:
            self.music.stop()
            self.music = None

        self.music = QSoundEffect()
        self.music.setSource(QUrl(path.join(music_path, name + ".wav")))
        if once:
            self.music.setLoopCount(1)
        else:
            self.music.setLoopCount(QSoundEffect.Infinite)
        self.music.setVolume(self.get_sound_volume(sfx_volume=False))
        self.music.play()

    def set_sound_volumes(self):
        """Sets sound effect volumes based on the distance to the local player."""
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
        """Gets volume of a sound effect based on the distance to the local player."""
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
    """Empty placeholder class for headless server, overriding all methods with pass."""
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

    def _set_sound(self, sound, pos, name):
        pass
