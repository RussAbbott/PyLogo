
from __future__ import annotations

# We also cache calls to trig functions
import math
from functools import lru_cache
from math import copysign
from random import randint

from pygame.color import Color

# noinspection PyUnresolvedReferences
import core.utils as utils


# ###################### Start trig functions in degrees ###################### #
# import Python's trig functions, which are in radians. pi radians == 180 degrees
# These functions expect their arguments in degrees.


def atan2(y, x):
    xy_max = max(abs(x), abs(y))
    (y_n, x_n) = (int(round(100*y/xy_max)), int(round(100*x/xy_max)))
    return atan2_normalized(y_n, x_n)


@lru_cache(maxsize=1024)
def atan2_normalized(y, x):
    return math.degrees(math.atan2(y, x))


def cos(degrees):
    return _cos(normalize_360(degrees))


@lru_cache(maxsize=512)
def _cos(degrees):
    return math.cos(math.radians(degrees))


def sin(degrees):
    return _sin(normalize_360(degrees))


@lru_cache(maxsize=512)
def _sin(degrees):
    return math.sin(math.radians(degrees))


# ###################### End trig functions in degrees ###################### #


def angle_to_heading(angle):
    """ Convert an angle to a heading. Same as heading to angle! """
    heading = heading_to_angle(angle)
    return heading


def bin_str(n, len):
    """
    Convert n to a binary string and add 0's to the left to make it length len.
    """
    return ('0'*len + f'{n:b}')[-len:]


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
        new_heading = angle_to_heading(angle)
        return new_heading


def dx(heading):
    return _dx(heading)


@lru_cache(maxsize=512)
def _dx(heading):
    angle = heading_to_angle(heading)
    delta_x = utils.cos(angle)
    return delta_x


def dy(heading):
    return _dy(heading)


@lru_cache(maxsize=512)
def _dy(heading):
    angle = heading_to_angle(heading)
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
    """ Convert a heading to an angle. Same as angle-to-heading. """
    return normalize_360(90 - heading)


def hex_to_rgb(hex_string):
    return Color(hex_string)


def int_round(x, ndigits=None):
    """ Always returns a result of type int. """
    return int(round(x, ndigits))


def normalize_360(angle):
    return int(round(angle)) % 360


def normalize_180(angle):
    """ Convert angle to the range (-180 .. 180]. """
    normalized_angle = normalize_360(angle)
    return normalized_angle if normalized_angle <= 180 else normalized_angle - 360


def normalize_dxdy(dxdy):
    mx = max(abs(dxdy.x), abs(dxdy.y))
    return dxdy if mx == 0 else dxdy/mx


def rgb_to_hex(rgb):
    (r, g, b) = rgb[:3]
    return f"#{r:02x}{g:02x}{b:02x}"


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
    return normalize_180(a - b)


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
    heading_delta = subtract_headings(new_heading, old_heading)
    # To take max_turn (an abs value) into consideration, we want to turn the
    # smaller (in absolute terms) of abs(heading_delta) and max_turn. But no
    # matter how much we turn, we want to turn in the direction indicated by
    # the sign of heading_delta

    # copysign returns the magnitude of the first argument but with the sign of the second.
    # copysign(mag, sign) = mag * (sign/abs(sign))
    amount_to_turn = copysign(min(abs(heading_delta), max_turn), heading_delta)
    return (amount_to_turn)


if __name__ == "__main__":

    print('\n-----hex string-----')
    hex_string = '#123456'
    (r, g, b, _) = Color(hex_string)
    print((r, g, b))
    hex1 = rgb_to_hex((r, g, b))
    print(hex1, hex_string, hex1 == hex_string)

    hex2 = rgb_to_hex((r, g, b))
    print(hex1)
