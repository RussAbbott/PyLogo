
import PyLogo.core.core_elements as core
import PyLogo.core.utils as utils

from pygame.color import Color

from itertools import cycle

from random import random, uniform


class Starburst_World(core.World):
    """
    A starburst world of turtles.
    No special Patches or Turtles.
    """

    def setup(self):
        nbr_turtles = self.get_gui_value('nbr_turtles')
        for _ in range(nbr_turtles):
            # When created, a turtle adds itself to self.turtles and to its patch's list of Turtles.
            self.turtle_class(scale_factor=1)

        initial_velocities = cycle([utils.Velocity(-1, -1), utils.Velocity(-1, 1),
                                    utils.Velocity(0, 0),
                                    utils.Velocity(1, -1), utils.Velocity(1, 1)])
        for (turtle, vel) in zip(self.turtles, initial_velocities):
            turtle.set_velocity(vel)

        self.patches[25, 25].set_color(Color('white'))

    def step(self):
        """
        Update the world by moving the turtles.
        """
        for turtle in self.turtles:
            turtle.move_by_velocity()
            if core.WORLD.TICKS > 150 and random() < 0.01:
                turtle.set_velocity(utils.Velocity(uniform(-2, 2), uniform(-2, 2)))


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [ [sg.Text('nbr turtles', pad=((0, 5), (20, 0))),
                  sg.Slider(key='nbr_turtles', range=(1, 101), resolution=1, default_value=1,
                            orientation='horizontal', size=(10, 20))] ]


if __name__ == "__main__":
    from PyLogo.core.core_elements import PyLogo
    PyLogo(Starburst_World, gui_elements, 'Starburst')
