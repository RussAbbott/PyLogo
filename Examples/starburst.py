import sim_engine as se

from itertools import cycle

from pySimpleGUI_with_PyLogo import SimpleGUI

from random import randint, random

from core_elements import World


class Starburst_World(World):
    """
    A starburst world of turtles.
    """

    def setup(self, values):
        super().setup(values)

        nbr_turtles = int(values['nbr_turtles'])
        for i in range(nbr_turtles):
            # Adds itself to self.turtles and to its patch's list of Turtles.
            self.turtle_class()

        initial_velocities = cycle([se.PixelVector2(-1, -1), se.PixelVector2(-1, 1),
                                    se.PixelVector2(0, 0),
                                    se.PixelVector2(1, -1), se.PixelVector2(1, 1)])
        for (turtle, vel) in zip(self.turtles, initial_velocities):
            turtle.velocity = vel


    def step(self, event, values):
        """
        Update the world by moving the turtles.
        """
        for turtle in self.turtles:
            turtle.move_by_velocity(values['Bounce?'])
            if se.TICKS > 200 and random() < 0.02:
                turtle.velocity = se.PixelVector2(randint(-2, 2), randint(-2, 2))


def main():

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [Text('number of turtles'),
                    Slider(key='nbr_turtles', range=(1, 100), default_value=25,
                           orientation='horizontal', pad=((0, 50), (0, 20))),
                    Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    simple_gui = SimpleGUI(gui_elements, caption='Starburst World')
    simple_gui.start(Starburst_World)


if __name__ == "__main__":
    main()
