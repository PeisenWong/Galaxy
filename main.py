import random

from kivy import platform
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Line, Quad, Triangle, Color
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

kivy.require('1.11.1')

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transform import transform, transform_perspective, transform_2D
    from user_action import _on_keyboard_up, _keyboard_closed, _on_keyboard_down, on_touch_down, on_touch_up
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    line = None
    vertical_line = []
    V_NB_LINE = 8
    SPACING = .2  # Percentage of width of screen

    horizontal_line = []
    H_NB_LINE = 5
    SPACING_Y = .2  # Percentage of height of screen

    SPEED = 0.015
    current_offset_y = 0

    SPEED_X = 0.04
    current_space_x = 0
    current_offset_x = 0

    tiles = []
    tiles_coordinate = []
    NB_TILES = 16
    current_y_loop = 0

    ship = None
    ship_coordinate = [(0, 0), (0, 0), (0, 0)]
    ship_height = 0.035
    ship_width = .1
    ship_base_y = 0.04

    game_over_state = False
    game_has_started_state = False
    menu_text = StringProperty("G   A   L   A   X   Y")
    menu_button_text = StringProperty("START GAME")

    score_text = StringProperty("SCORE: " + str(0))

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT  " + "W: " + str(self.width) + ", " + "H: " + str(self.height))
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_sound()
        self.sound_galaxy.play()
        self.init_tile()
        self.init_ship()  # Must call the ship after the tile!
        self.pre_fill_tile_coordinate()
        self.generate_tiles_coordinate()
        # Use keyboard in desktop, determine whether is in desktop but analysing platform
        if self.on_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)  # the update function will be called in every 1/60 sec

    def init_sound(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_begin.volume = 1
        self.sound_restart.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_music1.volume = .25
        self.sound_gameover_impact.volume = .6

    def reset_game(self):
        self.current_offset_y = 0
        self.current_space_x = 0
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.tiles_coordinate = []
        self.score_text = "SCORE: " + str(self.current_y_loop)
        self.pre_fill_tile_coordinate()
        self.generate_tiles_coordinate()
        self.game_over_state = False

    def on_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    # State the value of perspective_point_x
    def on_perspective_point_x(self, widget, value):
        # print("PX: " + str(value))
        pass

    def on_perspective_point_y(self, widget, value):
        # print("PY: " + str(value))
        pass

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.ship_base_y * self.height
        ship_height = self.ship_height * self.height
        ship_width = self.ship_width * self.width
        # State the coordinate of triangle
        #       2
        #   1      3
        self.ship_coordinate[0] = (center_x - (ship_width / 2), base_y)
        self.ship_coordinate[1] = (center_x, base_y + ship_height)
        self.ship_coordinate[2] = (center_x + (ship_width / 2), base_y)

        # the * can expand the variable to x and y
        x1, y1 = self.transform(*self.ship_coordinate[0])
        x2, y2 = self.transform(*self.ship_coordinate[1])
        x3, y3 = self.transform(*self.ship_coordinate[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinate)):
            ti_x, ti_y = self.tiles_coordinate[i]
            # No need to check the line_y above the ship
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collide_with_tile(ti_x, ti_y):
                return True
        # If all 3 points of ship out of tile, consider as collided and game over
        return False

    # Check the ship is still in the path
    def check_ship_collide_with_tile(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinate(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinate(ti_x + 1, ti_y + 1)
        # Enable two point of ship not in tile, but if 3 point not in tile, it is game over
        for i in range(0, 3):
            px, py = self.ship_coordinate[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def init_tile(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tile_coordinate(self):
        for i in range(0, 10):
            self.tiles_coordinate.append((0, i))

    def generate_tiles_coordinate(self):
        last_x = 0
        last_y = 0
        # Clean the tile which are out of screen
        # when ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinate) - 1, -1, -1):
            if self.tiles_coordinate[i][1] < self.current_y_loop:
                del self.tiles_coordinate[i]

            # Created new tile after deleting the old tile
            if len(self.tiles_coordinate) > 0:
                last_coordinate = self.tiles_coordinate[-1]
                last_y = last_coordinate[1] + 1
                last_x = last_coordinate[0]

        for i in range(len(self.tiles_coordinate), self.NB_TILES):
            # Generate the coordinate of tile
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            # Set up the border of tiles
            start_index = -int(self.V_NB_LINE / 2) + 1
            end_index = int(self.V_NB_LINE + start_index)
            if last_x >= end_index:
                r = 2
            if last_x <= start_index:
                r = 1
            self.tiles_coordinate.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinate.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinate.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinate.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinate.append((last_x, last_y))

            last_y += 1

    def get_tile_coordinate(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tile(self):
        for i in range(0, self.NB_TILES):
            # Create 'tile' to access all tile created in loop
            tile = self.tiles[i]
            # Access the x and y which appended into the tiles_coordinate list (tiles_coordinate[0] = x, [1]=y)
            # Access all the coordinates created in loop (self.tile_coordinate)
            tile_coordinates = self.tiles_coordinate[i]
            x_min, y_min = self.get_tile_coordinate(tile_coordinates[0], tile_coordinates[1])
            x_max, y_max = self.get_tile_coordinate(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            # Shape of tile
            #  2    3
            #
            # `1    4

            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)

            # Give the tile the coordinate of each other
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def init_vertical_line(self):
        with self.canvas:
            #  self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NB_LINE):
                self.vertical_line.append(Line())  # Created the no. of line required

    def get_line_x_from_index(self, index):
        central_x = self.perspective_point_x
        spacing = self.width * self.SPACING
        offset = index - 0.5
        line_x = central_x + spacing * offset + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing = self.SPACING_Y * self.height
        offset = index
        line_y = spacing * offset - self.current_offset_y
        return line_y

    def update_vertical_line(self):
        start_index = -int(self.V_NB_LINE / 2) + 1
        end_index = int(self.V_NB_LINE + start_index)
        #  self.line.points = [center_x, 0, center_x, 100]
        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_line[i].points = [x1, y1, x2, y2]

    def init_horizontal_line(self):
        with self.canvas:
            for i in range(0, self.H_NB_LINE):
                self.horizontal_line.append(Line())

    def update_horizontal_line(self):
        start_index = -int(self.V_NB_LINE / 2) + 1
        end_index = int(self.V_NB_LINE + start_index) - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINE):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_line[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        # dt should always follow the time, which is 1/60 but sometime depends on the condition of computer
        # Hence, if the other computer cannot afford calling the update function 60 time per sec
        # we need to speed up the speed of horizontal line to avoid being easy
        # the time factor should be 1 in normal condition(1 / 60 * 60)
        time_factor = dt * 60
        self.update_vertical_line()
        self.update_horizontal_line()
        self.update_tile()
        self.update_ship()

        if not self.game_over_state and self.game_has_started_state:
            speed_y = self.SPEED * self.height  # Create the relationship between speed and screen
            self.current_offset_y += speed_y * time_factor
            spacing_y = self.SPACING_Y * self.height

            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.generate_tiles_coordinate()
                # print("loop: " + str(self.current_y_loop))
                self.score_text = "SCORE: " + str(self.current_y_loop)

            speed_x = self.current_space_x * self.height
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.game_over_state:  # Print the game over state once
            self.menu_text = "G A M E   O V E R"
            self.menu_button_text = "RESTART"
            self.game_over_state = True
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.game_over_sound, 1)  # Delay the game over for 1 second
            # print("GAME OVER")

    def game_over_sound(self, dt):
        if self.game_over_state:
            self.sound_gameover_voice.play()

    def on_menu_button_press(self):
        if self.game_over_state:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        # print("Pressed")
        self.game_has_started_state = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
