from itertools import cycle

from core.agent import Agent, PyLogo
from core.gui import BLOCK_SPACING
from core.pairs import REP_COEFF, REP_EXPONENT, Velocity, force_as_dxdy
from core.sim_engine import gui_get
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Starburst_Agent(Agent):

    def turn_away_from_neighbors(self, forces_cache):
        """ Back away from to close neighbors """
        velocity = self.velocity
        influence_radius = gui_get('Influence radius')
        neighbors = self.agents_in_radius(influence_radius * BLOCK_SPACING())
        for neighbor in neighbors:
            force = forces_cache.get((neighbor, self), None)
            if force is None:
                force = force_as_dxdy(self.center_pixel, neighbor.center_pixel)
                forces_cache[(neighbor, self)] = force * (-1)
            velocity = velocity + force
        speed_factor = gui_get('Speed factor')
        self.set_velocity(normalize_dxdy(velocity, 1.5*speed_factor/100))

    @staticmethod
    def update_agent_velocities():
        forces_cache = {}
        for agent in World.agents:
            agent.turn_away_from_neighbors(forces_cache)


class Starburst_World(World):

    def setup(self):
        nbr_agents = gui_get('nbr_agents')
        for _ in range(nbr_agents):
            self.agent_class(scale=1)

        vs = [Velocity((-1, -1)), Velocity((-1, 1)), Velocity((0, 0)), Velocity((1, -1)), Velocity((1, 1))]
        for (agent, vel) in zip(World.agents, cycle(vs)):
            agent.set_velocity(vel)

    def step(self):
        burst_tick = gui_get('Burst tick')
        if World.ticks >= burst_tick:
            Starburst_Agent.update_agent_velocities()

        Agent.update_agent_positions()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

gui_left_upper = [ [sg.Text('Number of agents', pad=((0, 5), (20, 0))),
                    sg.Slider(key='nbr_agents', range=(1, 101), resolution=25, default_value=25,
                              orientation='horizontal', size=(10, 20))],

                   [sg.Text('Burst tick', pad=((0, 10), (20, 0)), tooltip='The burst tick'),
                    sg.Slider(range=(0, 900), default_value=710, resolution=10, size=(15, 20),
                              orientation='horizontal', key='Burst tick', tooltip='The burst tick')],

                   [sg.Text('Repulsion coefficient', pad=((0, 10), (15, 0)), tooltip='Larger is stronger.'),
                    sg.Combo((0.5, 1.0, 1.5, 2.0, 2.5, 3.0), key=REP_COEFF, default_value=1.5,
                             size=(5, 20), tooltip='Larger is stronger.', pad=((0, 0), (15, 0)))],

                   [sg.Text('Repulsion exponent', pad=((0, 10), (20, 0)),
                            tooltip='Negative means raise to the power and divide (like gravity).\n'
                                    'Larger magnitude means distince reduces repulsive force more.'),
                    sg.Slider(range=(-3, 0), default_value=-2, orientation='horizontal',
                              key=REP_EXPONENT, size=(15, 20),
                              tooltip='Negative means raise to the power and divide (like gravity).\n'
                                      'Larger magnitude means distince reduces repulsive force more.')],

                   [sg.Text('Influence radius', pad=((0, 10), (20, 0)), tooltip='Influence radius'),
                    sg.Slider(range=(0, 20), default_value=10, orientation='horizontal',
                              key='Influence radius', size=(15, 20), tooltip='Influence radius')],

                   [sg.Text('Speed factor', pad=((0, 10), (20, 0)), tooltip='Relative speed'),
                    sg.Slider(range=(0, 200), default_value=100, orientation='horizontal',
                              key='Speed factor', size=(15, 20), tooltip='Relative speed')]      ]


if __name__ == "__main__":
    PyLogo(Starburst_World, 'Starburst', gui_left_upper, agent_class=Starburst_Agent,
           bounce=(True, False), patch_size=9, board_rows_cols=(71, 71))
