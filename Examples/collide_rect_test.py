
from pygame.color import Color
from pygame.sprite import collide_rect

import PySimpleGUI as sg   # import run_model, read_values

from PySimpleGUI_with_PyLogo import SimpleGUI

from random import randint, random

import sim_engine as se


class CollisionRect_Patch(se.Patch):

    def __init__(self, row_col: se.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')

    def update_collision_color(self, turtles):
        collides = any([collide_rect(self, turtle) for turtle in turtles])
        fill_color = self.hit_color if collides else self.color
        self.image.fill(fill_color)


class CollisionRect_World(se.BasicWorld):
    """
    A world in which the patches change to green when intersecting with a turtle.
    """

    def setup(self, values):
        super().setup(values)

        nbr_turtles = int(values['nbr_turtles'])
        for i in range(nbr_turtles):
            # Adds itself to self.turtles and to its patch's list of Turtles.
            turtle = self.turtle_class()

            # Give each turtle a random initial velocity.
            turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)

    def step(self, event, values):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            while random() < 0.02 or turtle.vel.x == 0 == turtle.vel.y or abs(turtle.vel.x) + abs(turtle.vel.y) > 4:
                turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))
            turtle.move_by_vel(values['Bounce?'])

        for patch in self.patches.flat:
            # self.update_patch_color(patch, self.turtles)
            patch.update_collision_color(self.turtles)


def main():
    se.SimEngine.SIM_ENGINE = se.SimEngine()

    se.SimEngine.WORLD = CollisionRect_World(patch_class=CollisionRect_Patch)

    gui_elements = [sg.Text('number of turtles'), sg.Slider(key='nbr_turtles',
                                                            range=(1, 10),
                                                            default_value=3,
                                                            orientation='horizontal',
                                                            pad=((0, 50), (0, 20))),
                    sg.Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    caption = se.SimEngine.extract_class_name(CollisionRect_World)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
