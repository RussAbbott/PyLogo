
from __future__ import annotations

from turtles_and_patches import BLOCK_SPACING, Patch, PixelVector2, RowCol, TestWorld, Turtle

import numpy as np
import pygame as pg
from pygame import display, event, QUIT
from pygame.color import Color
from pygame.sprite import collide_rect
from pygame.time import Clock

from PySimpleGUI import RGB

from random import randint, random


class MyTestWorld(TestWorld):

    def __init__(self, screen_rect, patches_shape=(50, 50)):
        super().__init__(screen_rect)
        # self.patches = np.array([Patch(RowCol(i, j)) for i in range(50) for j in range(50)])
        # self.patches: np.ndarray = self.patches.reshape(patches_shape)
        for patch in self.patches.flat:
            patch.hit_color = Color('green')
        turtle_pos = PixelVector2(randint(0, screen_rect.w)-BLOCK_SPACING,
                                  randint(0, screen_rect.h)-BLOCK_SPACING)
        self.turtle = Turtle(turtle_pos)
        self.turtle_vel = TestWorld.new_velocity()
        self.screen_rect = screen_rect

    def draw(self, screen):
        for patch in self.patches.flat:
            patch.draw(screen)
        self.turtle.draw(screen)

    # Bounces turtle off the screen edges
    def move_turtle(self):
        turtle_rect = self.turtle.rect
        if turtle_rect.right >= self.screen_rect.right or turtle_rect.left <= self.screen_rect.left:
            self.turtle_vel = self.turtle_vel._replace(x=self.turtle_vel.x * (-1))
        if turtle_rect.top <= self.screen_rect.top or turtle_rect.bottom >= self.screen_rect.bottom:
            self.turtle_vel = self.turtle_vel._replace(y=self.turtle_vel.y * (-1))

        # move_ip is move in place.
        turtle_rect.move_ip(self.turtle_vel.x, self.turtle_vel.y)
        # Don't change both x and y at the same time.
        if random( ) < 0.003:
            self.turtle_vel = self.turtle_vel._replace(x=randint(-2, 2))
        elif random( ) < 0.003:
            self.turtle_vel = self.turtle_vel._replace(y=randint(-2, 2))

    @staticmethod
    def new_velocity():
        return PixelVector2(randint(-2, 2), randint(-2, 2))


    def update(self):
        self.move_turtle()
        for patch in self.patches.flat:
            patch.fill_color = patch.hit_color if collide_rect(patch, self.turtle) else patch.color


class Test:

    def __init__(self):
        pg.init()

        self.width = 801
        self.height = 801
        self.fps = 60
        # self.color = Color('darkslategray')  # (47, 79, 79, 255), same as pygame.colordict.THECOLORS['...']
        # self.color = Color('gray20')  # (51, 51, 51, 255), same as pygame.colordict.THECOLORS['...']
        # A compromize between 'darkslategray' and 'gray20'
        self.color = Color(RGB(50, 60, 60))

        # set_mode() creates a Surface for display
        self.screen = display.set_mode((self.width, self.height))
        title = "Test world"
        display.set_caption(title)
        self.my_test_world = MyTestWorld(self.screen.get_rect())

        self.clock = Clock( )

    # Clear screen with background color, then draw blocks, then draw turtle on top. Then update the display.
    def draw(self):
        self.screen.fill(self.color)
        self.my_test_world.draw(self.screen)
        display.update()

    def run_test(self):
        while True:
            for ev in event.get():
                if ev.type == QUIT:
                    return

            self.my_test_world.update()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    Test().run_test()
