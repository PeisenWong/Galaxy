from kivy.uix.relativelayout import RelativeLayout


def on_touch_down(self, touch):
    if not self.game_over_state and self.game_has_started_state:
        if touch.x < self.width / 2:
            self.current_space_x += self.SPEED_X
        else:
            self.current_space_x -= self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.current_space_x = 0


def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None


def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_space_x += self.SPEED_X
    elif keycode[1] == 'right':
        self.current_space_x -= self.SPEED_X
    return True


def _on_keyboard_up(self, keyboard, keycode):
    self.current_space_x = 0
    return True