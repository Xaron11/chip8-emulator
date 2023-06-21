from functools import partial
import random

import platform
if platform.system() == 'Windows':
    import winsound
else:
    import os

class Chip:
    def __init__(self, screen, keyboard):
        self.paused = False
        self.speed = 10

        self.v = bytearray(16)
        self.index = 0x0
        self.delay_timer = 0x0
        self.sound_timer = 0x0
        self.pc = self.PROGRAM_START
        self.sp = 0x0
        self.stack = []

        self.memory = bytearray(4096)

        self.screen = screen
        self.keyboard = keyboard
        self.on_next_key_press = None

    PROGRAM_START = 0x200
    SPRITES = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ]

    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def next_instruction(self, inst):
        self.pc += 2
        i = (inst & 0xF000) >> 12
        e = inst & 0x000F
        kk = inst & 0x00FF
        nnn = inst & 0x0FFF
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4

        call = self.get_instruction(i, kk, e)
        call(x, y, kk, nnn)

    def load_sprites(self):
        for i in range(len(self.SPRITES)):
            self.memory[i] = self.SPRITES[i]

    def load_program(self, program):
        for i in range(len(program)):
            self.memory[self.PROGRAM_START + i] = program[i]

    def load_rom(self, program, setup_keys=None):
        self.load_sprites()
        self.load_program(program)
        if setup_keys:
            for k, v in setup_keys.items():
                self.keyboard.keys[k] = v

    def cycle(self):
        for i in range(self.speed):
            if not self.paused:
                opcode = (self.memory[self.pc] << 8 | self.memory[self.pc + 1])
                self.next_instruction(opcode)

        if not self.paused:
            self.update_timers()

        self.screen.paint()

    def get_instruction(self, i, kk, e):
        if i == 0x0:
            if kk == 0xE0:
                return self.cls
            elif kk == 0xEE:
                return self.ret
        elif i == 0x1:
            return self.jp_addr
        elif i == 0x2:
            return self.call_addr
        elif i == 0x3:
            return self.se_vx_byte
        elif i == 0x4:
            return self.sne_vx_byte
        elif i == 0x5:
            return self.se_vx_vy
        elif i == 0x6:
            return self.ld_vx_byte
        elif i == 0x7:
            return self.add_vx_byte
        elif i == 0x8:
            if e == 0x0:
                return self.ld_vx_xy
            elif e == 0x1:
                return self.or_vx_vy
            elif e == 0x2:
                return self.and_vx_vy
            elif e == 0x3:
                return self.xor_vx_vy
            elif e == 0x4:
                return self.add_vx_vy
            elif e == 0x5:
                return self.sub_vx_vy
            elif e == 0x6:
                return self.shr_vx_vy
            elif e == 0x7:
                return self.subn_vx_vy
            elif e == 0xE:
                return self.shl_vx_vy
        elif i == 0x9:
            return self.sne_vx_vy
        elif i == 0xA:
            return self.ld_i_addr
        elif i == 0xB:
            return self.jp_v0_addr
        elif i == 0xC:
            return self.rnd_vx_byte
        elif i == 0xD:
            return self.drw_vx_vy_n
        elif i == 0xE:
            if kk == 0x9E:
                return self.skp_vx
            elif kk == 0xA1:
                return self.sknp_vx
        elif i == 0xF:
            if kk == 0x07:
                return self.ld_vx_dt
            elif kk == 0x0A:
                return self.ld_vx_k
            elif kk == 0x15:
                return self.ld_dt_vx
            elif kk == 0x18:
                return self.ld_st_vx
            elif kk == 0x1E:
                return self.add_i_vx
            elif kk == 0x29:
                return self.ld_f_vx
            elif kk == 0x33:
                return self.ld_b_vx
            elif kk == 0x55:
                return self.ld_i_vx
            elif kk == 0x65:
                return self.ld_vx_i

        raise Exception(f'Wrong OpCode: i:{i}, kk:{kk}, e:{e}')

    def cls(self, x, y, kk, nnn):
        self.screen.clear()

    def ret(self, x, y, kk, nnn):
        self.pc = self.stack.pop()

    def jp_addr(self, x, y, kk, nnn):
        self.pc = nnn

    def call_addr(self, x, y, kk, nnn):
        self.stack.append(self.pc)
        self.pc = nnn

    def se_vx_byte(self, x, y, kk, nnn):
        if self.v[x] == kk:
            self.pc += 2

    def sne_vx_byte(self, x, y, kk, nnn):
        if self.v[x] != kk:
            self.pc += 2

    def se_vx_vy(self, x, y, kk, nnn):
        if self.v[x] == self.v[y]:
            self.pc += 2

    def ld_vx_byte(self, x, y, kk, nnn):
        self.v[x] = kk

    def add_vx_byte(self, x, y, kk, nnn):
        result = self.v[x] + kk
        self.v[x] = result & 0xFF

    def ld_vx_xy(self, x, y, kk, nnn):
        self.v[x] = self.v[y]

    def or_vx_vy(self, x, y, kk, nnn):
        self.v[x] |= self.v[y]

    def and_vx_vy(self, x, y, kk, nnn):
        self.v[x] &= self.v[y]

    def xor_vx_vy(self, x, y, kk, nnn):
        self.v[x] ^= self.v[y]

    def add_vx_vy(self, x, y, kk, nnn):
        result = self.v[x] + self.v[y]
        self.v[0xF] = result > 0xFF
        self.v[x] = result & 0xFF

    def sub_vx_vy(self, x, y, kk, nnn):
        self.v[0xF] = self.v[x] > self.v[y]
        result = self.v[x] - self.v[y]
        if result < 0:
            result = 0
        self.v[x] = result

    def shr_vx_vy(self, x, y, kk, nnn):
        self.v[0xF] = self.v[x] & 0x1
        self.v[x] >>= 1

    def subn_vx_vy(self, x, y, kk, nnn):
        self.v[0xF] = self.v[y] > self.v[x]
        self.v[x] = self.v[y] - self.v[x]

    def shl_vx_vy(self, x, y, kk, nnn):
        # TODO: before implementation:
        # self.v[0xF] = (self.v[x] >> 8) & 0x1
        self.v[0xF] = self.v[x] & 0x80
        self.v[x] = (self.v[x] << 1) & 0xFF

    def sne_vx_vy(self, x, y, kk, nnn):
        if self.v[x] != self.v[y]:
            self.pc += 2

    def ld_i_addr(self, x, y, kk, nnn):
        self.index = nnn

    def jp_v0_addr(self, x, y, kk, nnn):
        self.pc = nnn + self.v[0]

    def rnd_vx_byte(self, x, y, kk, nnn):
        rnd = random.randint(0, 255)
        self.v[x] = rnd & kk

    def drw_vx_vy_n(self, x, y, kk, nnn):
        byte = 8
        n = nnn & 0xF

        self.v[0xF] = 0

        for row in range(n):
            sprite = self.memory[self.index + row]
            for col in range(byte):
                if (sprite & 0x80) > 0:
                    if self.screen.set_pixel(self.v[x] + col, self.v[y] + row):
                        self.v[0xF] = 1

                sprite = (sprite << 1) & 0xFF

    def skp_vx(self, x, y, kk, nnn):
        if self.keyboard.is_pressed(self.v[x]):
            self.pc += 2

    def sknp_vx(self, x, y, kk, nnn):
        if not self.keyboard.is_pressed(self.v[x]):
            self.pc += 2

    def ld_vx_dt(self, x, y, kk, nnn):
        self.v[x] = self.delay_timer

    def ld_vx_k(self, x, y, kk, nnn):
        self.paused = True

        def on_next_press(key):
            self.v[x] = key
            self.paused = False

        self.keyboard.on_next_key_press = partial(on_next_press, self)

    def ld_dt_vx(self, x, y, kk, nnn):
        self.delay_timer = self.v[x]

    def ld_st_vx(self, x, y, kk, nnn):
        self.sound_timer = self.v[x]
        if self.sound_timer > 0:
            if platform.system() == 'Windows':
                winsound.Beep(2500, int(self.sound_timer * 1000/60))
            else:
                os.system(f'play -nq -t alsa synth {self.sound_timer / 1000} sine 440')

    def add_i_vx(self, x, y, kk, nnn):
        self.index += self.v[x]

    def ld_f_vx(self, x, y, kk, nnn):
        self.index = self.v[x] * 5

    def ld_b_vx(self, x, y, kk, nnn):
        number = self.v[x]
        hundreds = number // 100
        tens = (number % 100) // 10
        ones = number % 10
        self.memory[self.index] = hundreds
        self.memory[self.index + 1] = tens
        self.memory[self.index + 2] = ones

    def ld_i_vx(self, x, y, kk, nnn):
        n = x + 1
        for i in range(n):
            self.memory[self.index + i] = self.v[i]

    def ld_vx_i(self, x, y, kk, nnn):
        n = x + 1
        for i in range(n):
            self.v[i] = self.memory[self.index + i]
