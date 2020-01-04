
# from __future__ import annotations
import PyLogo.core.sim_engine as se

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

    def __init__(self, pixel_pos: se.PixelVector2, color=Color('black')):
        super().__init__()
        self.color = color
        self.pixel_pos: se.PixelVector2 = pixel_pos
        self.rect = Rect((self.pixel_pos.x(), self.pixel_pos.y()), (se.BLOCK_SIDE, se.BLOCK_SIDE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.image.fill(color)

    def draw(self):  # , screen):
        # screen.blit(self.image, self.rect)
        se.SCREEN.blit(self.image, self.rect)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        

class Patch(Block):
    def __init__(self, row_col: se.RowCol, color=Color('black')):
        super().__init__(se.row_col_to_pixel_pos(row_col), color)
        self.row_col = row_col
        self.turtles = set()

    def __str__(self):
        class_name = se.get_class_name(self)
        return f'{class_name}{(self.row_col.row(), self.row_col.col())} at {(self.pixel_pos.x(), self.pixel_pos.y())}'

    def add_turtle(self, tur):
        self.turtles.add(tur)

    def neighbors_4(self):
        return self._neighbors()

    def neighbors_8(self):
        return self._neighbors(extra_deltas=((-1, -1), (-1, 1), (1, -1), (1, 1)))

    def _neighbors(self, extra_deltas=()):
        """
        The 4 or 8 neighbors of this patch.
        Must use an empty tuple, rather than an empty list, for the default extra_deltas.
        Default arguments may not be mutable.
        """
        # The initial cardinal_deltas are the cardinal directions: N, S, E, W
        cardinal_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1))
        # The extra_deltas, if given are the corner directions.
        rc_deltas = cardinal_deltas + extra_deltas
        (row, col) = self.row_col.as_tuple()
        neighbs = [se.WORLD.patches[row+r, col+c]
                   for (r, c) in rc_deltas if se.in_bounds_rc(row+r, col+c)]
        return neighbs

    def remove_turtle(self, tur):
        self.turtles.remove(tur)


class Turtle(Block):
    def __init__(self, pixel_pos: se.PixelVector2 = se.CENTER_PIXEL, color=None):
        if color is None:
            # Use either se.NETLOGO_PRIMARY_COLORS or se.NETLOGO_PRIMARY_COLORS
            # color = choice(se.NETLOGO_PRIMARY_COLORS)
            color = choice(se.PYGAME_COLORS)
        super().__init__(pixel_pos, color)
        se.WORLD.turtles.add(self)
        self.patch().add_turtle(self)
        self.velocity = se.PixelVector2(0, 0)

    def __str__(self):
        class_name = se.get_class_name(self)
        return f'{class_name}{(self.pixel_pos.x(), self.pixel_pos.y())} on {self.patch()}'

    def move_turtle(self, wrap):
        pass

    def move_by_dxdy(self, dxdy: se.PixelVector2):
        """
        Move to self.pixel_pos + (dx, dy)
        """
        self.move_to_xy(se.PixelVector2(self.pixel_pos.x() + dxdy.x(), self.pixel_pos.y() + dxdy.y()))

    def move_by_velocity(self, bounce):
        if bounce:
            # Bounce turtle off the screen edges
            screen_rect = se.SCREEN_RECT
            turtle_rect = self.rect
            margin = 0
            if turtle_rect.right >= screen_rect.right - margin or turtle_rect.left <= screen_rect.left + margin:
                self.velocity = se.PixelVector2(self.velocity.x() * (-1), self.velocity.y())
            if turtle_rect.top <= screen_rect.top + margin or turtle_rect.bottom >= screen_rect.bottom - margin:
                self.velocity = se.PixelVector2(self.velocity.x(), self.velocity.y() * (-1))
        self.move_by_dxdy(self.velocity)

    def move_to_xy(self, xy: se.PixelVector2):
        """
        Remove this turtle from the list of turtles at its current patch.
        Move this turtle to its new xy pixel_pos.
        Add this turtle to the list of turtles in its new patch.
        """
        current_patch: Patch = self.patch()
        current_patch.remove_turtle(self)
        self.pixel_pos = xy.wrap()
        self.rect = Rect((self.pixel_pos.x(), self.pixel_pos.y()), (se.BLOCK_SIDE, se.BLOCK_SIDE))
        new_patch = self.patch()
        new_patch.add_turtle(self)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.pixel_pos)

    def patch(self) -> Patch:
        (row, col) = se.pixel_pos_to_row_col(self.pixel_pos).as_tuple()
        patch = se.WORLD.patches[row, col]
        return patch


class World:

    def __init__(self, patch_class=Patch, turtle_class=Turtle):
        se.WORLD = self

        self.patch_class = patch_class
        self.patches = None

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
        patch_pseudo_array = [[self.patch_class(se.RowCol(r, c)) for c in range(se.PATCH_GRID_SHAPE.col())]
                              for r in range(se.PATCH_GRID_SHAPE.row())]
        self.patches = np.array(patch_pseudo_array)
        se.reset_ticks()

    def step(self, event, values):
        """
        Update the world. Override for each world
        """
        pass
