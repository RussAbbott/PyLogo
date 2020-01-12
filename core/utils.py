
from __future__ import annotations

import PyLogo.core.gui as gui
# noinspection PyUnresolvedReferences
import PyLogo.core.utils as utils

from pygame.math import Vector2


class PixelVector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, velocity: utils.Velocity):
        new_pixel_vector = PixelVector(self.x + velocity.dx, self.y + velocity.dy)
        return new_pixel_vector

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        return self.x != other.x or self.y != other.y

    def __str__(self):
        return f'PixelVector{self.x, self.y}'

    def as_tuple(self):
        return (self.x, self.y)

    def wrap(self):
        screen_rect = gui.simple_gui.SCREEN.get_rect()
        new_pixel_vector = PixelVector(self.x % screen_rect.w, self.y % screen_rect.h)
        return new_pixel_vector


class RowCol:

    def __init__(self, row, col):
        # Wrap around the patch grid.
        self.row = row
        self.col = col
        self.wrap()

    def __add__(self, other_row_col: RowCol):
        new_row_col = RowCol(self.row + other_row_col.row, self.col + other_row_col.col)
        return new_row_col

    def __str__(self):
        return f'RowCol{self.row, self.col}'

    def as_tuple(self):
        return (self.row, self.col)

    def wrap(self):
        self.row = self.row % gui.PATCH_ROWS
        self.col = self.col % gui.PATCH_COLS
        return self


class Velocity:

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return f'Velocity{self.dx, self.dy}'

    def as_tuple(self):
        return (self.dx, self.dy)

    def rounded(self):
        return Velocity(round(self.dx, 2), round(self.dy, 2))


def angle_to_heading(angle):
    heading = heading_to_angle(angle)
    return heading


def extract_class_name(full_class_name: type):
    """
    full_class_name will be something like: <class 'PyLogo.core.static_values'>
    We return the str: static_values. Take the final segment [-1] after segmenting
    at '.' and then drop the final two characters [:-2].
    """
    return str(full_class_name).split('.')[-1][:-2]


def get_class_name(obj) -> str:
    """ Get the name of the object's class as a string. """
    full_class_name = type(obj)
    return extract_class_name(full_class_name)


def heading_to_angle(heading):
    return (90 - heading) % 360


def CENTER_PIXEL():
    rect = gui.simple_gui.SCREEN.get_rect()
    cp = PixelVector(rect.centerx, rect.centery)
    return cp


def center_pixel_to_row_col(center_pixel: PixelVector):
    """
    Get the patch RowCol for this pixel
   """
    row = center_pixel.y // gui.BLOCK_SPACING()
    col = center_pixel.x // gui.BLOCK_SPACING()
    return RowCol(int(row), int(col))


def row_col_to_center_pixel(row_col: RowCol):
    """
    Get the pixel position for this RowCol.
    Leave a border of 1 pixel at the top and left of the patches
    """
    pv = PixelVector(1 + gui.BLOCK_SPACING() * row_col.col + gui.HALF_PATCH_SIZE(),
                     1 + gui.BLOCK_SPACING() * row_col.row + gui.HALF_PATCH_SIZE())
    return pv


def V2(x, y):
    # noinspection PyArgumentList
    return Vector2(x, y)
