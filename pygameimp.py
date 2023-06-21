import pygame

from keyboard import Keyboard
from screen import Screen


class PygameScreen(Screen):
    BACKGROUND_COLOR = (0, 0, 0)
    WHITE_COLOR = (255, 255, 255)

    def __init__(self, scale=8, title='8-Chip Emulator'):
        super().__init__()
        self.scale = scale
        self.title = title
        self.screen = pygame.display.set_mode((self.WIDTH * scale, self.HEIGHT * scale))
        pygame.display.set_caption(title)

    def paint(self):
        self.screen.fill(PygameScreen.BACKGROUND_COLOR)

        for i, pixel in enumerate(self.display):
            x = (i % self.WIDTH) * self.scale
            y = i // self.WIDTH * self.scale

            if self.display[i] == 1:
                pygame.draw.rect(self.screen, PygameScreen.WHITE_COLOR, (x, y, self.scale, self.scale))


class PygameKeyboard(Keyboard):
    def __init__(self):
        super().__init__()
        # self.keys.values = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
        #                     pygame.K_9, pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f]

    def is_pressed(self, key):
        return pygame.key.get_pressed()[self.keys[key]]
