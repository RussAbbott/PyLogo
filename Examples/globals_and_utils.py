from collections import namedtuple
from pygame.rect import Rect


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

CLOCK = None
TICKS = None


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


def place_turtle_on_screen(turtle):
    # Wrap around the screen.
    turtle.pixel_pos = PixelVector2(turtle.pixel_pos.x % SCREEN_RECT.w,
                                    turtle.pixel_pos.y % SCREEN_RECT.h)
    turtle.rect = Rect((turtle.pixel_pos.x, turtle.pixel_pos.y), (BLOCK_SIDE, BLOCK_SIDE))


def reset_ticks():
    # TICKS = 0
    global TICKS
    TICKS = 0
