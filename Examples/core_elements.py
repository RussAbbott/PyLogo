
from __future__ import annotations

# from collections import namedtuple

import sim_engine as se

import numpy as np

# import pygame as pg

from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
# from pygame.time import Clock

# from PySimpleGUI import RGB


# # Global constants
# RowCol = namedtuple('RowCol', 'row col')
# PixelVector2 = namedtuple('PixelVector2', 'x y')
#
# # Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
# BLOCK_SIDE = 15
# BLOCK_SPACING = BLOCK_SIDE + 1
#

class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector2 but not necessarily a RowCol. Has a Color.
    """

    def __init__(self, pixel_pos: se.PixelVector2, color=Color('black')):
        super().__init__()
        self.color = color
        self.pixel_pos: se.PixelVector2 = pixel_pos
        self.rect = Rect((self.pixel_pos.x, self.pixel_pos.y), (se.BLOCK_SIDE, se.BLOCK_SIDE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.image.fill(color)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        

class Patch(Block):
    def __init__(self, row_col: se.RowCol, color=Color('black')):
        super().__init__(se.WORLD.row_col_to_pixel_pos(row_col), color)
        self.row_col = row_col
        self.turtles = set()

    def add_turtle(self, tur):
        self.turtles.add(tur)

    def neighbors_4(self):
        return self._neighbors()

    def neighbors_8(self):
        return self._neighbors(extra_deltas=((-1, -1), (-1, 1), (1, -1), (1, 1)))

    def _neighbors(self, extra_deltas=()):
        """
        The 4 or 8 neighbors of this patch.
        Must use an empty tuple, rather than an empty list, for the default extra_deltas.
        Default arguments may not be mutable.
        """
        # The initial cardinal_deltas are the cardinal directions: N, S, E, W
        cardinal_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1))
        # The extra_deltas, if given are the corner directions.
        rc_deltas = cardinal_deltas + extra_deltas
        (row, col) = self.row_col
        neighbs = [se.WORLD.patches[row+r, col+c]
                   for (r, c) in rc_deltas if se.in_bounds(row+r, col+c)]
        return neighbs

    def remove_turtle(self, tur):
        self.turtles.remove(tur)

    def __str__(self):
        class_name = se.get_class_name(self)
        return f'{class_name}{(self.row_col.row, self.row_col.col)} at {(self.pixel_pos.x, self.pixel_pos.y)}'


class Turtle(Block):
    def __init__(self,
                 pixel_pos: se.PixelVector2 = se.PixelVector2(25*se.BLOCK_SPACING-1, 25*se.BLOCK_SPACING-1),
                 color=Color('red')):
        super().__init__(pixel_pos, color)
        se.WORLD.turtles.add(self)
        self.patch().add_turtle(self)
        self.vel = se.PixelVector2(0, 0)


    def move_turtle(self, wrap):
        pass

    def move_by_dxdy(self, dxdy: se.PixelVector2):
        """
        Move to self.pixel_pos + (dx, dy)
        """
        self.move_to_xy(se.PixelVector2(self.pixel_pos.x + dxdy.x, self.pixel_pos.y + dxdy.y))

    def move_by_vel(self, bounce):
        if bounce:
            # Bounce turtle off the screen edges
            screen_rect = se.SCREEN_RECT
            turtle_rect = self.rect
            margin = se.BLOCK_SIDE*0.1
            if turtle_rect.right >= screen_rect.right - margin or turtle_rect.left <= screen_rect.left + margin:
                self.vel = self.vel._replace(x=self.vel.x * (-1))
            if turtle_rect.top <= screen_rect.top + margin or turtle_rect.bottom >= screen_rect.bottom - margin:
                self.vel = self.vel._replace(y=self.vel.y * (-1))
        self.move_by_dxdy(self.vel)

    def move_to_xy(self, xy: se.PixelVector2):
        """
        Removes this turtle from the list of turtles at its current patch.
        Move this turtle to its new xy pixel_pos.
        Adds this turtle to the list of turtles in its new patch.
        Then calls SIM_ENGINE.place_turtle_on_screen(turtle) to place it on the screen.
        SIM_ENGINE.place_turtle_on_screen() wraps around if necessary.
        """
        current_patch: Patch = self.patch()
        current_patch.remove_turtle(self)
        self.pixel_pos = xy
        se.place_turtle_on_screen(self)
        new_patch = self.patch()
        new_patch.add_turtle(self)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.pixel_pos)

    def patch(self) -> Patch:
        (row, col) = se.WORLD.pixel_pos_to_row_col(self.pixel_pos)
        patch = se.WORLD.patches[row, col]
        return patch

    def __str__(self):
        class_name = se.get_class_name(self)
        return f'{class_name}{(self.pixel_pos.x, self.pixel_pos.y)} on {self.patch()}'


class World:

    def __init__(self, patch_class=Patch, turtle_class=Turtle):
        se.WORLD = self

        self.patch_class = patch_class
        self.turtle_class = turtle_class

        self.patches = None

        self.create_patches()

        self.turtles = set()

        self.patches_shape = se.patch_grid_shape

        self.center_pixels = se.CENTER_PIXELS

    def clear_all(self):
        self.turtles = set()

    def create_patches(self):
        patch_grid_shape = se.patch_grid_shape
        patches_temp_array = np.array([self.patch_class(se.RowCol(r, c))
                                       for r in range(patch_grid_shape.row)
                                       for c in range(patch_grid_shape.col)])
        self.patches: np.ndarray = patches_temp_array.reshape(patch_grid_shape)

    def done(self):
        return False

    def draw(self, screen):
        for patch in self.patches.flat:
            patch.draw(screen)
        for turtle in self.turtles:
            turtle.draw(screen)

    def final_thoughts(self):
        """ Add any final tests, data gathering, or summarization here. """
        pass

    @staticmethod
    def pixel_pos_to_row_col(pixel_pos: se.PixelVector2):
        """
        Get the patch RowCol for this pixel_pos
        Leave a border of 1 pixel at the top and left of the patches
       """
        row = (pixel_pos.y - 1) // se.BLOCK_SPACING
        col = (pixel_pos.x - 1) // se.BLOCK_SPACING
        return se.RowCol(row, col)

    @staticmethod
    def reset_ticks():
        se.reset_ticks()

    @staticmethod
    def row_col_to_pixel_pos(row_col: se.RowCol):
        """
        Get the pixel position for this RowCol.
        Leave a border of 1 pixel at the top and left of the patches
        """
        return se.PixelVector2(1 + se.BLOCK_SPACING*row_col.col, 1 + se.BLOCK_SPACING*row_col.row)

    def setup(self, values):
        self.clear_all()
        self.create_patches()
        se.reset_ticks()

    def step(self, event, values):
        """
        Update the world. Override for each world
        """
        pass


# class SimEngine:
#     """
#     The engine that runs the simulation.
#     """
#
#     pass
#
#     # # These are globally available as se.SIM_ENGINE and se.WORLD
#     # SIM_ENGINE = None  # The SimEngine object
#     # WORLD = None       # The world
#     #
#     # SCREEN_RECT = None
#     # CENTER_PIXELS = None
#     #
#     # CLOCK = None
#     # TICKS = None
#
#     # def __init__(self, patch_grid_shape=se.RowCol(51, 51)):
#         # se.SIM_ENGINE = self
#         #
#         # se.TICKS = 0
#         # self.patch_grid_shape = patch_grid_shape
#         # self.screen_color = Color(RGB(50, 60, 60))
#         # se.CLOCK = Clock()
#
#     # # Fill the screen with the background color, then: draw patches, draw turtles on top, update the display.
#     # def draw(self, screen):
#     #     screen.fill(self.screen_color)
#     #     se.WORLD.draw(screen)
#     #     pg.display.update()
#
#     # @staticmethod
#     # def extract_class_name(full_class_name: type):
#     #     """
#     #     full_class_name will be something like: <class '__main__.SimpleWorld_1'>
#     #     We return the str: SimpleWorld_1
#     #     """
#     #     return str(full_class_name).split('.')[1][:-2]
#     #
#     # @staticmethod
#     # def get_class_name(obj) -> str:
#     #     """ Get the name of the object's class as a string. """
#     #     full_class_name = type(obj)
#     #     return se.extract_class_name(full_class_name)
#     #
#     # def in_bounds(self, r, c):
#     #     return 0 <= r < self.patch_grid_shape.row and 0 <= c < self.patch_grid_shape.col
#     #
#     # @staticmethod
#     # def place_turtle_on_screen(turtle):
#     #     # Wrap around the screen.
#     #     turtle.pixel_pos = se.PixelVector2(turtle.pixel_pos.x % se.SCREEN_RECT.w,
#     #                                        turtle.pixel_pos.y % se.SCREEN_RECT.h)
#     #     turtle.rect = Rect((turtle.pixel_pos.x, turtle.pixel_pos.y), (se.BLOCK_SIDE, se.BLOCK_SIDE))
#     #
#     # @staticmethod
#     # def reset_ticks():
#     #     se.TICKS = 0
#     #     # global TICKS
#     #     # TICKS = 0
