
from turtles_and_patches import BasicWorld, Model, Patch, PatchWorld, PixelVector2, RowCol, Turtle

import pygame as pg
from pygame import display, event, K_d, K_ESCAPE, KMOD_CTRL, K_q, KEYDOWN, QUIT
from pygame.color import Color
from pygame.sprite import collide_rect
from pygame.time import Clock

from PySimpleGUI import RGB

from random import randint, random

# ############################################################ #
# A simple world and model to test the patches and the turtle. #
# ############################################################ #


class MyPatch(Patch):
    def __init__(self, row_col: RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')


class MyTurtle(Turtle):
    pass


class SimpleWorld(BasicWorld):

    def initalize_turtles(self):
        # Give each turtle a random initial velocity.
        for turtle in self.turtles:
            turtle.vel = PixelVector2(randint(-2, 2), randint(-2, 2))

    def move_turtle(self, turtle):
        # Bounce turtle off the screen edges
        turtle_rect = turtle.rect
        if turtle_rect.right >= self.screen_rect.right - 10 or turtle_rect.left <= self.screen_rect.left + 10:
            turtle.vel = turtle.vel._replace(x=turtle.vel.x * (-1))
        if turtle_rect.top <= self.screen_rect.top + 10 or turtle_rect.bottom >= self.screen_rect.bottom - 10:
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
            if random( ) < 0.5:
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


if __name__ == "__main__":
    model = Model(world=SimpleWorld, turtle=MyTurtle, nbr_turtles=3, patch=MyPatch, caption="Simple Model")
    model.run_model()
