
from math import sqrt

import numpy as np

# Importing this file eliminates the need for a globals declaration
# noinspection PyUnresolvedReferences
import PyLogo.core.core_elements as core
import PyLogo.core.gui as gui
import PyLogo.core.utils as utils

from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface


WORLD = None  # The world


class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector but not necessarily a RowCol. Has a Color.
    """
    def __init__(self, center_pixel: utils.PixelVector, color=Color('black')):
        super().__init__()
        self.center_pixel = center_pixel
        self.rect = Rect(center_pixel.as_tuple(), (gui.PATCH_SIZE, gui.PATCH_SIZE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.color = color

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


class World:

    def __init__(self, patch_class, turtle_class):
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

    def create_ordered_turtles(self, n):
        """Create n Turtles with headings evenly spaced from 0 to 360"""
        for i in range(n):
            turtle = self.turtle_class()
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
        # Turtle.color_palette = choice([NETLOGO_PRIMARY_COLORS, PYGAME_COLORS])
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
