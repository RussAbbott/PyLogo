from collections import namedtuple

import pygame as pg
from pygame.color import Color
from pygame.rect import Rect
from pygame.time import Clock

from PySimpleGUI import RGB

# Global constants
RowCol = namedtuple('RowCol', 'row col')
PixelVector2 = namedtuple('PixelVector2', 'x y')

# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
BLOCK_SIDE = 15
BLOCK_SPACING = BLOCK_SIDE + 1



# These are globally available as SimEngine.SIM_ENGINE and SimEngine.WORLD
SIM_ENGINE = None  # The SimEngine object
WORLD = None  # The world

SCREEN_RECT = None
CENTER_PIXELS = None

patch_grid_shape = RowCol(51, 51)
screen_color = Color(RGB(50, 60, 60))

CLOCK = Clock()
TICKS = 0


# def __init__():
#     global CLOCK, patch_grid_shape, screen_color, TICKS
#     CLOCK = Clock()
#     TICKS = 0
#     patch_grid_shape = RowCol(51, 51)
#     screen_color = Color(RGB(50, 60, 60))


# Fill the screen with the background color, then: draw patches, draw turtles on top, update the display.
def draw(screen):
    screen.fill(screen_color)
    WORLD.draw(screen)
    pg.display.update( )


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


def in_bounds(r, c):
    return 0 <= r < patch_grid_shape.row and 0 <= c < patch_grid_shape.col


def place_turtle_on_screen(turtle):
    # Wrap around the screen.
    turtle.pixel_pos = PixelVector2(turtle.pixel_pos.x % SCREEN_RECT.w,
                                    turtle.pixel_pos.y % SCREEN_RECT.h)
    turtle.rect = Rect((turtle.pixel_pos.x, turtle.pixel_pos.y), (BLOCK_SIDE, BLOCK_SIDE))


def reset_ticks():
    global TICKS
    TICKS = 0


# __init__()