"""Power-up yang kadang jatuh dari bata yang pecah.

W = paddle lebar, S = bola lambat, + = nyawa tambahan.
"""
import random

from game_object import GameObject
from settings import BG, FONT, NEON_CYAN, NEON_PINK, NEON_YELLOW

TYPES = {
    'W': (NEON_CYAN, 'PADDLE LEBAR!'),
    'S': (NEON_YELLOW, 'BOLA LAMBAT!'),
    '+': (NEON_PINK, 'NYAWA +1!'),
}
DROP_CHANCE = 0.18


class PowerUp(GameObject):
    _count = 0

    def __init__(self, canvas, x, y, kind):
        PowerUp._count += 1
        self.kind = kind
        tag = f'powerup{PowerUp._count}'
        color = TYPES[kind][0]
        # kotak + huruf digabung dalam satu tag supaya bergerak bersama
        canvas.create_rectangle(x - 16, y - 9, x + 16, y + 9, fill=BG,
                                outline=color, width=2, tags=(tag, 'powerup'))
        canvas.create_text(x, y, text=kind, fill=color,
                           font=(FONT, 11, 'bold'), tags=(tag, 'powerup'))
        super().__init__(canvas, tag)

    def update(self):
        self.move(0, 2.5)

    @staticmethod
    def maybe_drop(canvas, x, y):
        if random.random() < DROP_CHANCE:
            return PowerUp(canvas, x, y, random.choice(list(TYPES)))
        return None
