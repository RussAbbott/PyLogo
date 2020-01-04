
import PyLogo.core.static_values as static

from pygame.rect import Rect


class PixelVector2:

    def __init__(self, x, y):
        # Wrap around the screen.
        self._x = x
        self._y = y
        self.wrap()

    def __str__(self):
        return f'PixelVector2{self.x(), self.y()}'

    def as_tuple(self):
        return (self._x, self._y)

    def wrap(self):
        self._x = self.x() % SCREEN_RECT.w
        self._y = self.y() % SCREEN_RECT.h
        return self

    def x(self):
        return self._x

    def y(self):
        return self._y


class RowCol:

    def __init__(self, row, col):
        # Wrap around the patch field.
        self._row = row
        self._col = col
        self.wrap()

    def __str__(self):
        return f'PixelVector2{self._row(), self._col()}'

    def as_tuple(self):
        return (self._row, self._col)

    def col(self):
        return self._col

    def row(self):
        return self._row

    def wrap(self):
        self._row = self.row() if self.row() <= static.PATCH_ROWS else self.row() % PATCH_GRID_SHAPE.row()
        self._col = self.col() if self.col() <= static.PATCH_COLS else self.col() % PATCH_GRID_SHAPE.col()
        return self


SCREEN_RECT = Rect((0, 0), (static.SCREEN_PIXEL_WIDTH, static.SCREEN_PIXEL_HEIGHT))
PATCH_GRID_SHAPE = RowCol(static.PATCH_ROWS, static.PATCH_COLS)

CENTER_PIXEL = PixelVector2(round(SCREEN_RECT.width/2), round(SCREEN_RECT.height/2))


def extract_class_name(full_class_name: type):
    """
    full_class_name will be something like: <class '__main__.SimpleWorld_1'>
    We return the str: SimpleWorld_1
    """
    return str(full_class_name).split('.')[1][:-2]


def get_class_name(obj) -> str:
    """ Get the name of the object's class as a string. """
    full_class_name = type(obj)
    return extract_class_name(full_class_name)


def in_bounds_rc(r, c):
    return 0 <= r < PATCH_GRID_SHAPE.row() and 0 <= c < PATCH_GRID_SHAPE.col()


def pixel_pos_to_row_col(pixel_pos: PixelVector2):
    """
    Get the patch RowCol for this pixel_pos
    Leave a border of 1 pixel at the top and left of the patches
   """
    row = (pixel_pos.y() - 1) // static.BLOCK_SPACING
    col = (pixel_pos.x() - 1) // static.BLOCK_SPACING
    return RowCol(row, col)


def row_col_to_pixel_pos(row_col: RowCol):
    """
    Get the pixel position for this RowCol.
    Leave a border of 1 pixel at the top and left of the patches
    """
    pv = PixelVector2(1 + static.BLOCK_SPACING * row_col.col(), 1 + static.BLOCK_SPACING * row_col.row())
    return pv


def reset_ticks():
    # global static.TICKS
    static.TICKS = 0
