import os
import pygame

class AudioManager:
    def __init__(self):
        self._available = False
        self._sounds = {}

    def pre_init(self, frequency=44100, size=-16, channels=2, buffer=512):
        """Call pygame.mixer.pre_init before pygame.init() to reduce latency."""
        try:
            pygame.mixer.pre_init(frequency, size, channels, buffer)
        except Exception:
            # If pygame isn't available or pre_init fails, continue silently
            pass

    def init(self):
        """Initialize the mixer and load default sounds from config."""
        try:
            # Try to (re)initialize the mixer
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._available = True
        except Exception:
            self._available = False

        # Load configured sounds if mixer is available
        if self._available:
            try:
                from src.ui.config import ARROW_SOUND_PATH, KNIFE_SOUND_PATH, LONGSWORD_SOUND_PATH, SOUND_VOLUME
                self.load('arrow', ARROW_SOUND_PATH, SOUND_VOLUME)
                self.load('knife', KNIFE_SOUND_PATH, SOUND_VOLUME)
                self.load('longsword', LONGSWORD_SOUND_PATH, SOUND_VOLUME)
            except Exception:
                # ignore config import or load errors
                pass

    def load(self, name: str, path: str, volume: float = 1.0):
        """Load a sound and store it under `name`. Safe if mixer or file are missing."""
        if not self._available:
            return None
        try:
            if not os.path.exists(path):
                return None
            snd = pygame.mixer.Sound(path)
            snd.set_volume(volume)
            self._sounds[name] = snd
            return snd
        except Exception:
            return None

    def play(self, name: str):
        """Play a previously loaded sound by name. Safe no-op if unavailable."""
        if not self._available:
            return
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def status(self):
        """Return status useful for debugging: whether mixer is available and which sounds loaded."""
        return {
            'available': bool(self._available),
            'loaded': list(self._sounds.keys())
        }


# Singleton instance
manager = AudioManager()

def pre_init(*a, **kw):
    manager.pre_init(*a, **kw)

def init():
    manager.init()

def load(name, path, volume=1.0):
    return manager.load(name, path, volume)

def play(name):
    return manager.play(name)

def status():
    return manager.status()
