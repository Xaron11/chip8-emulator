

class Screen:
    WIDTH = 64
    HEIGHT = 32

    def __init__(self):
        self.display = [0] * (self.WIDTH * self.HEIGHT)

    def set_pixel(self, x, y):
        if x >= self.WIDTH:
            x -= self.WIDTH
        elif x < 0:
            x += self.WIDTH

        if y >= self.HEIGHT:
            y -= self.HEIGHT
        elif y < 0:
            y += self.HEIGHT

        self.display[x + y * self.WIDTH] ^= 1
        return self.display[x + y * self.WIDTH] != 1

    def clear(self):
        self.display = [0] * (self.WIDTH * self.HEIGHT)

    def paint(self):
        pass

