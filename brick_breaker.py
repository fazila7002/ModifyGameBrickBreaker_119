"""
Modify Game Brick Breaker - Tkinter
Nama : Fazilatun Nisa Muslimah
NIM  : 20250140119

Basis: https://www.studytonight.com/tkinter/brick-breaker-game-using-tkinter-python-project
Modifikasi: skor, level bertingkat, high score, pause, restart,
kontrol mouse, pantulan paddle bersudut, HUD baru, tema warna gelap.
"""

import tkinter as tk
import random


# ===================== CLASS INDUK =====================
class GameObject:
    """Class induk untuk semua objek di dalam canvas."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# ===================== BOLA =====================
class Ball(GameObject):
    def __init__(self, canvas, x, y, speed=5):
        self.radius = 9
        self.direction = [1, -1]
        self.speed = speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#F8F8F2', outline='')
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # MODIFIKASI: pakai abs() supaya bola tidak "nyangkut" di dinding
        if coords[0] <= 0:
            self.direction[0] = abs(self.direction[0])
        elif coords[2] >= width:
            self.direction[0] = -abs(self.direction[0])
        if coords[1] <= 0:
            self.direction[1] = abs(self.direction[1])
        self.move(self.direction[0] * self.speed,
                  self.direction[1] * self.speed)

    def collide(self, game_objects):
        """Atur pantulan bola. Mengembalikan list bata yang hancur."""
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        destroyed = []

        paddles = [obj for obj in game_objects if isinstance(obj, Paddle)]
        if paddles:
            # MODIFIKASI: sudut pantul tergantung titik kena di paddle
            p = paddles[0].get_position()
            center = (p[0] + p[2]) * 0.5
            half = (p[2] - p[0]) * 0.5
            offset = max(-1, min(1, (x - center) / half))
            dx = offset * 1.3
            if abs(dx) < 0.3:
                dx = 0.3 if dx >= 0 else -0.3
            self.direction[0] = dx
            self.direction[1] = -1
        elif len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            obj_coords = game_objects[0].get_position()
            if x > obj_coords[2]:
                self.direction[0] = abs(self.direction[0])
            elif x < obj_coords[0]:
                self.direction[0] = -abs(self.direction[0])
            else:
                self.direction[1] *= -1

        for obj in game_objects:
            if isinstance(obj, Brick) and obj.hit():
                destroyed.append(obj)
        return destroyed


# ===================== PADDLE =====================
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 12
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='#FFB643', outline='')
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # batasi supaya paddle tidak keluar layar
        if coords[0] + offset < 0:
            offset = -coords[0]
        if coords[2] + offset > width:
            offset = width - coords[2]
        super().move(offset, 0)
        if self.ball is not None:
            self.ball.move(offset, 0)

    def move_to(self, x):
        """MODIFIKASI: paddle mengikuti posisi mouse."""
        coords = self.get_position()
        center = (coords[0] + coords[2]) * 0.5
        self.move(x - center)


# ===================== BATA =====================
class Brick(GameObject):
    COLORS = {1: '#50FA7B', 2: '#FF79C6', 3: '#BD93F9'}
    POINTS = {1: 10, 2: 20, 3: 30}

    def __init__(self, canvas, x, y, hits):
        self.width = 73
        self.height = 18
        self.hits = hits
        self.points = Brick.POINTS[hits]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=Brick.COLORS[hits], outline='#1E1E2E',
                                       tags='brick')
        super().__init__(canvas, item)

    def hit(self):
        """Kurangi nyawa bata. True kalau bata hancur."""
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return True
        self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
        return False


# ===================== GAME =====================
class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.width = 610
        self.height = 420
        self.canvas = tk.Canvas(self, bg='#1E1E2E', highlightthickness=0,
                                width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.lives = 3
        self.score = 0
        self.level = 1
        self.high_score = 0
        self.state = 'ready'      # ready / playing / paused / between / over
        self.loop_id = None
        self.message = None

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 380)
        self.items[self.paddle.item] = self.paddle

        # HUD (MODIFIKASI: skor, level, high score, nyawa berbentuk hati)
        self.canvas.create_line(0, 30, self.width, 30, fill='#44475A')
        self.hud_lives = self.canvas.create_text(12, 15, anchor='w',
                                                 fill='#FF5555', font=('Helvetica', 13, 'bold'))
        self.hud_score = self.canvas.create_text(self.width / 2, 15,
                                                 fill='#F8F8F2', font=('Helvetica', 13, 'bold'))
        self.hud_level = self.canvas.create_text(self.width - 12, 15, anchor='e',
                                                 fill='#8BE9FD', font=('Helvetica', 13, 'bold'))

        self.build_level()
        self.setup_round()

        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))
        self.canvas.bind('<Motion>', lambda e: self.paddle.move_to(e.x))
        self.canvas.bind('<space>', lambda _: self.on_space())
        self.canvas.bind('<p>', lambda _: self.toggle_pause())
        self.canvas.bind('<P>', lambda _: self.toggle_pause())

    # ---------- tampilan ----------
    def update_hud(self):
        self.canvas.itemconfig(self.hud_lives, text='♥ ' * self.lives)
        self.canvas.itemconfig(self.hud_score,
                               text=f'Skor: {self.score}   High: {self.high_score}')
        self.canvas.itemconfig(self.hud_level, text=f'Level {self.level}')

    def show_message(self, text, size=22):
        self.clear_message()
        self.message = self.canvas.create_text(self.width / 2, self.height / 2 + 40,
                                               text=text, fill='#F8F8F2', justify='center',
                                               font=('Helvetica', size, 'bold'))

    def clear_message(self):
        if self.message is not None:
            self.canvas.delete(self.message)
            self.message = None

    # ---------- level & ronde ----------
    def build_level(self):
        """MODIFIKASI: level makin tinggi, baris & bata keras makin banyak."""
        for item in self.canvas.find_withtag('brick'):
            self.canvas.delete(item)
            self.items.pop(item, None)

        rows = 3 + min(self.level - 1, 3)
        weights = [max(1, 6 - self.level), 3, self.level]
        for row in range(rows):
            y = 55 + row * 22
            for x in range(5, self.width - 5, 75):
                hits = random.choices([1, 2, 3], weights=weights)[0]
                brick = Brick(self.canvas, x + 37.5, y, hits)
                self.items[brick.item] = brick

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        coords = self.paddle.get_position()
        x = (coords[0] + coords[2]) * 0.5
        speed = 5 + (self.level - 1)          # MODIFIKASI: bola makin cepat tiap level
        self.ball = Ball(self.canvas, x, coords[1] - 10, speed)
        self.paddle.set_ball(self.ball)

    def setup_round(self):
        self.add_ball()
        self.update_hud()
        self.state = 'ready'
        self.show_message('Tekan SPASI untuk mulai\nGerakkan: mouse / panah   |   P = pause', 15)

    def start_game(self):
        self.clear_message()
        self.paddle.ball = None
        self.state = 'playing'
        self.game_loop()

    def on_space(self):
        if self.state == 'ready':
            self.start_game()
        elif self.state == 'over':
            self.restart()

    def toggle_pause(self):
        """MODIFIKASI: fitur pause."""
        if self.state == 'playing':
            self.state = 'paused'
            if self.loop_id:
                self.after_cancel(self.loop_id)
            self.show_message('PAUSE\nTekan P untuk lanjut')
        elif self.state == 'paused':
            self.clear_message()
            self.state = 'playing'
            self.game_loop()

    def next_level(self):
        self.level += 1
        self.build_level()
        self.setup_round()

    def game_over(self):
        self.state = 'over'
        self.high_score = max(self.high_score, self.score)
        self.update_hud()
        self.show_message(f'GAME OVER\nSkor kamu: {self.score}\nTekan SPASI untuk main lagi')

    def restart(self):
        """MODIFIKASI: main lagi tanpa menutup program."""
        self.lives = 3
        self.score = 0
        self.level = 1
        self.build_level()
        self.setup_round()

    # ---------- loop utama ----------
    def game_loop(self):
        if self.state != 'playing':
            return
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))

        if num_bricks == 0:
            self.state = 'between'
            self.score += 100 * self.level      # bonus naik level
            self.high_score = max(self.high_score, self.score)
            self.update_hud()
            self.ball.delete()
            self.ball = None
            self.show_message(f'Level {self.level} selesai!\nBonus +{100 * self.level}')
            self.after(1500, self.next_level)
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            self.update_hud()
            if self.lives <= 0:
                self.game_over()
            else:
                self.state = 'between'
                self.show_message('Nyawa berkurang!')
                self.after(1000, self.setup_round)
        else:
            self.ball.update()
            self.loop_id = self.after(30, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        for brick in self.ball.collide(objects):
            self.score += brick.points
            self.items.pop(brick.item, None)
        self.update_hud()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker - Modified by Fazila (119)')
    root.resizable(False, False)
    game = Game(root)
    game.mainloop()
