
import pygame as pg
from pygame.color import Color
from pygame.colordict import THECOLORS

# from PySimpleGUI import RGB

from typing import Optional, Tuple

# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
BLOCK_SIDE = 15
BLOCK_SPACING = BLOCK_SIDE + 1


def is_acceptable_color(rgb: Tuple[int, int, int]):
    """
    Require reasonably bright colors (>= 150) that aren't washed out (<= 600)
    and for which r, g, and b are not too close to each other.
    """
    sum_rgb = sum(rgb)
    avg_rgb = sum_rgb/3
    return 150 <= sum_rgb <= 600 and sum(abs(avg_rgb-x) for x in rgb) > 50


# These are colors defined by pygame that satisfy is_acceptable_color above.
PYGAME_COLORS = [rgba for rgba in THECOLORS.values() if is_acceptable_color(rgba[:3])]

NETLOGO_PRIMARY_COLORS = [Color('gray'), Color('red'), Color('orange'), Color('brown'), Color('yellow'),
                          Color('green'), Color('limegreen'), Color('turquoise'), Color('cyan'),
                          Color('skyblue3'), Color('blue'), Color('violet'), Color('magenta'), Color('pink')]

PATCH_ROWS = 51
PATCH_COLS = 51

SCREEN: Optional[pg.Surface] = None

SCREEN_PIXEL_WIDTH = 816
SCREEN_PIXEL_HEIGHT = 816

TICKS = 0

WORLD = None  # The world
