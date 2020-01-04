
from pygame.color import Color
from pygame.colordict import THECOLORS


PATCH_ROWS = 51
PATCH_COLS = 51

SCREEN_PIXEL_WIDTH = 816
SCREEN_PIXEL_HEIGHT = 816

SCREEN = None

# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
BLOCK_SIDE = 15
BLOCK_SPACING = BLOCK_SIDE + 1


NETLOGO_PRIMARY_COLORS = [Color('gray'), Color('red'), Color('orange'), Color('brown'), Color('yellow'),
                          Color('green'), Color('limegreen'), Color('turquoise'), Color('cyan'),
                          Color('skyblue3'), Color('blue'), Color('violet'), Color('magenta'), Color('pink')]
PYGAME_COLORS = [rgba for rgba in THECOLORS.values()]


TICKS = 0

WORLD = None  # The world
