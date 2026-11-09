"""Efek visual arcade: bintang bergerak, partikel ledakan, teks melayang, dan getaran layar."""
import random

from settings import FONT, HEIGHT, WIDTH


class Starfield:
    """Bintang-bintang kecil yang bergerak turun pelan di latar belakang."""

    def __init__(self, canvas, count=60):
        self.canvas = canvas
        self.stars = []
        for _ in range(count):
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            speed = random.choice([0.3, 0.6, 1.2])
            size = 1 if speed < 1 else 2
            color = '#3a3a6a' if speed < 0.5 else ('#6a6aa0' if speed < 1 else '#b0b0e0')
            item = canvas.create_rectangle(x, y, x + size, y + size,
                                           fill=color, outline='', tags='star')
            self.stars.append((item, speed))

    def update(self):
        for item, speed in self.stars:
            self.canvas.move(item, 0, speed)
            if self.canvas.coords(item)[1] > HEIGHT:
                self.canvas.move(item, 0, -HEIGHT - 4)


class Particles:
    """Partikel ledakan dan teks skor yang melayang."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.items = []     # [item, vx, vy, umur, gravitasi]

    def burst(self, x, y, color, count=14):
        for _ in range(count):
            s = random.choice([2, 3, 4])
            item = self.canvas.create_rectangle(x, y, x + s, y + s, fill=color, outline='')
            self.items.append([item, random.uniform(-4, 4), random.uniform(-5, 1),
                               random.randint(20, 40), 0.25])

    def text(self, x, y, msg, color, size=12):
        item = self.canvas.create_text(x, y, text=msg, fill=color,
                                       font=(FONT, size, 'bold'))
        self.items.append([item, 0, -1.2, 45, 0])

    def update(self):
        alive = []
        for p in self.items:
            self.canvas.move(p[0], p[1], p[2])
            p[2] += p[4]
            p[3] -= 1
            if p[3] <= 0:
                self.canvas.delete(p[0])
            else:
                alive.append(p)
        self.items = alive


class Shake:
    """Getaran layar: semua objek di canvas digeser acak sebentar."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.power = 0
        self.dx = self.dy = 0

    def start(self, power=6):
        self.power = max(self.power, power)

    def reset(self):
        """Kembalikan posisi sebelum logika game dihitung."""
        if self.dx or self.dy:
            self.canvas.move('all', -self.dx, -self.dy)
            self.dx = self.dy = 0

    def apply(self):
        if self.power > 0:
            self.dx = random.randint(-self.power, self.power)
            self.dy = random.randint(-self.power, self.power)
            self.canvas.move('all', self.dx, self.dy)
            self.power -= 1
