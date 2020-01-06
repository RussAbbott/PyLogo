
import PyLogo.core.static_values as static
import PyLogo.core.utils as utils

import numpy as np

from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

from random import choice


class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector2 but not necessarily a RowCol. Has a Color.
    """

    def __init__(self, pixel_pos: utils.PixelVector2, color=Color('black')):
        super().__init__()
        self.color = color
        self.pixel_pos = pixel_pos
        self.rect = Rect((self.pixel_pos.x, self.pixel_pos.y), (static.PATCH_SIZE, static.PATCH_SIZE))
        # print(self.rect)
        self.image = Surface((self.rect.w, self.rect.h))
        self.image.fill(color)

    def draw(self):
        static.SCREEN.blit(self.image, self.rect)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        

class Patch(Block):
    def __init__(self, row_col: utils.RowCol, color=Color('black')):
        super().__init__(utils.row_col_to_pixel_pos(row_col), color)
        self.row_col = row_col
        self.turtles = set()
        self._neighbors_4 = None
        self._neighbors_8 = None

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}{(self.row_col.row, self.row_col.col)}'

    def add_turtle(self, tur):
        self.turtles.add(tur)

    def neighbors_4(self):
        if self._neighbors_4 is None:
            cardinal_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1))
            self._neighbors_4 = self._neighbors(cardinal_deltas)
        return self._neighbors_4

    def neighbors_8(self):
        if self._neighbors_8 is None:
            all_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
            self._neighbors_8 = self._neighbors(all_deltas)
        return self._neighbors_8

    def _neighbors(self, deltas):
        """
        The neighbors of this patch determined by the deltas.
        Note the addition of two RowCol objects to produce a new RowCol object: self.row_col + utils.RowCol(r, c).
        Wrap around is handled by RowCol. We then turn the RowCol object to a tuple to access the np.ndarray
        """
        neighbors = [static.WORLD.patches[(self.row_col + utils.RowCol(r, c)).as_tuple()] for (r, c) in deltas]
        return neighbors

    def remove_turtle(self, tur):
        self.turtles.remove(tur)


class Turtle(Block):
    def __init__(self, pixel_pos: utils.PixelVector2 = None, color=None):
        if color is None:
            # Use either static.NETLOGO_PRIMARY_COLORS or static.NETLOGO_PRIMARY_COLORS
            # color = choice(static.NETLOGO_PRIMARY_COLORS)
            color = choice(static.PYGAME_COLORS)
        if pixel_pos is None:
            # Get the center pixel
            screen_rect = static.SCREEN.get_rect()
            pixel_pos = utils.PixelVector2(round(screen_rect.width / 2), round(screen_rect.height / 2))
            # pixel_pos = utils.CENTER_PIXEL()
            # pixel_pos = cp
        super().__init__(pixel_pos, color)
        static.WORLD.turtles.add(self)
        self.patch().add_turtle(self)
        self.velocity = utils.PixelVector2(0, 0)

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}{(self.pixel_pos.x, self.pixel_pos.y)} on {self.patch()}'

    def move_turtle(self, wrap):
        pass

    def move_by_dxdy(self, dxdy: utils.PixelVector2):
        """
        Move to self.pixel_pos + (dx, dy)
        """
        self.move_to_xy(utils.PixelVector2(self.pixel_pos.x + dxdy.x, self.pixel_pos.y + dxdy.y))

    def move_by_velocity(self, bounce):
        if bounce:
            # Bounce turtle off the screen edges
            screen_rect = static.SCREEN.get_rect()
            turtle_rect = self.rect
            if turtle_rect.right >= screen_rect.right or turtle_rect.left <= screen_rect.left:
                self.velocity = utils.PixelVector2(self.velocity.x * (-1), self.velocity.y)
            if turtle_rect.top <= screen_rect.top or turtle_rect.bottom >= screen_rect.bottom:
                self.velocity = utils.PixelVector2(self.velocity.x, self.velocity.y * (-1))
        self.move_by_dxdy(self.velocity)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.pixel_pos)

    def move_to_xy(self, xy: utils.PixelVector2):
        """
        Remove this turtle from the list of turtles at its current patch.
        Move this turtle to its new xy pixel_pos.
        Add this turtle to the list of turtles in its new patch.
        """
        current_patch: Patch = self.patch()
        current_patch.remove_turtle(self)
        self.pixel_pos = xy.wrap()
        self.rect = Rect((self.pixel_pos.x, self.pixel_pos.y), (static.PATCH_SIZE, static.PATCH_SIZE))
        new_patch = self.patch()
        new_patch.add_turtle(self)

    def patch(self) -> Patch:
        (row, col) = utils.pixel_pos_to_row_col(self.pixel_pos).as_tuple()
        patch = static.WORLD.patches[row, col]
        return patch


class World:

    def __init__(self, patch_class=Patch, turtle_class=Turtle):
        static.WORLD = self

        self.patch_class = patch_class
        self.patches: np.ndarray = np.ndarray([])

        self.turtle_class = turtle_class
        self.turtles = set()

    def clear_all(self):
        self.turtles = set()

    def done(self):
        return False

    def draw(self):
        for patch in self.patches.flat:
            patch.draw()
        for turtle in self.turtles:
            turtle.draw()

    def final_thoughts(self):
        """ Add any final tests, data gathering, summarization, etc. here. """
        pass

    def setup(self, values):
        self.clear_all()
        patch_pseudo_array = [[self.patch_class(utils.RowCol(r, c)) for c in range(static.PATCH_COLS)]
                              for r in range(static.PATCH_ROWS)]
        self.patches: np.ndarray = np.array(patch_pseudo_array)
        utils.reset_ticks()

    def step(self, event, values):
        """
        Update the world. Override for each world
        """
        pass
