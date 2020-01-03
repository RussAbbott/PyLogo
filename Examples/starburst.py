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
            turtle.vel = vel


    def step(self, event, values):
        """
        Update the world by moving the turtles.
        """
        for turtle in self.turtles:
            turtle.move_by_vel(values['Bounce?'])
            if se.TICKS > 200 and random() < 0.02:
                turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))


def main():
    # se.SIM_ENGINE = SimEngine()

    se.WORLD = Starburst_World()

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [Text('number of turtles'), Slider(key='nbr_turtles',
                                                      range=(1, 100),
                                                      default_value=25,
                                                      orientation='horizontal',
                                                      pad=((0, 50), (0, 20))),
                    Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    caption = se.extract_class_name(Starburst_World)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
