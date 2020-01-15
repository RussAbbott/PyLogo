
import PyLogo.core.utils as utils
from PyLogo.core.world_patch_block import World

from pygame.color import Color

from itertools import cycle

from random import random, uniform


class Starburst_World(World):
    """
    A starburst world of agents.
    No special Patches or Agents.
    """

    def setup(self):
        nbr_agents = self.get_gui_value('nbr_agents')
        for _ in range(nbr_agents):
            # When created, a agent adds itself to self.agents and to its patch's list of Agents.
            self.agent_class(scale=1)

        initial_velocities = cycle([utils.Velocity(-1, -1), utils.Velocity(-1, 1),
                                    utils.Velocity(0, 0),
                                    utils.Velocity(1, -1), utils.Velocity(1, 1)])
        for (agent, vel) in zip(self.agents, initial_velocities):
            agent.set_velocity(vel)

        # So we can see where the agents are initially put. (Currently not accurate. Should be center of patch.)
        self.patches[25, 25].set_color(Color('white'))

    def step(self):
        """
        Update the world by moving the agents.
        """
        self.patches[25, 25].set_color(self.patches[0, 0].color)
        for agent in self.agents:
            agent.move_by_velocity()
            # if wpb.THE_WORLD.TICKS > 150 and random() < 0.01:
            if self.the_world().TICKS > 150 and random() < 0.01:
                agent.set_velocity(utils.Velocity(uniform(-2, 2), uniform(-2, 2)))


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [ [sg.Text('nbr agents', pad=((0, 5), (20, 0))),
                  sg.Slider(key='nbr_agents', range=(1, 101), resolution=25, default_value=25,
                            orientation='horizontal', size=(10, 20))] ]


if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Starburst_World, 'Starburst', gui_elements)
