
from __future__ import annotations

from pygame.color import Color

import PyLogo.core.gui as gui
# noinspection PyUnresolvedReferences
import PyLogo.core.utils as utils

from functools import lru_cache
from math import copysign
from random import randint


class XY:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, xy: XY):
        xx = self.x + xy.x
        yy = self.y + xy.y
        cls = type(self)
        return cls(xx, yy)

    def __div__(self, scalar):
        return self * (1/scalar)

    def __mul__(self, scalar):
        xx = self.x * scalar
        yy = self.y * scalar
        cls = type(self)
        return cls(xx, yy)

    def __sub__(self, xy: XY):
        return self + xy*(-1)

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


class Pixel_xy(XY):

    def __init__(self, x, y):
        super().__init__(x, y)

    def __str__(self):
        return f'Pixel_xy{self.x, self.y}'

    def distance_to(self, other, wrap):
        # Try all ways to get there including wrapping around.
        # wrap = not World.THE_WORLD.get_gui_value('bounce')
        # Can't do this directly since importing World would be circular
        end_pts = [(self, other)]
        if wrap:
            screen_width = gui.SCREEN_PIXEL_WIDTH()
            screen_height = gui.SCREEN_PIXEL_HEIGHT()
            wrapped_end_pts = [((self+a+b).wrap3(screen_width, screen_height),
                                (other+a+b).wrap3(screen_width, screen_height))
                               for a in [utils.Pixel_xy_00, utils.Pixel_xy(screen_width/2, 0)]
                               for b in [utils.Pixel_xy_00, utils.Pixel_xy(0, screen_height/2)]
                               ]
            end_pts += wrapped_end_pts
        dist = min(math.sqrt((start.x - end.x)**2 + (start.y - end.y)**2) for (start, end) in end_pts)
        return dist

    def heading_toward(self, to_pixel: Pixel_xy):
        """ The heading to face from the from_pixel to the to_pixel """
        # Make the default heading 0 if from_pixel == to_pixel.
        if self == to_pixel:
            return 0
        delta_x = to_pixel.x - self.x
        delta_y = to_pixel.y - self.y
        new_heading = utils.dxdy_to_heading(delta_x, delta_y, default_heading=0)
        return new_heading

    def pixel_to_patch(self: Pixel_xy):
        """
        Get the patch RowCol for this pixel
       """
        row = self.y // gui.BLOCK_SPACING()
        col = self.x // gui.BLOCK_SPACING()
        return RowCol(int(row), int(col))

    def wrap(self):
        screen_rect = gui.simple_gui.SCREEN.get_rect()
        wrapped = self.wrap3(screen_rect.w, screen_rect.h)
        return wrapped


utils.Pixel_xy_00 = utils.Pixel_xy(0, 0)


class RowCol(XY):

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

    def patch_to_center_pixel(self) -> Pixel_xy:
        """
        Get the center_pixel position for this RowCol.
        Leave a border of 1 pixel at the top and left of the patches
        """
        pv = Pixel_xy(1 + gui.BLOCK_SPACING() * self.col + gui.HALF_PATCH_SIZE(),
                      1 + gui.BLOCK_SPACING() * self.row + gui.HALF_PATCH_SIZE())
        return pv

    def wrap(self):
        wrapped = self.wrap3(gui.PATCH_ROWS, gui.PATCH_COLS)
        return wrapped


class Velocity(XY):

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
# These functions expect their arguments in degrees.
import math


def atan2(y, x):
    xy_max = max(abs(x), abs(y))
    (y_n, x_n) = (int(round(100*y/xy_max)), int(round(100*x/xy_max)))
    return atan2_normalized(y_n, x_n)


@lru_cache(maxsize=1024)
def atan2_normalized(y, x):
    return radians_to_degrees(math.atan2(y, x))


def cos(x):
    return _cos_int(normalize_360(x))


@lru_cache(maxsize=512)
def _cos_int(x):
    return math.cos(degrees_to_radians(x))


def sin(x):
    return _sin_int(normalize_360(x))


@lru_cache(maxsize=512)
def _sin_int(x):
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


def center_pixel():
    rect = gui.simple_gui.SCREEN.get_rect()
    cp = Pixel_xy(rect.centerx, rect.centery)
    return cp


def color_random_variation(color: Color):
    # noinspection PyArgumentList
    new_color = Color(color.r+randint(-40, 0), color.g+randint(-40, 0), color.b+randint(0, 40), 255)
    return new_color


def dxdy_to_heading(dx, dy, default_heading=None):
    if dx == 0 == dy:
        return default_heading
    else:
        # (-1) to compensate for inverted y-axis.
        angle = utils.atan2((-1) * dy, dx)
        new_heading = utils.angle_to_heading(angle)
        return new_heading


def dx(heading):
    return _dx_int(heading)


@lru_cache(maxsize=512)
def _dx_int(heading):
    angle = utils.heading_to_angle(heading)
    delta_x = utils.cos(angle)
    return delta_x


def dy(heading):
    return _dy_int(heading)


@lru_cache(maxsize=512)
def _dy_int(heading):
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


def heading_to_angle(heading):
    """ Convert a heading to an angle """
    return normalize_360(90 - heading)


def heading_to_dxdy(heading) -> Velocity:
    return _heading_to_dxdy_int(heading)


@lru_cache(maxsize=512)
def _heading_to_dxdy_int(heading) -> Velocity:
    """ Convert a heading to a (dx, dy) pair as a unit velocity """
    angle = heading_to_angle(heading)
    dx = cos(angle)
    # The -1 accounts for the y-axis being inverted.
    dy = (-1) * sin(angle)
    vel = Velocity(dx, dy)
    return vel


def int_round(x, ndigits=None):
    """ Always returns a result of type int. """
    return int(round(x, ndigits))


def normalize_360(angle):
    return int(round(angle)) % 360


def normalize_180(angle):
    """ Convert angle to the range (-180 .. 180]. """
    normalized_angle = normalize_360(angle)
    return normalized_angle if normalized_angle <= 180 else normalized_angle - 360


def subtract_headings(a, b):
    """
    subtract heading b from heading a.
    To get from heading b to heading a we must turn by a-b.

       a
     /
    /_____ b

    Since larger headings are to the right (clockwise), if (a-b) is negative, that means b is to the right of a,
    as in the diagram. So we must turn negatively, i.e., counter-clockwise.
    Similarly for positive results. a is to the right of b, i.e., clockwise.

    Normalize to values between -180 and +180 to ensure that larger numbers are to the right, i.e., clockwise.
    No jump from 360 to 0.
    """
    return utils.normalize_180(a - b)


def turn_away_amount(new_heading, old_heading, max_turn):
    """
    turn_toward_amount(new_heading, old_heading, max_turn) finds the direction to turn
    starting at new_heading to get to old-heading -- limited by max_turn. If we reverse
    new_heading and old_heading, turn_toward_amount(old_heading, new_heading, max_turn),
    we are finding how much to turn to get from new_heading to old heading. But since
    we are starting at old_heading, turning in that direction turns us (farther) away
    from new_heading.
    """
    return turn_toward_amount(old_heading, new_heading, max_turn)


def turn_toward_amount(old_heading, new_heading, max_turn):
    """
    heading_delta will the amount old_heading should turn (positive or negative)
    to face more in the direction of new_heading.
    """
    heading_delta = utils.subtract_headings(new_heading, old_heading)
    # To take max_turn (an abs value) into consideration, we want to turn the
    # smaller (in absolute terms) of abs(heading_delta) and max_turn. But no
    # matter how much we turn, we want to turn in the direction indicated by
    # the sign of heading_delta

    # copysign returns the magnitude of the first argument but with the sign of the second.
    # copysign(mag, sign) = mag * (sign/abs(sign))
    amount_to_turn = copysign(min(abs(heading_delta), max_turn), heading_delta)
    return (amount_to_turn)


if __name__ == "__main__":
    # Various tests and experiments
    pv = Pixel_xy(1.234, 5.678)
    print(pv.round(2))

    vel = Velocity(1.234, 5.678)
    print(vel.round(2))

    rc = RowCol(3, 4)
    print(rc.as_tuple())

    screen_width = gui.SCREEN_PIXEL_WIDTH()
    screen_height = gui.SCREEN_PIXEL_HEIGHT()
    v1 = utils.Pixel_xy(1, 1)
    v2 = utils.Pixel_xy(2, 2)
    print(v1.distance_to(v2, True))
    print(v1.distance_to(v2, False))
    v3 = (v1 - v2).wrap3(screen_width, screen_height)
    print(v1.round(2), v2.round(2), v3.round(2))
    print(v1.distance_to(v3, True))
    print(v1.distance_to(v3, False))
    print(v3.distance_to(v1, True))
    print(v3.distance_to(v1, False))
    print('-----------------------------')
    v1 = utils.Pixel_xy(1, 1)
    v02 = utils.Pixel_xy(0, 2)
    v20 = utils.Pixel_xy(2, 0)
    v03 = (v1 - v02).wrap3(screen_width, screen_height)
    print(v1.distance_to(v03, True))
    print(v1.distance_to(v03, False))
    v30 = (v1 - v20).wrap3(screen_width, screen_height)
    print(v1.distance_to(v30, True))
    print(v1.distance_to(v30, False))
