"""Sound engine chiptune.

Semua efek suara dan musik latar dibuat sendiri lewat kode (gelombang kotak,
segitiga, dan noise), lalu disimpan sebagai file .wav sementara.
Tidak perlu download file audio apa pun.

Backend:
- pygame-ce (pip install pygame-ce) -> efek suara + musik jalan bersamaan
- kalau tidak ada pygame, di Windows pakai winsound (efek suara saja)
- selain itu game tetap jalan tanpa suara
"""
import array
import math
import os
import random
import tempfile
import wave

RATE = 22050
CACHE = os.path.join(tempfile.gettempdir(), 'brick_breaker_119_audio_v1')


def note(midi):
    """Ubah nomor nada MIDI jadi frekuensi (Hz)."""
    return 440.0 * 2 ** ((midi - 69) / 12)


def _square(phase):
    return 1.0 if phase % 1.0 < 0.5 else -1.0


def _triangle(phase):
    return 4.0 * abs(phase % 1.0 - 0.5) - 1.0


def _render(steps, shape=_square, volume=0.35):
    """steps = list (frekuensi_awal, frekuensi_akhir, durasi_detik)."""
    out = []
    phase = 0.0
    for f0, f1, dur in steps:
        n = int(RATE * dur)
        for i in range(n):
            t = i / n
            f = f0 + (f1 - f0) * t
            phase += f / RATE
            env = min(1.0, i / 80) * (1.0 - t) ** 0.6
            out.append(shape(phase) * volume * env)
    return out


def _save(path, samples):
    data = array.array('h', (int(max(-1.0, min(1.0, s)) * 32767) for s in samples))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())


# ---------- efek suara ----------
SFX = {
    'paddle': [(note(72), note(79), 0.07)],
    'wall': [(note(60), note(62), 0.03)],
    'hit': [(note(84), note(88), 0.05)],
    'break': [(note(79), note(79), 0.04), (note(84), note(84), 0.04), (note(91), note(91), 0.08)],
    'powerup': [(note(72 + k), note(72 + k), 0.05) for k in (0, 4, 7, 12, 16, 19, 24)],
    'lose': [(note(67), note(55), 0.18), (note(55), note(40), 0.35)],
    'start': [(note(76), note(76), 0.08), (note(81), note(81), 0.08), (note(88), note(88), 0.18)],
    'level': [(note(m), note(m), 0.11) for m in (72, 76, 79, 84, 79, 84, 88)],
    'gameover': [(note(m), note(m), 0.25) for m in (67, 63, 60, 55)],
}

# ---------- musik latar (loop 8 bar, A minor) ----------
MELODY = [81, 76, 72, 76, 81, 76, 72, 76,
          77, 72, 69, 72, 77, 72, 69, 72,
          79, 76, 72, 76, 79, 76, 72, 76,
          79, 74, 71, 74, 83, 79, 74, 79,
          81, 0, 81, 83, 84, 83, 81, 76,
          77, 0, 77, 79, 81, 79, 77, 72,
          79, 0, 79, 81, 83, 81, 79, 74,
          76, 80, 83, 88, 83, 80, 76, 0]
BASS = [45, 41, 48, 43, 45, 41, 43, 40]
STEP = 0.2   # durasi 1 not (detik)


def _music():
    n = int(RATE * STEP)
    mix = [0.0] * (n * len(MELODY))
    # melodi: gelombang kotak
    phase = 0.0
    for k, m in enumerate(MELODY):
        if not m:
            continue
        f = note(m)
        for i in range(n):
            phase += f / RATE
            env = min(1.0, i / 60) * (1.0 - i / n) ** 0.8
            mix[k * n + i] += _square(phase) * 0.15 * env
    # bass: gelombang segitiga, oktaf naik-turun
    phase = 0.0
    for k in range(len(MELODY)):
        f = note(BASS[k // 8] + (12 if k % 2 else 0))
        for i in range(n):
            phase += f / RATE
            env = min(1.0, i / 60) * (1.0 - i / n) ** 0.4
            mix[k * n + i] += _triangle(phase) * 0.3 * env
    # hi-hat: noise pendek di ketukan off-beat
    rnd = random.Random(7)
    hat = int(RATE * 0.03)
    for k in range(1, len(MELODY), 2):
        for i in range(hat):
            mix[k * n + i] += (rnd.random() * 2 - 1) * 0.06 * (1 - i / hat)
    return mix


class Sound:
    def __init__(self):
        self.music_on = True
        self.backend = None
        self.files = {}
        self.sounds = {}
        try:
            os.makedirs(CACHE, exist_ok=True)
            for name, steps in SFX.items():
                path = os.path.join(CACHE, name + '.wav')
                if not os.path.exists(path):
                    _save(path, _render(steps))
                self.files[name] = path
            self.music_file = os.path.join(CACHE, 'music.wav')
            if not os.path.exists(self.music_file):
                _save(self.music_file, _music())
        except OSError:
            return

        try:
            os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
            import pygame
            pygame.mixer.pre_init(RATE, -16, 1, 512)
            pygame.mixer.init()
            self.sounds = {k: pygame.mixer.Sound(v) for k, v in self.files.items()}
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(0.45)
            self.pygame = pygame
            self.backend = 'pygame'
        except Exception:
            try:
                import winsound
                self.winsound = winsound
                self.backend = 'winsound'
            except ImportError:
                self.backend = None

    def play(self, name):
        if name not in self.files:
            return
        if self.backend == 'pygame':
            self.sounds[name].play()
        elif self.backend == 'winsound':
            ws = self.winsound
            ws.PlaySound(self.files[name], ws.SND_FILENAME | ws.SND_ASYNC | ws.SND_NODEFAULT)

    def start_music(self):
        if self.backend == 'pygame' and self.music_on:
            if not self.pygame.mixer.music.get_busy():
                self.pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.backend == 'pygame':
            self.pygame.mixer.music.stop()

    def pause_music(self):
        if self.backend == 'pygame':
            self.pygame.mixer.music.pause()

    def resume_music(self):
        if self.backend == 'pygame' and self.music_on:
            self.pygame.mixer.music.unpause()

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.start_music()
        else:
            self.stop_music()
        return self.music_on
