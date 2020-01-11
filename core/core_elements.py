
from math import atan2, cos, pi, sin, sqrt

import numpy as np

# Importing this file eliminates the need for a globals declaration
# noinspection PyUnresolvedReferences
import PyLogo.core.core_elements as core
import PyLogo.core.gui as gui
import PyLogo.core.utils as utils

import pygame as pg
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
import pygame.transform as pgt

from random import choice

from typing import Tuple


def is_acceptable_color(rgb: Tuple[int, int, int]):
    """
    Require reasonably bright colors for which r, g, and b are not too close to each other.
    """
    sum_rgb = sum(rgb)
    avg_rgb = sum_rgb/3
    return 150 <= sum_rgb and sum(abs(avg_rgb-x) for x in rgb) > 100


# These are colors defined by pygame that satisfy is_acceptable_color above.
PYGAME_COLORS = [rgba for rgba in THECOLORS.values() if is_acceptable_color(rgba[:3])]

# These are NetLogo primary colors.
NETLOGO_PRIMARY_COLORS = [Color('gray'), Color('red'), Color('orange'), Color('brown'), Color('yellow'),
                          Color('green'), Color('limegreen'), Color('turquoise'), Color('cyan'),
                          Color('skyblue3'), Color('blue'), Color('violet'), Color('magenta'), Color('pink')]


WORLD = None  # The world


class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector but not necessarily a RowCol. Has a Color.
    """
    def __init__(self, center_pixel: utils.PixelVector, color=Color('black')):
        super().__init__()
        self.center_pixel = center_pixel
        self.rect = Rect((self.center_pixel.x - gui.HALF_PATCH_SIZE(), self.center_pixel.y - gui.HALF_PATCH_SIZE()),
                         (gui.PATCH_SIZE, gui.PATCH_SIZE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.color = color
        # self.image.fill(color)

    def distance_to_xy(self, xy: utils.PixelVector):
        x_dist = self.center_pixel.x - xy.x
        y_dist = self.center_pixel.y - xy.y
        dist = sqrt(x_dist * x_dist + y_dist*y_dist)
        return dist
        
    def draw(self):
        gui.simple_gui.SCREEN.blit(self.image, self.rect)


    @staticmethod
    def get_gui_value(key):
        return WORLD.get_gui_value(key)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        

class Patch(Block):
    def __init__(self, row_col: utils.RowCol, color=Color('black')):
        super().__init__(utils.row_col_to_center_pixel(row_col), color)
        self.row_col = row_col
        self.turtles = set()
        self._neighbors_4 = None
        self._neighbors_8 = None

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}{(self.row_col.row, self.row_col.col)}'

    def add_turtle(self, tur):
        self.turtles.add(tur)

    def neighbors_4(self):
        if self._neighbors_4 is None:
            cardinal_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1))
            self._neighbors_4 = self.neighbors(cardinal_deltas)
        return self._neighbors_4

    def neighbors_8(self):
        if self._neighbors_8 is None:
            all_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
            self._neighbors_8 = self.neighbors(all_deltas)
        return self._neighbors_8

    def neighbors(self, deltas):
        """
        The neighbors of this patch determined by the deltas.
        Note the addition of two RowCol objects to produce a new RowCol object: self.row_col + utils.RowCol(r, c).
        Wrap around is handled by RowCol. We then turn the RowCol object to a tuple to access the np.ndarray
        """
        neighbors = [WORLD.patches[(self.row_col + utils.RowCol(r, c)).as_tuple( )] for (r, c) in deltas]
        return neighbors

    def remove_turtle(self, turtle):
        self.turtles.remove(turtle)


class Turtle(Block):

    color_palette = None

    id = 0

    def __init__(self, center_pixel: utils.PixelVector = None, color=None):
        if color is None:
            # Select a color at random from the color_palette
            # Turtle.color_palette is set during World.setup().
            color = choice(Turtle.color_palette)

        # Can't make this a default value because it isn't defined when the default values is compiled
        if center_pixel is None:
            center_pixel = utils.CENTER_PIXEL()

        super().__init__(center_pixel, color)
        self.original_image = Surface((self.rect.w, self.rect.h))
        # self.original_image.set_alpha(0)

        pg.draw.polygon(self.original_image,
                        self.color,
                        [utils.V2(gui.PATCH_SIZE, gui.PATCH_SIZE),
                         utils.V2(gui.HALF_PATCH_SIZE( ), 0),
                         utils.V2(0, gui.PATCH_SIZE),
                         utils.V2(gui.HALF_PATCH_SIZE( ), gui.PATCH_SIZE*3/4),
                         ])

        self.image = self.original_image

        Turtle.id += 1
        self.id = Turtle.id
        WORLD.turtles.add(self)
        self.current_patch().add_turtle(self)
        self.heading = 0
        self.speed = 1
        self.set_velocity(utils.Velocity(0, 0))

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}-{self.id}. pixel: {(self.center_pixel.x, self.center_pixel.y)}, heading: {self.heading}'

    def bounce_off_screen_edge(self, dxdy):
        """
       Bounce turtle off the screen edges
       """
        sc_rect = gui.simple_gui.SCREEN.get_rect()
        center_pixel = self.center_pixel
        next_center_pixel = center_pixel + dxdy
        if next_center_pixel.x <= sc_rect.left <= center_pixel.x or \
            center_pixel.x <= sc_rect.right <= next_center_pixel.x:
            dxdy = utils.Velocity(dxdy.dx*(-1), dxdy.dy)

        if next_center_pixel.y <= sc_rect.top <= center_pixel.y or \
            center_pixel.y <= sc_rect.bottom <= next_center_pixel.y:
            dxdy = utils.Velocity(dxdy.dx, dxdy.dy*(-1))

        return dxdy

    def current_patch(self) -> Patch:
        row_col: utils.RowCol = utils.center_pixel_to_row_col(self.center_pixel)
        patch = WORLD.patches[row_col.row, row_col.col]
        return patch

    def face_xy(self, xy: utils.PixelVector):
        delta_x = xy.x - self.center_pixel.x
        # Subtract in reverse to compensate for the reversal of the y axis.
        delta_y = self.center_pixel.y - xy.y
        atn2 = atan2(delta_y, delta_x)
        angle = (atn2 / (2 * pi) ) * 360
        self.set_heading(utils.angle_to_heading(angle))

    def forward(self, speed=None):
        if speed is None:
            speed = self.speed
        angle = pi * (((self.heading - 90)*(-1) + 360) % 360) / 180
        dx = cos(angle) * speed
        dy = (-1)*sin(angle) * speed
        self.move_by_dxdy(utils.Velocity(dx, dy))

    def move_turtle(self, wrap):
        pass

    def move_by_dxdy(self, dxdy: utils.Velocity):
        """
        Move to self.center_pixel + (dx, dy)
        """
        if self.get_gui_value('Bounce?'):
            new_dxdy = self.bounce_off_screen_edge(dxdy)
            if dxdy is self.velocity:
                self.set_velocity(new_dxdy)
            dxdy = new_dxdy
        self.move_to_xy(self.center_pixel + dxdy)

    def move_by_velocity(self):
        self.move_by_dxdy(self.velocity)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.center_pixel)

    def move_to_xy(self, xy: utils.PixelVector):
        """
        Remove this turtle from the list of turtles at its current patch.
        Move this turtle to its new xy center_pixel.
        Add this turtle to the list of turtles in its new patch.
        """
        current_patch: Patch = self.current_patch()
        current_patch.remove_turtle(self)
        self.center_pixel: utils.PixelVector = xy.wrap()
        r = self.rect
        (r.x, r.y) = (self.center_pixel.x-gui.HALF_PATCH_SIZE(), self.center_pixel.y-gui.HALF_PATCH_SIZE())
        new_patch = self.current_patch( )
        new_patch.add_turtle(self)

    def set_heading(self, angle):
        self.heading = angle
        self.image = self.original_image
        self.image = pgt.rotate(self.image, -angle)
        # self.image = pgt.scale2x(self.image)
        # self.image = pgt.rotozoom(self.image, -angle, 2)

    def turn_left(self, delta_angles):
        self.turn_right(-delta_angles)

    def turn_right(self, delta_angles):
        self.set_heading((self.heading + delta_angles + 360) % 360)

    def set_velocity(self, velocity):
        self.velocity = velocity
        self.face_xy(self.center_pixel + velocity)


class World:

    def __init__(self, patch_class=Patch, turtle_class=Turtle):
        core.WORLD = self

        self.event = None
        self.values = None

        self.TICKS = 0

        self.patch_class = patch_class
        self.patches: np.ndarray = self.create_patches( )


        self.turtle_class = turtle_class
        self.turtles = set()

    def create_patches(self):
        patch_pseudo_array = [[self.patch_class(utils.RowCol(r, c)) for c in range(gui.PATCH_COLS)]
                              for r in range(gui.PATCH_ROWS)]
        return np.array(patch_pseudo_array)

    def clear_all(self):
        self.turtles = set()

    @staticmethod
    def create_ordered_turtles(n):
        """Create n Turtles with headings evenly spaced from 0 to 360"""
        for i in range(n):
            turtle = Turtle()
            angle = i*360/n
            turtle.set_heading(angle)

    def done(self):
        return False

    def draw(self):
        for patch in self.patches.flat:
            patch.draw()

        for turtle in self.turtles:
            turtle.draw()

    def final_thoughts(self):
        """ Add any final tests, data gathering, summarization, etc. here. """
        pass

    @staticmethod
    def get_gui_value(key):
        value = core.WORLD.values.get(key, None)
        return int(value) if isinstance(value, float) and value == int(value) else value

    def increment_ticks(self):
        self.TICKS += 1

    def reset_all(self):
        self.clear_all()
        self.reset_ticks()
        self.patches = self.create_patches( )

    def reset_ticks(self):
        self.TICKS = 0

    def save_values_and_setup(self, event, values):
        self.event = event
        self.values = values
        Turtle.color_palette = choice([NETLOGO_PRIMARY_COLORS, PYGAME_COLORS])
        self.setup()

    def setup(self):
        pass

    def save_values_and_step(self, event, values):
        self.event = event
        self.values = values
        self.step()

    def step(self):
        """
        Update the world. Override for each world
        """
        pass
