
from math import atan2, cos, pi, sin, sqrt

import numpy as np

from pygame.colordict import THECOLORS

# Importing this file eliminates the need for a globals declaration
import PyLogo.core.core_elements as core
import PyLogo.core.gui as gui
import PyLogo.core.utils as utils

from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

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

NETLOGO_PRIMARY_COLORS = [Color('gray'), Color('red'), Color('orange'), Color('brown'), Color('yellow'),
                          Color('green'), Color('limegreen'), Color('turquoise'), Color('cyan'),
                          Color('skyblue3'), Color('blue'), Color('violet'), Color('magenta'), Color('pink')]


WORLD = None  # The world


class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector but not necessarily a RowCol. Has a Color.
    """

    def __init__(self, pixel_pos: utils.PixelVector, color=Color('black')):
        super().__init__()
        self.color = color
        self.pixel_pos = pixel_pos
        self.rect = Rect((self.pixel_pos.x, self.pixel_pos.y), (gui.PATCH_SIZE, gui.PATCH_SIZE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.image.fill(color)

    def distance_to_xy(self, xy: utils.PixelVector):
        x_dist = self.pixel_pos.x - xy.x
        y_dist = self.pixel_pos.y - xy.y
        dist = sqrt(x_dist * x_dist + y_dist*y_dist)
        return dist
        
    def draw(self):
        gui.simple_gui.SCREEN.blit(self.image, self.rect)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        

class Patch(Block):
    def __init__(self, row_col: utils.RowCol, color=Color('black')):
        super().__init__(utils.row_col_to_pixel_pos(row_col), color)
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
        neighbors = [core.WORLD.patches[(self.row_col + utils.RowCol(r, c)).as_tuple()] for (r, c) in deltas]
        return neighbors

    def remove_turtle(self, turtle):
        self.turtles.remove(turtle)


class Turtle(Block):
    def __init__(self, pixel_pos: utils.PixelVector = None, color=None):
        if color is None:
            # Select a color at random from among NETLOGO_PRIMARY_COLORS or PYGAME_COLORS
            
            # color = choice(NETLOGO_PRIMARY_COLORS)
            color = choice(PYGAME_COLORS)
        if pixel_pos is None:
            pixel_pos = utils.CENTER_PIXEL()
        super().__init__(pixel_pos, color)
        core.WORLD.turtles.add(self)
        self.current_patch().add_turtle(self)
        self.heading = 0
        self.speed = 1
        self.velocity = utils.PixelVector(0, 0)

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}{(self.pixel_pos.x, self.pixel_pos.y, self.heading)} on {self.current_patch()}'

    def bounce_off_screen_edge(self):
        """ 
       Bounce turtle off the screen edges 
       """
        sc_rect = gui.simple_gui.SCREEN.get_rect( )
        t_rect = self.rect
        t_vel = self.velocity
        if sc_rect.right < t_rect.right and t_vel.x > 0 or t_rect.left < sc_rect.left and t_vel.x < 0:
            self.velocity = utils.PixelVector(t_vel.x * (-1), t_vel.y)
            while sc_rect.right < t_rect.right or t_rect.left < sc_rect.left:
                self.move_by_dxdy(self.velocity)
                t_rect = self.rect
        if t_rect.bottom > sc_rect.bottom and t_vel.y > 0 or t_rect.top < sc_rect.top and t_vel.y < 0:
            self.velocity = utils.PixelVector(t_vel.x, t_vel.y * (-1))
            while t_rect.bottom > sc_rect.bottom or t_rect.top < sc_rect.top:
                self.move_by_dxdy(self.velocity)
                t_rect = self.rect

    def current_patch(self) -> Patch:
        (row, col) = utils.pixel_pos_to_row_col(self.pixel_pos).as_tuple()
        patch = core.WORLD.patches[row, col]
        return patch

    def face_xy(self, xy: utils.PixelVector):
        delta_x = max(1, xy.x - self.pixel_pos.x)
        delta_y = xy.y - self.pixel_pos.y
        self.heading = atan2(delta_y, delta_x) * 2 * pi

    def forward(self, speed=None):
        if speed is None:
            speed = self.speed
        angle = pi * (((self.heading - 90)*(-1) + 360) % 360) / 180
        # dx and dy must be integers. They are the number of pixels to move.
        dx = cos(angle) * speed
        dy = (-1)*sin(angle) * speed
        # print(self.heading, angle, speed, dx, dy)
        self.move_by_dxdy(utils.PixelVector(dx, dy))

    def move_turtle(self, wrap):
        pass

    def move_by_dxdy(self, dxdy: utils.PixelVector):
        """
        Move to self.pixel_pos + (dx, dy)
        """
        self.move_to_xy(utils.PixelVector(self.pixel_pos.x + dxdy.x, self.pixel_pos.y + dxdy.y))

    def move_by_velocity(self, bounce):
        if bounce:
            self.bounce_off_screen_edge( )
        self.move_by_dxdy(self.velocity)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.pixel_pos)

    def move_to_xy(self, xy: utils.PixelVector):
        """
        Remove this turtle from the list of turtles at its current patch.
        Move this turtle to its new xy pixel_pos.
        Add this turtle to the list of turtles in its new patch.
        """
        current_patch: Patch = self.current_patch()
        current_patch.remove_turtle(self)
        self.pixel_pos = xy
        self.rect = Rect((round(self.pixel_pos.x), round(self.pixel_pos.y)), (gui.PATCH_SIZE, gui.PATCH_SIZE))
        new_patch = self.current_patch()
        new_patch.add_turtle(self)

    def turn_left(self, delta_angles):
        self.turn_right(-delta_angles)

    def turn_right(self, delta_angles):
        self.heading = (self.heading + delta_angles + 360) % 360


class World:

    def __init__(self, patch_class=Patch, turtle_class=Turtle):
        core.WORLD = self

        self.TICKS = 0

        self.patch_class = patch_class
        self.patches: np.ndarray = self.create_patches( )


        self.turtle_class = turtle_class
        self.turtles = set()

    def create_patches(self):
        # self.patches: np.ndarray = np.ndarray([])
        patch_pseudo_array = [[self.patch_class(utils.RowCol(r, c)) for c in range(gui.PATCH_COLS)]
                              for r in range(gui.PATCH_ROWS)]
        return np.array(patch_pseudo_array)

    def clear_all(self):
        self.turtles = set()

    @staticmethod
    def create_ordered_turtles(n):
        """Create n Turtles with headings evenly spaced from 0 to 360"""
        for i in range(n):
            angle = i*360/n
            turtle = Turtle()
            turtle.heading = angle

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

    def increment_ticks(self):
        self.TICKS += 1

    def reset_all(self):
        self.clear_all()
        self.reset_ticks()
        self.patches = self.create_patches( )

    def reset_ticks(self):
        self.TICKS = 0

    def setup(self, values):
        pass

    def step(self, event, values):
        """
        Update the world. Override for each world
        """
        pass
