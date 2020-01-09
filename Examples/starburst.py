
import PyLogo.core.core_elements as core
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils

from itertools import cycle

from random import randint, random, uniform


class Starburst_World(core.World):
    """
    A starburst world of turtles.
    No special Patches or Turtles.
    """

    def setup(self):
        nbr_turtles = int(core.WORLD.values['nbr_turtles'])
        for _ in range(nbr_turtles):
            # When created a turtle adds itself to self.turtles and to its patch's list of Turtles.
            self.turtle_class()

        initial_velocities = cycle([utils.Velocity(-1, -1), utils.Velocity(-1, 1),
                                    utils.Velocity(0, 0),
                                    utils.Velocity(1, -1), utils.Velocity(1, 1)])
        for (turtle, vel) in zip(self.turtles, initial_velocities):
            turtle.velocity = vel

    def step(self):
        """
        Update the world by moving the turtles.
        """
        for turtle in self.turtles:
            turtle.move_by_velocity()
            if core.WORLD.TICKS > 150 and random() < 0.01:
                turtle.velocity = utils.Velocity(uniform(-2, 2), uniform(-2, 2))


def main():

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [[Text('nbr turtles', pad=((0, 5), (20, 0))),
                     Slider(key='nbr_turtles', range=(5, 100), resolution=5, default_value=25,
                            orientation='horizontal', size=(10, 20))],
                    ]

    sim_engine = SimEngine(gui_elements, caption='Starburst')
    sim_engine.start(Starburst_World)


if __name__ == "__main__":
    main()
