
import PyLogo.core.core_elements as core
import PyLogo.core.utils as utils

from pygame.color import Color
from pygame.sprite import collide_rect

from random import randint, random, uniform


class CollisionTest_Patch(core.Patch):

    def __init__(self, row_col: utils.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('white')

    def update_collision_color(self, turtles):
        collides = any([collide_rect(self, turtle) for turtle in turtles])
        fill_color = self.hit_color if collides else self.color
        self.image.fill(fill_color)


class CollisionTest_World(core.World):
    """
    A world in which the patches change to green when intersecting with a turtle.
    """

    def setup(self):
        nbr_turtles = int(core.WORLD.values['nbr_turtles'])
        for i in range(nbr_turtles):
            # Adds itself to self.turtles and to its patch's list of Turtles.
            turtle = self.turtle_class(color=Color('red'), scale_factor=1.4)
            turtle.set_velocity(utils.Velocity(uniform(-2, 2), uniform(-2, 2)))

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)

    def step(self):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            turtle.move_by_velocity()
            if random() < 0.01:
                turtle.set_velocity(utils.Velocity(randint(-2, 2), randint(-2, 2)))

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('nbr turtles', pad=((0, 5), (20, 0))),
                 sg.Slider(key='nbr_turtles', range=(1, 10), default_value=3,
                           orientation='horizontal', size=(10, 20))],
                ]

if __name__ == "__main__":
    from PyLogo.core.core_elements import PyLogo
    PyLogo(CollisionTest_World, gui_elements, 'Collision test', patch_class=CollisionTest_Patch, bounce=False)
