"""
BRICK BREAKER - ARCADE EDITION (Tkinter)
Nama : Fazilatun Nisa Muslimah
NIM  : 20250140119

Basis: https://www.studytonight.com/tkinter/brick-breaker-game-using-tkinter-python-project
"""

import math
import random
import tkinter as tk

import highscore
import settings as S
from effects import Particles, Shake, Starfield
from game_object import GameObject
from powerups import TYPES, PowerUp
from sound import Sound


# ===================== BOLA =====================
class Ball(GameObject):
    MAX_SPEED = 10

    def __init__(self, canvas, x, y, speed):
        self.radius = 8
        self.speed = speed
        angle = math.radians(random.uniform(-35, 35))
        self.vx = speed * math.sin(angle)
        self.vy = -speed * math.cos(angle)
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill=S.BALL_COLOR, outline=S.NEON_CYAN, width=2)
        super().__init__(canvas, item)

    def center(self):
        c = self.get_position()
        return (c[0] + c[2]) / 2, (c[1] + c[3]) / 2

    def set_speed(self, speed):
        speed = max(3, min(self.MAX_SPEED, speed))
        current = math.hypot(self.vx, self.vy) or 1
        self.vx *= speed / current
        self.vy *= speed / current
        self.speed = speed

    def update(self):
        """Gerakkan bola. Return True kalau memantul di dinding."""
        c = self.get_position()
        bounced = False
        if (c[0] + self.vx <= 0 and self.vx < 0) or (c[2] + self.vx >= S.WIDTH and self.vx > 0):
            self.vx = -self.vx
            bounced = True
        if c[1] + self.vy <= S.HUD_H and self.vy < 0:
            self.vy = -self.vy
            bounced = True
        self.move(self.vx, self.vy)
        return bounced

    def bounce_paddle(self, paddle):
        """Sudut pantul tergantung titik kena di paddle (tengah lurus, pinggir miring)."""
        p = paddle.get_position()
        x, _ = self.center()
        half = (p[2] - p[0]) / 2
        offset = max(-1.0, min(1.0, (x - (p[0] + half)) / half))
        angle = math.radians(offset * 60)
        self.speed = min(self.MAX_SPEED, self.speed + 0.15)
        self.vx = self.speed * math.sin(angle)
        self.vy = -self.speed * math.cos(angle)

    def bounce_bricks(self, bricks):
        x, y = self.center()
        b = bricks[0].get_position()
        bx, by = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if len(bricks) > 1 or b[0] <= x <= b[2]:
            self.vy = abs(self.vy) if y > by else -abs(self.vy)
        elif b[1] <= y <= b[3]:
            self.vx = abs(self.vx) if x > bx else -abs(self.vx)
        else:   # kena pojok bata
            self.vx = abs(self.vx) if x > bx else -abs(self.vx)
            self.vy = abs(self.vy) if y > by else -abs(self.vy)


# ===================== PADDLE =====================
class Paddle(GameObject):
    BASE_WIDTH = 100

    def __init__(self, canvas, x, y):
        self.width = self.BASE_WIDTH
        self.height = 12
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=S.PADDLE_COLOR, outline='#ffffff', width=2)
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        c = self.get_position()
        if c[0] + offset < 0:
            offset = -c[0]
        if c[2] + offset > S.WIDTH:
            offset = S.WIDTH - c[2]
        if offset:
            super().move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

    def move_to(self, x):
        c = self.get_position()
        self.move(x - (c[0] + c[2]) / 2)

    def set_width(self, width):
        c = self.get_position()
        cx = max(width / 2, min(S.WIDTH - width / 2, (c[0] + c[2]) / 2))
        self.width = width
        self.canvas.coords(self.item, cx - width / 2, c[1], cx + width / 2, c[3])


# ===================== BATA =====================
class Brick(GameObject):
    def __init__(self, canvas, x, y, hits):
        self.hits = hits
        self.points = S.BRICK_POINTS[hits]
        fill, line = S.BRICK_STYLE[hits]
        item = canvas.create_rectangle(x - S.BRICK_W / 2, y - S.BRICK_H / 2,
                                       x + S.BRICK_W / 2, y + S.BRICK_H / 2,
                                       fill=fill, outline=line, width=2, tags='brick')
        super().__init__(canvas, item)

    def color(self):
        return S.BRICK_STYLE[self.hits][0]

    def hit(self):
        """Kurangi nyawa bata. True kalau bata hancur."""
        self.hits -= 1
        if self.hits <= 0:
            self.delete()
            return True
        fill, line = S.BRICK_STYLE[self.hits]
        self.canvas.itemconfig(self.item, fill=fill, outline=line)
        return False


# ===================== GAME =====================
class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=S.BG)
        self.canvas = tk.Canvas(self, width=S.WIDTH, height=S.HEIGHT,
                                bg=S.BG, highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.sound = Sound()
        self.high_score = highscore.load()
        self.state = 'title'
        self.frame = 0
        self.keys = set()
        self.overlay = []
        self.blink = []
        self.title_items = []
        self.touching = set()
        self.powerups = []
        self.trail = []
        self.ball = None
        self.items = {}
        self.reset_stats()

        self.draw_background()
        self.stars = Starfield(self.canvas)
        self.canvas.tag_lower('star')
        self.canvas.tag_lower('bg')
        self.particles = Particles(self.canvas)
        self.shake = Shake(self.canvas)

        self.trail_items = [self.canvas.create_oval(-20, -20, -20, -20, fill=c, outline='')
                            for c in S.TRAIL_COLORS]
        self.paddle = Paddle(self.canvas, S.WIDTH / 2, S.HEIGHT - 50)
        self.items[self.paddle.item] = self.paddle

        self.create_hud()
        self.bind_keys()
        self.show_title()
        self.tick()

    # ---------- tampilan ----------
    def draw_background(self):
        """Grid neon ala game retro."""
        for x in range(0, S.WIDTH + 1, 40):
            self.canvas.create_line(x, S.HUD_H, x, S.HEIGHT, fill=S.GRID, tags='bg')
        for y in range(S.HUD_H, S.HEIGHT + 1, 40):
            self.canvas.create_line(0, y, S.WIDTH, y, fill=S.GRID, tags='bg')

    def create_hud(self):
        self.canvas.create_rectangle(0, 0, S.WIDTH, S.HUD_H, fill='#11112a', outline='')
        self.canvas.create_line(0, S.HUD_H, S.WIDTH, S.HUD_H, fill=S.NEON_PINK, width=2)
        font = (S.FONT, 13, 'bold')
        self.hud_lives = self.canvas.create_text(12, S.HUD_H / 2, anchor='w', fill=S.NEON_PINK,
                                                 font=('Segoe UI Symbol', 14, 'bold'))
        self.hud_score = self.canvas.create_text(S.WIDTH / 2, S.HUD_H / 2,
                                                 fill=S.TEXT, font=font)
        self.hud_level = self.canvas.create_text(S.WIDTH - 12, S.HUD_H / 2, anchor='e',
                                                 fill=S.NEON_CYAN, font=font)
        self.hud_info = self.canvas.create_text(S.WIDTH / 2, S.HEIGHT - 14, fill=S.DIM,
                                                font=(S.FONT, 10, 'bold'))

    def update_hud(self):
        self.canvas.itemconfig(self.hud_lives, text='♥ ' * self.lives)
        best = max(self.high_score, self.score)
        self.canvas.itemconfig(self.hud_score, text=f'SCORE {self.score:06d}   HI {best:06d}')
        self.canvas.itemconfig(self.hud_level, text=f'LV {self.level}')
        info = []
        if self.combo > 1:
            info.append(f'COMBO x{self.combo}')
        if self.wide_timer:
            info.append('PADDLE LEBAR')
        if self.slow_timer:
            info.append('BOLA LAMBAT')
        music = 'ON' if self.sound.music_on else 'OFF'
        text = '   '.join(info) or f'[P] PAUSE   [M] MUSIK {music}'
        self.canvas.itemconfig(self.hud_info, text=text)

    def overlay_text(self, x, y, text, color, size, blink=False):
        font = (S.FONT, size, 'bold')
        items = []
        if size >= 16:   # bayangan supaya teks terlihat "timbul"
            items.append(self.canvas.create_text(x + 3, y + 3, text=text, fill=S.SHADOW,
                                                 font=font, justify='center'))
        item = self.canvas.create_text(x, y, text=text, fill=color, font=font, justify='center')
        items.append(item)
        self.overlay.extend(items)
        if blink:
            self.blink.extend(items)
        return item

    def clear_overlay(self):
        for item in self.overlay:
            self.canvas.delete(item)
        self.overlay = []
        self.blink = []
        self.title_items = []

    def animate_text(self):
        show = (self.frame // 25) % 2 == 0
        for item in self.blink:
            self.canvas.itemconfig(item, state='normal' if show else 'hidden')
        if self.frame % 6 == 0:
            for i, item in enumerate(self.title_items):
                color = S.RAINBOW[(self.frame // 6 + i) % len(S.RAINBOW)]
                self.canvas.itemconfig(item, fill=color)

    # ---------- kontrol ----------
    def bind_keys(self):
        c = self.canvas
        c.focus_set()
        c.bind('<KeyPress-Left>', lambda _: self.keys.add('L'))
        c.bind('<KeyRelease-Left>', lambda _: self.keys.discard('L'))
        c.bind('<KeyPress-Right>', lambda _: self.keys.add('R'))
        c.bind('<KeyRelease-Right>', lambda _: self.keys.discard('R'))
        c.bind('<Motion>', self.on_mouse)
        c.bind('<Button-1>', lambda _: (c.focus_set(), self.on_space()))
        c.bind('<space>', lambda _: self.on_space())
        for key in ('p', 'P'):
            c.bind(f'<{key}>', lambda _: self.toggle_pause())
        for key in ('m', 'M'):
            c.bind(f'<{key}>', lambda _: self.toggle_music())

    def on_mouse(self, event):
        if self.state in ('ready', 'playing'):
            self.paddle.move_to(event.x)

    def on_space(self):
        if self.state == 'title':
            self.sound.play('start')
            self.setup_round()
        elif self.state == 'ready':
            self.clear_overlay()
            self.paddle.set_ball(None)
            self.state = 'playing'
            self.sound.play('paddle')
        elif self.state == 'gameover':
            self.show_title()

    def toggle_pause(self):
        if self.state == 'playing':
            self.state = 'paused'
            self.sound.pause_music()
            self.overlay_text(S.WIDTH / 2, 300, 'PAUSE', S.NEON_YELLOW, 30)
            self.overlay_text(S.WIDTH / 2, 345, 'TEKAN P UNTUK LANJUT', S.TEXT, 14, blink=True)
        elif self.state == 'paused':
            self.clear_overlay()
            self.sound.resume_music()
            self.state = 'playing'

    def toggle_music(self):
        self.sound.toggle_music()
        self.update_hud()

    # ---------- alur game ----------
    def reset_stats(self):
        self.lives = 3
        self.score = 0
        self.level = 1
        self.combo = 1
        self.wide_timer = 0
        self.slow_timer = 0
        self.saved_speed = 0

    def show_title(self):
        self.state = 'title'
        self.reset_stats()
        self.clear_overlay()
        self.clear_powerups()
        self.build_level()
        self.paddle.set_width(Paddle.BASE_WIDTH)
        cx = S.WIDTH / 2
        for i, word in enumerate(['BRICK', 'BREAKER']):
            self.title_items.append(self.overlay_text(cx, 235 + i * 52, word, S.RAINBOW[i], 40))
        self.overlay_text(cx, 335, '- ARCADE EDITION -', S.NEON_YELLOW, 14)
        self.overlay_text(cx, 380, 'TEKAN SPASI UNTUK MULAI', S.TEXT, 16, blink=True)
        self.overlay_text(cx, 418, f'HIGH SCORE {self.high_score:06d}', S.NEON_CYAN, 12)
        self.overlay_text(cx, 445, 'MOUSE / PANAH = GERAK    P = PAUSE    M = MUSIK', S.DIM, 10)
        self.sound.start_music()
        self.update_hud()

    def build_level(self):
        for item in list(self.canvas.find_withtag('brick')):
            self.canvas.delete(item)
            self.items.pop(item, None)
        if self.level <= len(S.LEVELS):
            pattern = S.LEVELS[self.level - 1]
        else:   # level acak, makin tinggi makin banyak bata keras
            rows = min(6, 3 + self.level // 2)
            weights = [3, 3, min(6, self.level - 2)]
            pattern = [''.join('.' if random.random() < 0.1 else random.choices('123', weights)[0]
                               for _ in range(S.BRICK_COLS)) for _ in range(rows)]
        left = (S.WIDTH - S.BRICK_COLS * (S.BRICK_W + 2)) / 2 + S.BRICK_W / 2 + 1
        for r, row in enumerate(pattern):
            for c, ch in enumerate(row):
                if ch != '.':
                    x = left + c * (S.BRICK_W + 2)
                    y = S.BRICK_TOP + r * (S.BRICK_H + 4)
                    brick = Brick(self.canvas, x, y, int(ch))
                    self.items[brick.item] = brick

    def setup_round(self):
        self.clear_overlay()
        self.clear_powerups()
        self.hide_trail()
        self.wide_timer = 0
        self.slow_timer = 0
        self.combo = 1
        self.touching = set()
        self.paddle.set_width(Paddle.BASE_WIDTH)
        if self.ball is not None:
            self.ball.delete()
        c = self.paddle.get_position()
        speed = 4.5 + 0.4 * (self.level - 1)
        self.ball = Ball(self.canvas, (c[0] + c[2]) / 2, c[1] - 9, speed)
        self.paddle.set_ball(self.ball)
        self.state = 'ready'
        self.overlay_text(S.WIDTH / 2, 300, f'LEVEL {self.level}', S.NEON_YELLOW, 26)
        self.overlay_text(S.WIDTH / 2, 345, 'TEKAN SPASI', S.TEXT, 14, blink=True)
        self.sound.start_music()
        self.update_hud()

    def level_clear(self):
        self.state = 'levelclear'
        bonus = 500 * self.level
        self.score += bonus
        self.remove_ball()
        self.clear_powerups()
        self.sound.play('level')
        cx = S.WIDTH / 2
        self.overlay_text(cx, 290, 'LEVEL CLEAR!', S.NEON_GREEN, 30)
        self.overlay_text(cx, 335, f'BONUS +{bonus}', S.NEON_YELLOW, 16)
        for _ in range(6):   # kembang api
            self.particles.burst(random.uniform(80, S.WIDTH - 80), random.uniform(90, 230),
                                 random.choice(S.RAINBOW), 22)
        self.update_hud()
        self.after(2200, self.next_level)

    def next_level(self):
        self.level += 1
        self.build_level()
        self.setup_round()

    def lose_life(self):
        self.lives -= 1
        self.combo = 1
        self.wide_timer = 0
        self.slow_timer = 0
        self.paddle.set_width(Paddle.BASE_WIDTH)
        self.remove_ball()
        self.clear_powerups()
        self.shake.start(10)
        self.sound.play('lose')
        self.update_hud()
        if self.lives <= 0:
            self.game_over()
        else:
            self.state = 'dead'
            self.overlay_text(S.WIDTH / 2, 300, 'OOPS!', S.NEON_PINK, 30)
            self.after(1200, self.setup_round)

    def game_over(self):
        self.state = 'gameover'
        self.sound.stop_music()
        self.sound.play('gameover')
        cx = S.WIDTH / 2
        new_record = self.score > self.high_score
        if new_record:
            self.high_score = self.score
            highscore.save(self.score)
        self.overlay_text(cx, 270, 'GAME OVER', S.NEON_PINK, 36)
        self.overlay_text(cx, 320, f'SCORE {self.score:06d}', S.TEXT, 18)
        if new_record:
            self.overlay_text(cx, 358, '★ NEW HIGH SCORE! ★', S.NEON_YELLOW, 16, blink=True)
        self.overlay_text(cx, 400, 'TEKAN SPASI', S.TEXT, 14, blink=True)
        self.update_hud()

    def remove_ball(self):
        if self.ball is not None:
            self.ball.delete()
            self.ball = None
        self.hide_trail()

    # ---------- loop utama (~60 FPS) ----------
    def tick(self):
        self.frame += 1
        self.shake.reset()
        self.stars.update()
        self.particles.update()
        if self.state in ('ready', 'playing'):
            step = (9 if 'R' in self.keys else 0) - (9 if 'L' in self.keys else 0)
            if step:
                self.paddle.move(step)
        if self.state == 'playing':
            self.update_play()
        self.animate_text()
        self.shake.apply()
        self.after(S.FPS_DELAY, self.tick)

    def update_play(self):
        if self.ball.update():
            self.sound.play('wall')
        self.update_trail()
        self.check_collisions()
        self.update_powerups()
        self.update_timers()
        if not self.canvas.find_withtag('brick'):
            self.level_clear()
        elif self.ball.get_position()[1] > S.HEIGHT:
            self.lose_life()

    def update_trail(self):
        """Jejak bola: lingkaran kecil di posisi-posisi sebelumnya."""
        self.trail.insert(0, self.ball.center())
        del self.trail[len(self.trail_items) + 1:]
        for i, item in enumerate(self.trail_items):
            if i + 1 < len(self.trail):
                x, y = self.trail[i + 1]
                r = 7 - i
                self.canvas.coords(item, x - r, y - r, x + r, y + r)
            else:
                self.canvas.coords(item, -20, -20, -20, -20)

    def hide_trail(self):
        self.trail = []
        for item in self.trail_items:
            self.canvas.coords(item, -20, -20, -20, -20)

    def check_collisions(self):
        ids = self.canvas.find_overlapping(*self.ball.get_position())
        objects = [self.items[i] for i in ids if i in self.items]
        if self.paddle in objects and self.ball.vy > 0:
            self.ball.bounce_paddle(self.paddle)
            self.combo = 1
            self.sound.play('paddle')
            self.update_hud()
        bricks = [o for o in objects if isinstance(o, Brick)]
        new = [b for b in bricks if b.item not in self.touching]
        self.touching = {b.item for b in bricks}
        if new:
            self.ball.bounce_bricks(new)
            for brick in new:
                self.hit_brick(brick)

    def hit_brick(self, brick):
        x0, y0, x1, y1 = brick.get_position()
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        color = brick.color()
        if brick.hit():
            self.items.pop(brick.item, None)
            points = brick.points * self.combo
            self.score += points
            self.particles.burst(cx, cy, color)
            self.particles.text(cx, cy, f'+{points}', color)
            self.shake.start(3 + min(self.combo, 5))
            self.sound.play('break')
            self.combo += 1
            if self.combo in (3, 5, 8, 12, 16, 20):
                self.particles.text(S.WIDTH / 2, 280, f'COMBO x{self.combo}!', S.NEON_YELLOW, 20)
            powerup = PowerUp.maybe_drop(self.canvas, cx, cy)
            if powerup:
                self.powerups.append(powerup)
        else:
            self.particles.burst(cx, cy, color, count=5)
            self.sound.play('hit')
        self.update_hud()

    def update_powerups(self):
        p = self.paddle.get_position()
        for powerup in list(self.powerups):
            powerup.update()
            x0, y0, x1, y1 = powerup.get_position()
            caught = y1 >= p[1] and y0 <= p[3] and x1 >= p[0] and x0 <= p[2]
            if caught:
                self.apply_powerup(powerup.kind, (x0 + x1) / 2, y0)
            if caught or y0 > S.HEIGHT:
                powerup.delete()
                self.powerups.remove(powerup)

    def apply_powerup(self, kind, x, y):
        self.sound.play('powerup')
        color, label = TYPES[kind]
        self.particles.text(x, y - 12, label, color, 12)
        self.particles.burst(x, y, color, 10)
        if kind == 'W':
            self.wide_timer = 600
            self.paddle.set_width(160)
        elif kind == 'S':
            if not self.slow_timer:
                self.saved_speed = self.ball.speed
            self.slow_timer = 480
            self.ball.set_speed(self.saved_speed * 0.6)
        elif kind == '+':
            self.lives = min(6, self.lives + 1)
        self.update_hud()

    def update_timers(self):
        if self.wide_timer:
            self.wide_timer -= 1
            if not self.wide_timer:
                self.paddle.set_width(Paddle.BASE_WIDTH)
                self.update_hud()
        if self.slow_timer:
            self.slow_timer -= 1
            if not self.slow_timer:
                self.ball.set_speed(self.saved_speed)
                self.update_hud()

    def clear_powerups(self):
        for powerup in self.powerups:
            powerup.delete()
        self.powerups = []


if __name__ == '__main__':
    root = tk.Tk()
    root.title('BRICK BREAKER - Arcade Edition | Fazila (119)')
    root.configure(bg=S.BG)
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()
