"""Pengaturan tema arcade: ukuran layar, warna neon, font, dan pola level."""

WIDTH = 640
HEIGHT = 520
HUD_H = 36              # tinggi panel skor di atas
FPS_DELAY = 16          # ms per frame (~60 FPS)

# ---------- warna neon ----------
BG = '#0b0b1a'
GRID = '#1a1440'
TEXT = '#f8f8f2'
DIM = '#8888bb'
NEON_PINK = '#ff2e88'
NEON_YELLOW = '#ffd319'
NEON_CYAN = '#2de2e6'
NEON_GREEN = '#7cff4f'
NEON_ORANGE = '#ff7b00'
NEON_PURPLE = '#b967ff'
RAINBOW = [NEON_PINK, NEON_ORANGE, NEON_YELLOW, NEON_GREEN, NEON_CYAN, NEON_PURPLE]
SHADOW = '#3a0a2a'

FONT = 'Consolas'

PADDLE_COLOR = NEON_CYAN
BALL_COLOR = '#ffffff'
TRAIL_COLORS = ['#c8c8ff', '#9a9ae0', '#6f6fc0', '#4a4a99', '#2e2e70', '#1c1c48']

# warna bata berdasarkan sisa hit: (isi, garis tepi)
BRICK_STYLE = {
    1: (NEON_GREEN, '#d4ffc4'),
    2: (NEON_PINK, '#ffc2dc'),
    3: (NEON_PURPLE, '#e6d1ff'),
}
BRICK_POINTS = {1: 10, 2: 20, 3: 30}

BRICK_W = 74
BRICK_H = 20
BRICK_COLS = 8
BRICK_TOP = 70

# pola level: angka = jumlah hit bata, '.' = kosong
# setelah level terakhir, level dibuat acak dan makin sulit
LEVELS = [
    ["11111111",
     "11111111",
     "22222222"],
    ["2.2.2.2.",
     ".1.1.1.1",
     "33333333",
     "1.1.1.1."],
    ["...33...",
     "..2222..",
     ".111111.",
     "22222222",
     ".111111."],
    ["3......3",
     "23....32",
     "123..321",
     "11233211",
     "22222222"],
]
