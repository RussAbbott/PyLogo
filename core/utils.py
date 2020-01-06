
from __future__ import annotations

import PyLogo.core.static_values as static

from pygame.rect import Rect


class PixelVector2:

    def __init__(self, x, y):
        # Wrap around the screen.
        self.x = x
        self.y = y
        self.wrap()

    def __str__(self):
        return f'PixelVector2{self.x, self.y}'

    def as_tuple(self):
        return (self.x, self.y)

    def wrap(self):
        self.x = self.x % SCREEN_RECT.w
        self.y = self.y % SCREEN_RECT.h
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
        self.row = self.row % static.PATCH_ROWS
        self.col = self.col % static.PATCH_COLS
        return self


# These must be here to avoid a circular import. This definition of SCREEN_RECT is temporary.
# It is defined now to allow the definition of CENTER_PIXEL. When the screen is created
# The actual screen_rect is substituted for this.
SCREEN_RECT = Rect((0, 0), (static.SCREEN_PIXEL_WIDTH(), static.SCREEN_PIXEL_HEIGHT()))


def CENTER_PIXEL():
    cp = PixelVector2(round(SCREEN_RECT.width/2), round(SCREEN_RECT.height/2))
    # print(SCREEN_RECT, cp)
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


def pixel_pos_to_row_col(pixel_pos: PixelVector2):
    """
    Get the patch RowCol for this pixel_pos
    Leave a border of 1 pixel at the top and left of the patches
   """
    row = (pixel_pos.y - 1) // static.BLOCK_SPACING()
    col = (pixel_pos.x - 1) // static.BLOCK_SPACING()
    return RowCol(row, col)


def row_col_to_pixel_pos(row_col: RowCol):
    """
    Get the pixel position for this RowCol.
    Leave a border of 1 pixel at the top and left of the patches
    """
    pv = PixelVector2(1 + static.BLOCK_SPACING() * row_col.col, 1 + static.BLOCK_SPACING() * row_col.row)
    # print(f'{row_col} -> {pv}')
    return pv


def reset_ticks():
    static.TICKS = 0
