from itertools import cycle

import PySimpleGUI as sg   # import run_model, read_values

from PySimpleGUI_with_PyLogo import SimpleGUI

from random import randint, random

import sim_engine as se


class Starburst_World(se.BasicWorld):
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
            if se.SimEngine.SIM_ENGINE.ticks > 200 and random() < 0.02:
                turtle.vel = se.PixelVector2(randint(-2, 2), randint(-2, 2))


def main():
    se.SimEngine.SIM_ENGINE = se.SimEngine()

    se.SimEngine.WORLD = Starburst_World()

    gui_elements = [sg.Text('number of turtles'), sg.Slider(key='nbr_turtles',
                                                            range=(1, 100),
                                                            default_value=25,
                                                            orientation='horizontal',
                                                            pad=((0, 50), (0, 20))),
                    sg.Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    caption = se.SimEngine.extract_class_name(Starburst_World)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
