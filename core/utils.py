
from __future__ import annotations

from pygame.color import Color

import PyLogo.core.gui as gui
# noinspection PyUnresolvedReferences
import PyLogo.core.utils as utils

from functools import lru_cache
from math import copysign
from random import randint


class V2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, v: V2):
        xx = self.x + v.x
        yy = self.y + v.y
        cls = type(self)
        return cls(xx, yy)

    def __mul__(self, scalar):
        xx = self.x * scalar
        yy = self.y * scalar
        cls = type(self)
        return cls(xx, yy)

    def __sub__(self, v: V2):
        return self + v*(-1)

    def as_tuple(self):
        return (self.x, self.y)

    def as_int_tuple(self):
        return (int(self.x), int(self.y))

    def round(self, prec=2):
        clas = type(self)
        return clas(round(self.x, prec), round(self.y, prec))

    def wrap3(self, x_limit, y_limit):
        self.x = self.x % x_limit
        self.y = self.y % y_limit
        return self


class PixelVector(V2):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __str__(self):
        return f'PixelVector{self.x, self.y}'

    def distance_to(self, other):
        screen_width = gui.SCREEN_PIXEL_WIDTH()
        screen_height = gui.SCREEN_PIXEL_HEIGHT()
        end_pts = [((self + a + b).wrap3(screen_width, screen_height),      #.as_tuple(),
                    (other + a + b).wrap3(screen_width, screen_height)      #.as_tuple()
                    )
                   for a in [utils.PixelVector(0, 0), utils.PixelVector(screen_width/2, 0)]
                   for b in [utils.PixelVector(0, 0), utils.PixelVector(0, screen_height/2)]
                   ]
        dist = min(math.sqrt((start.x - end.x)**2 + (start.y - end.y)**2) for (start, end) in end_pts)
        return dist

    def wrap(self):
        screen_rect = gui.simple_gui.SCREEN.get_rect()
        wrapped = self.wrap3(screen_rect.w, screen_rect.h)
        return wrapped


class RowCol(V2):

    def __init__(self, row, col):
        super().__init__(row, col)
        # Wrap around the patch grid.
        self.wrap()

    def __str__(self):
        return f'RowCol{self.row, self.col}'

    @property
    def col(self):
        return int(self.y)

    @property
    def row(self):
        return int(self.x)

    def wrap(self):
        wrapped = self.wrap3(gui.PATCH_ROWS, gui.PATCH_COLS)
        return wrapped


class Velocity(V2):

    def __init__(self, dx, dy):
        super().__init__(dx, dy)

    def __str__(self):
        return f'Velocity{self.dx, self.dy}'

    # The @property decorator allows you to call the function without parentheses: v = Velocity(3, 4); v.dx -> 3
    # Inside the class must use self.dx, and self.dy.
    @property
    def dx(self):
        return self.x

    @property
    def dy(self):
        return self.y


# ###################### Start trig functions in degrees ###################### #
# import Python's trig functions, which are in radians. pi radians == 180 degrees
import math


# These functions expect their arguments in degrees.
def atan2(y, x):
    return radians_to_degrees(math.atan2(y, x))


def cos(x):
    return math.cos(degrees_to_radians(x))


def sin(x):
    return math.sin(degrees_to_radians(x))


def degrees_to_radians(degrees):
    return degrees*math.pi/180


def radians_to_degrees(radians):
    return radians*180/math.pi


# ###################### End trig functions in degrees ###################### #


def angle_to_heading(angle):
    """ Convert an angle to a heading. Same as heading to angle! """
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


@lru_cache(maxsize=360)
def dx(heading):
    angle = utils.heading_to_angle(heading)
    delta_x = utils.cos(angle)
    return delta_x


@lru_cache(maxsize=360)
def dy(heading):
    angle = utils.heading_to_angle(heading)
    delta_y = utils.sin(angle)
    # make it negative to account for inverted y axis
    return (-1)*delta_y


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
    angle = atan2(delta_y, delta_x)
    new_heading = utils.angle_to_heading(angle)
    return new_heading


def heading_to_angle(heading):
    """ Convert a heading to an angle """
    return normalize_angle_360(90 - heading)


@lru_cache(maxsize=360)
def heading_to_dxdy(heading) -> Velocity:
    """ Convert a heading to a (dx, dy) pair as a unit velocity """
    angle = heading_to_angle(heading)
    dx = cos(angle)
    # The -1 accounts for the y-axis being inverted.
    dy = (-1) * sin(angle)
    vel = Velocity(dx, dy)
    return vel


def normalize_angle_360(angle):
    return angle % 360


def normalize_angle_180(angle):
    """ Convert angle to the range (-180 .. 180]. """
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
    subtract heading b from heading a.
    To get from b to a we must turn b by a-b.

      a
     |
    |_____ b

    Since larger headings are to the right (clockwise), if (a-b) is negative, that means b is to the right of a,
    as in the diagram. So we must turn negatively, i.e., counter-clockwise.
    Similarly for positive results. a is to the right of b, i.e., clockwise.

    Normalize to values between -180 and +180 to ensure that larger numbers are to the right, i.e., clockwise.
    No jump from 360 to 0.
    """
    a_180 = utils.normalize_angle_180(a)
    b_180 = utils.normalize_angle_180(b)
    return a_180 - b_180


def turn_away_amount(old_heading, new_heading, max_turn):
    # If we reverse old_heading and new_heading, we are finding the direction new_heading
    # should turn to face more toward old_heading. But if old_heading turned that way
    # it would be turning away from new_heading.
    return turn_toward_amount(new_heading, old_heading, max_turn)


def turn_toward_amount(old_heading, new_heading, max_turn):
    # heading_delta will the amount old_heading should turn (positive or negative)
    # to face more in the direction of new_heading.
    heading_delta = utils.subtract_headings(new_heading, old_heading)
    # Take max_turn (an abs value) into consideration.
    # We want to turn the smaller (in absolute terms) of abs(heading_delta) and max_turn.
    # We want to turn in the direction indicated by the sign of heading_delta

    # copysign returns the first argument but with the sign of the second, i.e.,
    amount_to_turn = copysign(min(abs(heading_delta), max_turn), heading_delta)
    return (amount_to_turn)


if __name__ == "__main__":
    # Various tests and experiments
    pv = PixelVector(1.234, 5.678)
    print(pv.round(2))

    vel = Velocity(1.234, 5.678)
    print(vel.round(2))

    rc = RowCol(3, 4)
    print(rc.as_tuple())

    screen_width = gui.SCREEN_PIXEL_WIDTH()
    screen_height = gui.SCREEN_PIXEL_HEIGHT()
    v1 = utils.PixelVector(1, 1)
    v2 = utils.PixelVector(2, 2)
    print(v1.distance_to(v2))
    v3 = (v1 - v2).wrap3(screen_width, screen_height)
    print(v1.round(2), v2.round(2), v3.round(2))
    print(v1.distance_to(v3))
