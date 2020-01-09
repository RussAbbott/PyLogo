
import PyLogo.core.core_elements as core
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils

from pygame.color import Color
from pygame.sprite import collide_rect

from random import randint, random, uniform


class CollisionTest_Patch(core.Patch):

    def __init__(self, row_col: utils.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')

    def update_collision_color(self, turtles):
        collides = any([collide_rect(self, turtle) for turtle in turtles])
        fill_color = self.hit_color if collides else self.color
        self.image.fill(fill_color)


class CollisionTest_Turtle(core.Turtle):

    def __init__(self):
        super().__init__(color=Color('red'))
        # Give each turtle a random initial velocity.
        self.velocity = utils.PixelVector(uniform(-2, 2), uniform(-2, 2))


class CollisionTest_World(core.World):
    """
    A world in which the patches change to green when intersecting with a turtle.
    """

    def setup(self):
        nbr_turtles = int(values['nbr_turtles'])
        for i in range(nbr_turtles):
            # Adds itself to self.turtles and to its patch's list of Turtles.
            self.turtle_class()

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)

    def step(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            turtle.move_by_velocity()
            if random() < 0.02:
                turtle.velocity = utils.PixelVector(randint(-2, 2), randint(-2, 2))

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)


def main():

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [[Text('nbr turtles', pad=((0, 5), (20, 0))),
                     Slider(key='nbr_turtles', range=(1, 10), default_value=3,
                            orientation='horizontal', size=(10, 20))],
                    ]

    sim_engine = SimEngine(gui_elements, caption='Collision test')
    sim_engine.start(CollisionTest_World, patch_class=CollisionTest_Patch, turtle_class=CollisionTest_Turtle)


if __name__ == "__main__":
    main()
