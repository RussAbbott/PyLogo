
from __future__ import annotations

from collections import namedtuple

import numpy as np

import pygame as pg
from pygame import display, event, K_d, K_ESCAPE, KMOD_CTRL, K_q, KEYDOWN, QUIT
from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.time import Clock

from PySimpleGUI import RGB

from typing import Set


# Global constants
RowCol = namedtuple('RowCol', 'row col')
PixelVector2 = namedtuple('PixelVector2', 'x y')

# Assumes that all Blocks are square with side BLOCK_SIDE
BLOCK_SIDE = 15
BLOCK_SPACING = BLOCK_SIDE + 1


class Block(Sprite):
    """
    A generic patch/turtle. Has a PixelVector2 but not necessarily a RowCol. Has a Color.
    """

    def __init__(self, pixel_pos: PixelVector2, color=Color('black')):
        super().__init__()
        self.color = color
        self.pixel_pos: PixelVector2 = pixel_pos
        self.rect = Rect((self.pixel_pos.x, self.pixel_pos.y), (BLOCK_SIDE, BLOCK_SIDE))
        self.image = Surface((self.rect.w, self.rect.h))
        self.image.fill(color)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        

class Patch(Block):
    def __init__(self, row_col: RowCol, color=Color('black')):
        super().__init__(SimEngine.WORLD.row_col_to_pixel_pos(row_col), color)
        self.row_col = row_col
        self.turtles = set()

    def neighbors(self, n=8):
        (row, col) = self.row_col
        n_4 = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        n_8 = n_4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        rc_deltas = n_4 if n == 4 else n_8
        patch_class = type(self)
        neighbs: Set[patch_class] = set(patch_class(r, c) for (r, c) in rc_deltas
                                        if SimEngine.WORLD.in_bounds(row+r, col+c))
        return neighbs


class Turtle(Block):
    def __init__(self,
                 pixel_pos: PixelVector2 = PixelVector2(25*BLOCK_SPACING-1, 25*BLOCK_SPACING-1),
                 color=Color('red')):
        super().__init__(pixel_pos, color)
        self.vel = PixelVector2(0, 0)
        
    def move_turtle(self):
        pass

    def move_by_vel(self):
        self.move_by_dx_dy(self.vel.x, self.vel.y)

    def move_by_dx_dy(self, dx, dy):
        """
        Computes the turtle pixel_pos based on its current pixel_pos and its velocity.
        Then calls SIM_ENGINE.place_turtle(turtle) to place it on the screen.
        SIM_ENGINE.place_turtle() wraps around if necessary.
        Removes the turtle from its current Patch and places it in its new Patch.
        """
        current_patch: Patch = self.patch()
        current_patch.turtles.remove(self)
        self.pixel_pos = PixelVector2(self.pixel_pos.x + dx, self.pixel_pos.y + dy)
        SimEngine.SIM_ENGINE.place_turtle(self)
        new_patch: Patch = self.patch()
        new_patch.turtles.add(self)

    def patch(self) -> Patch:
        (row, col) = SimEngine.WORLD.pixel_pos_to_row_col(self.pixel_pos)
        patch = SimEngine.WORLD.patches[row, col]
        return patch


class BasicWorld:

    def __init__(self, patch_class=Patch, patches_shape=RowCol(50, 50), turtle_class=Turtle, nbr_turtles=25):
        SimEngine.WORLD = self
        self.shape = patches_shape
        self.patches = np.array([patch_class(RowCol(r, c))
                                 for r in range(self.shape.row) for c in range(self.shape.col)])
        self.patches: np.ndarray = self.patches.reshape(patches_shape)
        self.turtles: Set[turtle_class] = set(turtle_class() for _ in range(nbr_turtles))
        for turtle in self.turtles:
            turtle.patch().turtles.add(turtle)


    def clear_all(self):
        self.turtles = set()

    def draw(self, screen):
        for patch in self.patches.flat:
            patch.draw(screen)
        for turtle in self.turtles:
            turtle.draw(screen)

    def in_bounds(self, r, c):
        return 0 <= r <= self.shape.row and 0 <= c <= self.shape.col

    @staticmethod
    def pixel_pos_to_row_col(pixel_pos: PixelVector2):
        """
        Get the patch row-col for this pixel_pos
        """
        row = (pixel_pos.y - 1) // BLOCK_SPACING
        col = (pixel_pos.x - 1) // BLOCK_SPACING
        return RowCol(row, col)

    @staticmethod
    def row_col_to_pixel_pos(row_col: RowCol):
        """
        Leave a border of 1 pixel at the top and left of the patches
        """
        return PixelVector2(1+BLOCK_SPACING*row_col.row, 1+BLOCK_SPACING*row_col.col)

    def setup(self):
        pass

    def update(self):
        pass


class SimEngine:
    """
    The engine that runs the simulation.
    """
    # These are globally available as SimEngine.SIM_ENGINE and SimEngine.WORLD
    SIM_ENGINE = None  # The SimEngine object
    WORLD = None       # The world

    def __init__(self, caption="Basic Model"):

        SimEngine.SIM_ENGINE = self

        # Leave a border of 1 pixel at the top and left of the patches
        self.width = 801
        self.height = 801
        self.fps = 60

        # This is the color of the lines between the patches, implemented as the screen background color.

        # self.screen_color = Color('darkslategray')  # (47, 79, 79, 255), same as pygame.colordict.THECOLORS['...']
        # self.screen_color = Color('gray20')  # (51, 51, 51, 255), same as pygame.colordict.THECOLORS['...']
        # A compromize between 'darkslategray' and 'gray20'
        self.screen_color = Color(RGB(50, 60, 60))

        # set_mode() creates a Surface for display
        self.screen = display.set_mode((self.width, self.height))
        display.set_caption(caption)
        self.clock = Clock()
        self.screen_rect = self.screen.get_rect()


    # Fill the screen with background color, then draw blocks, then draw turtle on top. Then update the display.
    def draw(self):
        self.screen.fill(self.screen_color)
        SimEngine.WORLD.draw(self.screen)
        display.update()

    def place_turtle(self, turtle):
        # Wrap around the screen.
        turtle.pixel_pos = PixelVector2(turtle.pixel_pos.x % self.screen_rect.w,
                                        turtle.pixel_pos.y % self.screen_rect.h)
        turtle.rect = Rect((turtle.pixel_pos.x, turtle.pixel_pos.y), (BLOCK_SIDE, BLOCK_SIDE))


    def run_model(self):
        pg.init()
        while True:
            for ev in event.get():
                if ev.type == QUIT or \
                   ev.type == KEYDOWN and (ev.key == K_ESCAPE or
                                           ev.key == K_q or
                                           # The following tests for ctrl-d.
                                           # (See https://www.pygame.org/docs/ref/key.html)
                                           ev.key == K_d and ev.mod & KMOD_CTRL):
                    return

            SimEngine.WORLD.update()
            self.draw()
            self.clock.tick(self.fps)
