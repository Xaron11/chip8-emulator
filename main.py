import pygame
import requests
from chip import Chip
from pygameimp import PygameScreen, PygameKeyboard

pong_url = 'https://github.com/kripod/chip8-roms/raw/master/games/Pong%20(1%20player).ch8'
space_invaders_url = 'https://github.com/kripod/chip8-roms/raw/master/games/Space%20Invaders%20%5BDavid%20Winter%5D.ch8'
tetris_url = 'https://github.com/kripod/chip8-roms/raw/master/games/Tetris%20%5BFran%20Dachille%2C%201991%5D.ch8'
test_url = 'https://github.com/corax89/chip8-test-rom/raw/master/test_opcode.ch8'

pong = requests.get(pong_url).content
space_invaders = requests.get(space_invaders_url).content
tetris = requests.get(tetris_url).content
test = requests.get(test_url).content


pygame.init()
chip = Chip(PygameScreen(), PygameKeyboard())
chip.load_rom(pong, {1: pygame.K_UP, 4: pygame.K_DOWN})
# chip.load_rom(space_invaders, {4: pygame.K_LEFT, 5: pygame.K_UP, 6: pygame.K_RIGHT})
# chip.load_rom(tetris, {4: pygame.K_UP, 5: pygame.K_LEFT, 6: pygame.K_RIGHT, 7: pygame.K_DOWN})

running = True
clock = pygame.time.Clock()


def get_key(pygame_key):
    for k, v in chip.keyboard.keys.items():
        if v == pygame_key:
            return k
    return None


while running:
    chip.cycle()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            key = get_key(event.key)
            if key:
                chip.keyboard.on_key_down(key)
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
