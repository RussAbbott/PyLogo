from itertools import cycle

import pygame

from pygame.color import Color
from pygame.sprite import collide_rect

from random import choice, randint, random

from turtles_and_patches import BasicWorld, SimEngine, Patch, PixelVector2, RowCol, Turtle

# ############################################################ #
# A simple world and model to test the patches and the turtle. #
# ############################################################ #


class MyPatch(Patch):
    def __init__(self, row_col: RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')


class MyTurtle(Turtle):

    def move_turtle(self):
        # Bounce turtle off the screen edges
        screen_rect = SimEngine.SIM_ENGINE.screen_rect
        turtle_rect = self.rect
        if turtle_rect.right >= screen_rect.right - 10 or turtle_rect.left <= screen_rect.left + 10:
            self.vel = self.vel._replace(x=self.vel.x * (-1))
        if turtle_rect.top <= screen_rect.top + 10 or turtle_rect.bottom >= screen_rect.bottom - 10:
            self.vel = self.vel._replace(y=self.vel.y * (-1))

        self.move_by_vel()

        # Don't change both x and y at the same time.
        if random() < 0.003:
            self.vel = self.vel._replace(x=randint(-3, 3))
        elif random() < 0.003:
            self.vel = self.vel._replace(y=randint(-3, 3))

        # Don't stop and don't move too fast.
        while self.vel.x == 0 == self.vel.y or abs(self.vel.x) + abs(self.vel.y) > 4:
            if random() < 0.5:
                self.vel = self.vel._replace(x=randint(-1, 1))
            else:
                self.vel = self.vel._replace(y=randint(-1, 1))


class SimpleWorld_1(BasicWorld):

    def __init__(self, patch_class=Patch, patches_shape=RowCol(50, 50), turtle_class=Turtle, nbr_turtles=25):
        super().__init__(patch_class=patch_class, patches_shape=patches_shape,
                         turtle_class=turtle_class, nbr_turtles=nbr_turtles)

    def setup(self):
        for (turtle, vel) in zip(self.turtles, cycle([PixelVector2(-1, -1), PixelVector2(-1, 1),
                                                      PixelVector2(1, -1), PixelVector2(1, 1),
                                                      PixelVector2(0, 0)])):
            turtle.vel = vel

    def update(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            if pygame.time.get_ticks( ) > 3000 and random( ) < 0.05:
                turtle.vel = PixelVector2(randint(-2, 2), randint(-2, 2))
            turtle.move_by_vel()

        # No Patch updates
        # noinspection PyUnusedLocal
        for patch in self.patches.flat:
            pass


class SimpleWorld_2(BasicWorld):

    def setup(self):
        super().setup()
        # Give each turtle a random initial velocity.
        for turtle in self.turtles:
            turtle.vel = PixelVector2(randint(-2, 2), randint(-2, 2))

    def update(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            turtle.move_turtle()
        for patch in self.patches.flat:
            collides = any([collide_rect(patch, turtle) for turtle in self.turtles])
            fill_color = patch.hit_color if collides else patch.color
            patch.image.fill(fill_color)


if __name__ == "__main__":
    # The assignment statements (SimEngine.WORLD = ... and SimEngine.SIM_ENGINE = ...) are
    # not necessary. They are done in the two __init__'s. The are included here for clarity.

    # Create the world
    (world, nbr_turtles) = choice([(SimpleWorld_1, 25), (SimpleWorld_2, 3)])
    SimEngine.WORLD = world(patch_class=MyPatch, turtle_class=MyTurtle, nbr_turtles=nbr_turtles)
    SimEngine.WORLD.setup()

    # Get the name of the world's class to use as a caption.
    # str(world) is: "<class '__main__.SimpleWorldx'>" where x is either 1 or 2.
    caption = str(world).split(sep='.')[1][:-2]

    # Create the SimEngine
    SimEngine.SIM_ENGINE = SimEngine(caption=caption)
    SimEngine.SIM_ENGINE.run_model()
