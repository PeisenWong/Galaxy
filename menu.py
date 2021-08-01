from kivy.uix.relativelayout import RelativeLayout


class MenuWidget(RelativeLayout):
    # Let the widget useless when opacity = 0
    def on_touch_down(self, touch):
        if self.opacity == 0:
            return False
        return super(RelativeLayout, self).on_touch_down(touch)
