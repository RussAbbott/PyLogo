
from __future__ import annotations

import PyLogo.core.gui as gui


class PixelVector:

    def __init__(self, x, y):
        """
        Wrap around the screen. x and y needn't be integers.
        """
        self.x = x
        self.y = y
        self.wrap()

    def __add__(self, other_pixel_vector: PixelVector):
        new_pixel_vector = PixelVector(self.x + other_pixel_vector.x, self.y + other_pixel_vector.y)
        return new_pixel_vector

    def __str__(self):
        return f'PixelVector{self.x, self.y}'

    def as_tuple(self):
        return (self.x, self.y)

    def wrap(self):
        screen_rect = gui.simple_gui.SCREEN.get_rect()
        # screen_rect = rect
        self.x = self.x % screen_rect.w
        self.y = self.y % screen_rect.h
        return self


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


def CENTER_PIXEL():
    from PyLogo.core.gui import simple_gui as simple_gui
    rect = simple_gui.SCREEN.get_rect()
    cp = PixelVector(round(rect.width/2), round(rect.height/2))
    return cp


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


def pixel_pos_to_row_col(pixel_pos: PixelVector):
    """
    Get the patch RowCol for this pixel_pos
    Leave a border of 1 pixel at the top and left of the patches
   """
    row = (pixel_pos.y - 1) // gui.BLOCK_SPACING()
    col = (pixel_pos.x - 1) // gui.BLOCK_SPACING()
    return RowCol(row, col)


def row_col_to_pixel_pos(row_col: RowCol):
    """
    Get the pixel position for this RowCol.
    Leave a border of 1 pixel at the top and left of the patches
    """
    pv = PixelVector(1 + gui.BLOCK_SPACING() * row_col.col, 1 + gui.BLOCK_SPACING() * row_col.row)
    return pv
