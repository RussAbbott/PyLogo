
from __future__ import annotations

from collections import namedtuple

from itertools import cycle

# from math import copysign
import numpy as np

import pygame as pg
from pygame import display, event, K_d, K_ESCAPE, KMOD_CTRL, K_q, KEYDOWN, QUIT
from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.time import Clock

from PySimpleGUI import RGB

from random import randint, random

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

    @staticmethod
    def row_col_to_pixel_pos(row_col: RowCol):
        """
        Leave a border of 1 pixel at the top and left of the patches
        """
        return PixelVector2(1+BLOCK_SPACING*row_col.row, 1+BLOCK_SPACING*row_col.col)


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
        super().__init__(Block.row_col_to_pixel_pos(row_col), color)
        self.row_col = row_col


class Turtle(Block):
    def __init__(self,
                 pixel_pos: PixelVector2 = PixelVector2(25*BLOCK_SPACING-1, 25*BLOCK_SPACING-1),
                 color=Color('red')):
        super().__init__(pixel_pos, color)
        self.vel = PixelVector2(0, 0)


class PatchWorld:

    def __init__(self, patch_type=Patch, patches_shape=(50, 50)):
        self.patches = np.array([patch_type(RowCol(i, j)) for i in range(50) for j in range(50)])
        self.patches: np.ndarray = self.patches.reshape(patches_shape)
        self.turtles = []

    def draw(self, screen):
        for patch in self.patches.flat:
            patch.draw(screen)
        for turtle in self.turtles:
            turtle.draw(screen)


# # ############################################################ #
# # A basic world and model to test the patches and the turtle. #
# # ############################################################ #

class BasicWorld(PatchWorld):

    def __init__(self, screen_rect, turtle=Turtle, nbr_turtles=25, patch=Patch):
        super().__init__(patch)
        self.screen_rect = screen_rect

        # Create Turtles
        self.turtles = [turtle() for _ in range(nbr_turtles)]
        self.initalize_turtles()

    def initalize_turtles(self):
        for (turtle, vel) in zip(self.turtles, cycle([PixelVector2(-1, -1), PixelVector2(-1, 1),
                                                      PixelVector2(1, -1), PixelVector2(1, 1),
                                                      PixelVector2(0, 0)])):
            turtle.vel = vel

    def move_turtle(self, turtle):
        # Wrap around the screen
        turtle.pixel_pos = PixelVector2((turtle.pixel_pos.x + turtle.vel.x) % self.screen_rect.w,
                                        (turtle.pixel_pos.y + turtle.vel.y) % self.screen_rect.h)
        turtle.rect = Rect((turtle.pixel_pos.x, turtle.pixel_pos.y), (BLOCK_SIDE, BLOCK_SIDE))


    def update(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            switch_vel = pg.time.get_ticks( ) > 3000 and random( ) < 0.05
            turtle.vel = PixelVector2(randint(-2, 2), randint(-2, 2)) if switch_vel else turtle.vel
            self.move_turtle(turtle)

        # No Patch updates
        # noinspection PyUnusedLocal
        for _patch in self.patches.flat:
            pass


class Model:

    def __init__(self, world=BasicWorld, turtle=Turtle, nbr_turtles=25, patch=Patch, caption="Basic Model"):
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
        self.world = world(self.screen.get_rect(), turtle=turtle, nbr_turtles=nbr_turtles, patch=patch)

    # Fill the screen with background color, then draw blocks, then draw turtle on top. Then update the display.
    def draw(self):
        self.screen.fill(self.screen_color)
        self.world.draw(self.screen)
        display.update()

    def run_model(self):
        pg.init()
        while True:
            for ev in event.get():
                if ev.type == QUIT or \
                   ev.type == KEYDOWN and (ev.key == K_ESCAPE or
                                              ev.key == K_q or
                                              # The following tests for ctrl_d.
                                              # (See https://www.pygame.org/docs/ref/key.html)
                                              ev.key == K_d and ev.mod & KMOD_CTRL):
                    return

            self.world.update()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    model = Model()
    model.run_model()
