
from __future__ import annotations

from math import atan2, cos, pi, sin

from pygame.color import Color
from pygame import Vector2

import PyLogo.core.gui as gui
# noinspection PyUnresolvedReferences
import PyLogo.core.utils as utils


from math import copysign
from random import randint


class V2(Vector2):

    def __add__(self, v: Vector2):
        # Returns a Vector2 because __add__ is done at that level
        sum: Vector2 = super().__add__(v)
        cls = type(self)
        new_inst = self.vector2_to_subclass(sum, cls)
        # new_pixel_vector: PixelVector = self.PV(sum)
        return new_inst

    def __mul__(self, scalar):
        # Returns a Vector2 because __mul__ is done at that level
        product: Vector2 = super().__mul__(scalar)
        cls = type(self)
        new_inst = self.vector2_to_subclass(product, cls)
        return new_inst

    def as_tuple(self):
        return (self.x, self.y)

    def as_int_tuple(self):
        return (int(self.x), int(self.y))

    def round(self, prec=2):
        clas = type(self)
        return clas(round(self.x, prec), round(self.y, prec))

    @staticmethod
    def vector2_to_subclass(v: Vector2, cls):
        return cls(v.x, v.y)

    def wrap3(self, x_limit, y_limit):
        self.x = self.x % x_limit
        self.y = self.y % y_limit
        return self



class PixelVector(V2):

    def __init__(self, x, y):
        # noinspection PyArgumentList
        super().__init__(x, y)

    # def __add__(self, velocity: utils.Velocity):
    #     # Returns a Vector2 because __add__ is done at that level
    #     sum: Vector2 = super().__add__(velocity)
    #     new_pixel_vector: PixelVector = self.PV(sum)
    #     return new_pixel_vector

    # def __eq__(self, other):
    #     """Override the default Equals behavior"""
    #     return self.x == other.x and self.y == other.y
    #
    # def __mul__(self, scalar):
    #     # Returns a Vector2 because __mul__ is done at that level
    #     product: Vector2 = super().__mul__(scalar)
    #     new_pixel_vector = self.PV(product)
    #     return new_pixel_vector

        # new_pixel_vector = PixelVector(scalar * self.x, scalar * self.y)
        # return new_pixel_vector
    #
    # def __ne__(self, other):
    #     """Override the default Unequal behavior"""
    #     return self.x != other.x or self.y != other.y

    # @staticmethod
    # def PV(v: Vector2):
    #     return PixelVector(v.x, v.y)
        # def __init__(self, v: Vector2):
        #     super().__init__(v.x, v.y)

    def __str__(self):
        return f'PixelVector{self.x, self.y}'

    # def as_tuple(self):
    #     return (self.x, self.y)
    #
    # def as_V2(self):
    #     return V2(self.x, self.y)
    #
    # def distance_to(self, xy: PixelVector):
    #     return sqrt((self.x - xy.x)**2 + (self.y - xy.y)**2)
    #
    # def round(self, prec=2):
    #     return PixelVector(round(self.x, prec), round(self.y, prec))

    def wrap(self):
        screen_rect = gui.simple_gui.SCREEN.get_rect()
        wrapped = self.wrap3(screen_rect.w, screen_rect.h)
        return wrapped

        # new_pixel_vector = PixelVector(self.x % screen_rect.w, self.y % screen_rect.h)
        # return new_pixel_vector


class RowCol(V2):

    def __init__(self, row, col):
        # noinspection PyArgumentList
        super().__init__(row, col)
        # Wrap around the patch grid.
        # self.row = row
        # self.col = col
        self.wrap()

    # def __add__(self, other_row_col: RowCol):
    #     new_row_col = RowCol(self.row + other_row_col.row, self.col + other_row_col.col)
    #     return new_row_col

    # def __add__(self, other_row_col: RowCol):
    #     # Returns a Vector2 because __add__ is done at that level
    #     sum: Vector2 = super().__add__(other_row_col)
    #     new_pixel_vector = self.PV(sum)
    #     return new_pixel_vector

    def __str__(self):
        return f'RowCol{self.row, self.col}'

    # def as_tuple(self):
    #     return (self.row, self.col)

    @property
    def col(self):
        return int(self.y)

    @property
    def row(self):
        return int(self.x)

    def wrap(self):
        wrapped = self.wrap3(gui.PATCH_ROWS, gui.PATCH_COLS)
        return wrapped
        # self.x = self.row % gui.PATCH_ROWS
        # self.y = self.col % gui.PATCH_COLS
        # return self


class Velocity(V2):

    def __init__(self, dx, dy):
        # noinspection PyArgumentList
        super().__init__(dx, dy)

    # def __add__(self, other_velocity: Velocity):
    #     new_velocity = Velocity(self.dx + other_velocity.dx, self.dy + other_velocity.dy)
    #     return new_velocity
    #
    # def __mul__(self, scalar):
    #     new_velocity = Velocity(scalar * self.dx, scalar * self.dy)
    #     return new_velocity

    def __str__(self):
        return f'Velocity{self.dx, self.dy}'

    # def as_tuple(self):
    #     return (self.dx, self.dy)

    # This decorator allows you to call the function without parentheses: v = Velocity(3, 4); v.dx -> 3
    # Inside the class must use self.dx, and self.dy.
    @property
    def dx(self):
        return self.x

    @property
    def dy(self):
        return self.y

    # def rounded(self):
    #     return Velocity(round(self.dx, 2), round(self.dy, 2))


def angle_to_heading(angle):
    """ Convert an angle to a heading """
    heading = heading_to_angle(angle)
    return heading


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


def color_random_variation(color: Color):
    # noinspection PyArgumentList
    new_color = Color(color.r+randint(-40, 0), color.g+randint(-40, 0), color.b+randint(0, 40), 255)
    return new_color


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


def heading_from_to(from_pixel: PixelVector, to_pixel: PixelVector):
    """ The heading to face from the from_pixel to the to_pixel """
    # Make the default heading 0 if from_pixel == to_pixel.
    if from_pixel == to_pixel:
        return 0
    delta_x = to_pixel.x - from_pixel.x
    # Subtract in reverse to compensate for the reversal of the y axis.
    delta_y = from_pixel.y - to_pixel.y
    atn2 = atan2(delta_y, delta_x)
    angle = (atn2 / (2 * pi)) * 360
    new_heading = utils.angle_to_heading(angle)
    return new_heading


def heading_to_angle(heading):
    """ Convert a heading to an angle """
    return normalize_angle_360(90 - heading)


def heading_to_dxdy(heading) -> Velocity:
    """ Convert a heading to a (dx, dy) pair as a unit velocity """
    # angle = normalize_angle_360(heading - 90) * (-1) * pi/180
    angle = heading_to_angle(heading) * pi/180  # Really 2*pi/360
    dx = cos(angle)
    # The -1 accounts for the y-axis being inverted.
    dy = (-1) * sin(angle)
    vel = Velocity(dx, dy)
    return vel


def normalize_angle_360(angle):
    return angle % 360


def normalize_angle_180(angle):
    normalized_angle = normalize_angle_360(angle)
    return normalized_angle if normalized_angle <= 180 else normalized_angle - 360


def row_col_to_center_pixel(row_col: RowCol) -> PixelVector:
    """
    Get the center_pixel position for this RowCol.
    Leave a border of 1 pixel at the top and left of the patches
    """
    pv = PixelVector(1 + gui.BLOCK_SPACING() * row_col.col + gui.HALF_PATCH_SIZE(),
                     1 + gui.BLOCK_SPACING() * row_col.row + gui.HALF_PATCH_SIZE())
    return pv


def subtract_headings(a, b):
    """
    subtract heading b from heading a
    Since larger headings are to the right (clockwise), if (a-b) is negative, that means b is to the right of a.
    To get from b to a we must turn to the left. Similarly for positive results.

    Normalize to values between -180 and +180 to ensure that larger numbers are to the right .
    """
    a_180 = utils.normalize_angle_180(a)
    b_180 = utils.normalize_angle_180(b)
    return a_180 - b_180


def turn_amount(turn, max_turn):
    # copysign returns the first argument but with the sign of the second.
    # copysign(x, y) = abs(x) * (y/abs(y))
    # turn_amount = min(abs(turn), max_turn) * (turn/abs(turn))
    return copysign(min(abs(turn), max_turn), turn)


def V_to_PV(v: Vector2) -> PixelVector:
    return PixelVector(v.x, v.y)


def V_to_Vel(v: Vector2) -> Velocity:
    return Velocity(v.x, v.y)


if __name__ == "__main__":
    pv = PixelVector(1.234, 5.678)
    print(pv.round(2))

    vel = Velocity(1.234, 5.678)
    print(vel.round(2))

    rc = RowCol(3, 4)
    print(rc.as_tuple())