class Keyboard:
    def __init__(self):
        self.keys = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None,
                     0xA: None, 0xB: None, 0xC: None, 0xD: None, 0xE: None, 0xF: None}
        self.on_next_key_press = None

    def on_key_down(self, key):
        if self.on_next_key_press is not None:
            self.on_next_key_press(key)
            self.on_next_key_press = None

    def is_pressed(self, key):
        pass
