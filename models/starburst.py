
from itertools import cycle

from core.agent import Agent
from core.gui import BLOCK_SPACING
from core.pairs import REP_COEFF, REP_EXPONENT, Velocity, force_as_dxdy
from core.sim_engine import gui_get
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Starburst_Agent(Agent):
    """
    A starburst world of agents.
    No special Patches or Agents.
    """

    forces = None

    def dont_hit_neighbors(self):
        """ Back away from to close neighbors """
        velocity = self.velocity
        influence_radius = gui_get('Influence radius')
        neighbors = self.agents_in_radius(influence_radius * BLOCK_SPACING())
        for neighbor in neighbors:
            force = Starburst_Agent.forces.get((neighbor, self), None)
            if force is None:
                force = force_as_dxdy(self.center_pixel, neighbor.center_pixel)
                # Add force to forces dictionary so that when we look for the same pair
                # in reverse we will get the inverted force, which we then use directly.
                Starburst_Agent.forces[(neighbor, self)] = force * (-1)
            velocity = velocity + force
        #  self.set_velocity(velocity.bound(1, 1, 1.5, 1.5))
        speed_factor = gui_get('Speed factor')
        self.set_velocity(normalize_dxdy(velocity, 1.5*speed_factor/100))

    def move(self):
        if World.ticks >= 190:
            self.dont_hit_neighbors()
        self.move_by_velocity()


class Starburst_World(World):
    """
    A starburst world of agents.
    No special Patches or Agents.
    """

    # noinspection DuplicatedCode
    def setup(self):
        nbr_agents = gui_get('nbr_agents')
        for _ in range(nbr_agents):
            # When created, a agent adds itself to World.agents and to its patch's list of Agents.

            # To create an agent:
            #         Agent(scale=1)
            # More generallly, though, you can use the agent_class the system knows about.
            self.agent_class(scale=1)

        initial_velocities = cycle([Velocity((-1, -1)), Velocity((-1, 1)),
                                    Velocity((0, 0)),
                                    Velocity((1, -1)), Velocity((1, 1))])
        for (agent, vel) in zip(World.agents, initial_velocities):
            agent.set_velocity(vel)

    def step(self):
        """
        Update the world by moving the agents.
        """
        # forces = {}
        Starburst_Agent.forces = {}
        for agent in World.agents:
            agent.move()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

# noinspection DuplicatedCode
gui_left_upper = [ [sg.Text('Number of agents', pad=((0, 5), (20, 0))),
                    sg.Slider(key='nbr_agents', range=(1, 101), resolution=25, default_value=25,
                              orientation='horizontal', size=(10, 20))],

                   [sg.Text('Repulsion coefficient', pad=((0, 10), (10, 0)), tooltip='Larger is stronger.'),
                    sg.Combo((0.5, 1.0, 1.5, 2.0, 2.5, 3.0), key=REP_COEFF, default_value=1.5,
                             size=(5, 20), tooltip='The relative strength of the repulsive force.',
                             pad=((0, 10), (10, 0)))],

                   [sg.Text('Repulsion exponent', pad=((0, 10), (20, 0)),
                            tooltip='Negative means raise to the power and divide (like gravity).\n'
                                    'Larger magnitude means distince reduces repulsive force more.'),
                    sg.Slider(range=(-3, 0), default_value=-2, orientation='horizontal', key=REP_EXPONENT,
                              pad=((0, 0), (0, 0)), size=(15, 20),
                              tooltip='Negative means raise to the power and divide (like gravity).\n'
                                      'Larger magnitude means distince reduces repulsive force more.')],

                   [sg.Text('Influence radius', pad=((0, 10), (20, 0)), tooltip='Influence radius'),
                    sg.Slider(range=(0, 20), default_value=10, orientation='horizontal', key='Influence radius',
                              pad=((0, 0), (0, 0)), size=(15, 20),
                              tooltip='Influence radius')],

                   [sg.Text('Speed factor', pad=((0, 10), (20, 0)), tooltip='Relative speed'),
                    sg.Slider(range=(0, 200), default_value=100, orientation='horizontal', key='Speed factor',
                              pad=((0, 0), (0, 0)), size=(15, 20),
                              tooltip='Relative speed')],

                   ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Starburst_World, 'Starburst', gui_left_upper, agent_class=Starburst_Agent, bounce=(True, False),
           patch_size=9, board_rows_cols=(71, 71))
