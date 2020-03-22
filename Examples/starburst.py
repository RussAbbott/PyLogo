
from itertools import cycle
from random import random, uniform

from core.agent import Agent
from core.pairs import Velocity
from core.sim_engine import SimEngine
from core.world_patch_block import World


class Starburst_World(World):
    """
    A starburst world of agents.
    No special Patches or Agents.
    """

    def setup(self):
        nbr_agents = SimEngine.gui_get('nbr_agents')
        for _ in range(nbr_agents):
            # When created, a agent adds itself to self.agents and to its patch's list of Agents.
            # self.agent_class(scale=1)
            Agent(scale=1)

        initial_velocities = cycle([Velocity((-1, -1)), Velocity((-1, 1)),
                                    Velocity((0, 0)),
                                    Velocity((1, -1)), Velocity((1, 1))])
        for (agent, vel) in zip(World.agents, initial_velocities):
            agent.set_velocity(vel)

    def step(self):
        """
        Update the world by moving the agents.
        """
        for agent in World.agents:
            agent.move_by_velocity()
            if World.ticks > 125 and random() < 0.01:
                agent.set_velocity(Velocity((uniform(-2, 2), uniform(-2, 2))))


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [ [sg.Text('nbr agents', pad=((0, 5), (20, 0))),
                    sg.Slider(key='nbr_agents', range=(1, 101), resolution=25, default_value=25,
                              orientation='horizontal', size=(10, 20))] ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Starburst_World, 'Starburst', gui_left_upper, bounce=True, patch_size=9, board_rows_cols=(71, 71))
