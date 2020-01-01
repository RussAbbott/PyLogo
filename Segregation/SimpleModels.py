from itertools import cycle

from pygame.color import Color
from pygame.sprite import collide_rect

import PySimpleGUI as sg   # import run_model, read_values

from PySimpleGUI_with_PyLogo import SimpleGUI

from random import choice, randint, random

import sim_engine as se


# ############################################################ #
#     Two simple worlds to test the patches and the turtle.    #
# ############################################################ #

# ######### ColliderWorld defines its own specialized Patch and Turtle ######### #


class Collider_Patch(se.Patch):

    def __init__(self, row_col: se.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')


class Collider_Turtle(se.Turtle):

    def move_turtle(self):
        # Bounce turtle off the screen edges
        screen_rect = se.SimEngine.SCREEN_RECT
        turtle_rect = self.rect
        margin = se.BLOCK_SIDE*2/3
        if turtle_rect.right >= screen_rect.right - margin or turtle_rect.left <= screen_rect.left + margin:
            self.vel = self.vel._replace(x=self.vel.x * (-1))
        if turtle_rect.top <= screen_rect.top + margin or turtle_rect.bottom >= screen_rect.bottom - margin:
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


class ColliderWorld(se.BasicWorld):
    """
    A world in which the patches change to green when intersecting with a turtle.
    """

    def setup(self, values):
        super().setup(values)

        # Give each turtle a random initial velocity.
        for turtle in self.turtles:
            turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))

    def step(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            turtle.move_turtle()
        for patch in self.patches.flat:
            collides = any([collide_rect(patch, turtle) for turtle in self.turtles])
            fill_color = patch.hit_color if collides else patch.color
            patch.image.fill(fill_color)


# ######### StarburstWorld uses the standard Patch and Turtle ######### #


class StarburstWorld(se.BasicWorld):
    """
    A world of starburst turtles.
    """

    def setup(self, values):
        super().setup(values)
        initial_velocities = cycle([se.PixelVector2(-1, -1), se.PixelVector2(-1, 1),
                                    se.PixelVector2(0, 0),
                                    se.PixelVector2(1, -1), se.PixelVector2(1, 1)])
        for (turtle, vel) in zip(self.turtles, initial_velocities):
            turtle.vel = vel

    def step(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect with it.
        """
        for turtle in self.turtles:
            if se.SimEngine.SIM_ENGINE.ticks > 200 and random() < 0.05:
                turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))
            turtle.move_by_vel()


def main():
    se.SimEngine.SIM_ENGINE = se.SimEngine()

    # Select a world
    (world_class, turtle_class, nbr_turtles, patch_class) = \
        choice([(StarburstWorld, se.Turtle, 25, se.Patch),
                (ColliderWorld, Collider_Turtle, 3, Collider_Patch)])

    se.SimEngine.SIM_ENGINE = se.SimEngine()  # caption="Segregation Model", fps=4)

    # se.SimEngine.WORLD = SegregationWorld()
    # The assignment (SimEngine.SIM_ENGINE = ... and SimEngine.WORLD = ...) are redundant.
    # They are done in the __init__'s and are included here for clarity.

    se.SimEngine.WORLD = world_class(turtle_class=turtle_class, patch_class=patch_class)

    gui_elements = [sg.Text('number of turtles'), sg.Slider(key='nbr_turtles',
                                                            range=(1, (100 if world_class is StarburstWorld else 10)),
                                                            default_value=(25 if world_class is StarburstWorld else 3),
                                                            orientation='horizontal',
                                                            pad=((0, 50), (0, 20)))]
    # Create a caption
    caption = se.SimEngine.extract_class_name(world_class)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
