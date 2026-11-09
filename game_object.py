"""Class induk untuk semua objek di dalam canvas (bola, paddle, bata, power-up)."""


class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item        # id item canvas atau nama tag

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)
