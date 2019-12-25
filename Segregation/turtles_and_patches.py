
from __future__ import annotations

from collections import namedtuple

import numpy as np

import pygame as pg
from pygame import display, event, K_d, K_ESCAPE, KMOD_CTRL, K_q, KEYDOWN, QUIT
from pygame.color import Color
from pygame.rect import Rect
from pygame.sprite import collide_rect, Sprite
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


# ############################################################ #
# A simple world and model to test the patches and the turtle. #
# ############################################################ #


class MyPatch(Patch):
    def __init__(self, row_col: RowCol):
        super().__init__(row_col)
        self.hit_color = Color('green')


class MyTurtle(Turtle):
    def __init__(self):
        super().__init__()
        # Each turtle gets a random initial velocity
        self.vel = PixelVector2(randint(-2, 2), randint(-2, 2))


class SimpleWorld(PatchWorld):

    def __init__(self, screen_rect, nbr_turtles=3):
        super().__init__(MyPatch)
        self.screen_rect = screen_rect

        # Create Turtles
        self.turtles = [MyTurtle() for _ in range(nbr_turtles)]

    # Bounces turtle off the screen edges
    def move_turtle(self, turtle):
        turtle_rect = turtle.rect
        if turtle_rect.right >= self.screen_rect.right-5 or turtle_rect.left <= self.screen_rect.left+5:
            turtle.vel = turtle.vel._replace(x=turtle.vel.x * (-1))
        if turtle_rect.top <= self.screen_rect.top+5 or turtle_rect.bottom >= self.screen_rect.bottom-5:
            turtle.vel = turtle.vel._replace(y=turtle.vel.y * (-1))

        # move_ip is move in place.
        turtle_rect.move_ip(turtle.vel.x, turtle.vel.y)

        # Don't change both x and y at the same time.
        if random( ) < 0.003:
            turtle.vel = turtle.vel._replace(x=randint(-3, 3))
        elif random( ) < 0.003:
            turtle.vel = turtle.vel._replace(y=randint(-3, 3))

        # Don't stop and don't move too fast.
        while turtle.vel.x == 0 == turtle.vel.y or abs(turtle.vel.x) + abs(turtle.vel.y) > 4:
            if random() < 0.5:
                turtle.vel = turtle.vel._replace(x=randint(-1, 1))
            else:
                turtle.vel = turtle.vel._replace(y=randint(-1, 1))

    def update(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            self.move_turtle(turtle)
        for patch in self.patches.flat:
            collides = any([collide_rect(patch, turtle) for turtle in self.turtles])
            fill_color = patch.hit_color if collides else patch.color
            patch.image.fill(fill_color)


class SimpleModel:

    def __init__(self):
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
        display.set_caption("Simple Model")
        self.simple_world = SimpleWorld(self.screen.get_rect())

        self.clock = Clock( )

    # Fill the screen with background color, then draw blocks, then draw turtle on top. Then update the display.
    def draw(self):
        self.screen.fill(self.screen_color)
        self.simple_world.draw(self.screen)
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

            self.simple_world.update()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    SimpleModel().run_model()
