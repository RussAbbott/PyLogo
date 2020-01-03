import globals_and_utils as gu

from itertools import cycle

from PySimpleGUI_with_PyLogo import SimpleGUI

from random import randint, random

from sim_engine import SimEngine, World


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

        initial_velocities = cycle([gu.PixelVector2(-1, -1), gu.PixelVector2(-1, 1),
                                    gu.PixelVector2(0, 0),
                                    gu.PixelVector2(1, -1), gu.PixelVector2(1, 1)])
        for (turtle, vel) in zip(self.turtles, initial_velocities):
            turtle.vel = vel


    def step(self, event, values):
        """
        Update the world by moving the turtles.
        """
        for turtle in self.turtles:
            turtle.move_by_vel(values['Bounce?'])
            if gu.TICKS > 200 and random() < 0.02:
                turtle.vel = gu.PixelVector2(randint(-2, 2), randint(-2, 2))


def main():
    gu.SIM_ENGINE = SimEngine()

    gu.WORLD = Starburst_World()

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [Text('number of turtles'), Slider(key='nbr_turtles',
                                                      range=(1, 100),
                                                      default_value=25,
                                                      orientation='horizontal',
                                                      pad=((0, 50), (0, 20))),
                    Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    caption = gu.extract_class_name(Starburst_World)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
