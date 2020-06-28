
from math import pi
from random import choice, randint

from core.gui import KNOWN_FIGURES
from core.pairs import center_pixel
from core.sim_engine import gui_get
from core.world_patch_block import World


class Synchronized_Agent_World(World):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The following two keep track of the agent's orientation between steps for breathing and moving twitchily.
        self.breathing_phase = None
        # Used to keep track of the agents' heading from one step to the next.
        # Must be set at the start of each step() when moving twitchily.
        self.cached_heading = None

        # The sort of action we are taking.
        self.current_figure = None

        # To see if the agents are approaching the inner or outer limit, look at just this one agent.
        self.reference_agent = None

    def breathe(self):
        for agent in World.agents:
            if self.breathing_phase == 'inhale':
                agent.turn_left(180)
            agent.forward()

    def do_a_step(self):
        if self.current_figure in ['clockwise', 'counter-clockwise']:
            r = self.reference_agent.distance_to_xy(center_pixel())
            self.go_in_circle(r)
        elif self.current_figure == 'breathe':
            self.breathe()
        elif self.current_figure == 'twitchy':
            self.go_twitchily()
        else:
            print(f'Error. No current figure: ({self.current_figure})')

    def go_in_circle(self, r):
        """ Recall that at the start of each step the agent is set to point to the center. """
        for agent in World.agents:
            agent.turn_left(90 if self.current_figure == 'clockwise' else -90)
            agent.forward(2 * pi * r / 360)

    def go_twitchily(self):
        twitchy_delta = randint(-90, 90) if self.ticks % 30 == 0 else 0
        for agent in World.agents:
            agent.set_heading(agent.cached_heading)
            agent.turn_right(twitchy_delta)
            agent.forward()
            agent.cached_heading = agent.heading

    def grow_shrink(self, grow_or_shrink):
        """
        Called when the agent gets to close too the center or too far away.
        It is not a figure. The agents may be performing any figure. This
        simple
        """
        offset = choice([-30, 30])
        for agent in World.agents:

            # At each step, the agents start pointing to the center.
            if grow_or_shrink == 'grow':
                agent.turn_right(180)
            agent.forward()

            # This is needed in case we are moving twitchily.
            agent.cached_heading = agent.heading + offset

            # Set the breathing phase in case we are currently breathing.
            self.breathing_phase = 'inhale' if grow_or_shrink == 'grow' else 'exhale'

    def setup(self):
        nbr_agents = gui_get('nbr_agents')
        shape_name = gui_get('shape')
        self.create_ordered_agents(nbr_agents, shape_name=shape_name, radius=100)
        self.reference_agent = list(World.agents)[0]
        twitchy_turn = randint(0, 360)
        for agent in World.agents:
            self.current_figure = gui_get('figure')
            self.breathing_phase = 'inhale'
            if self.current_figure in ['clockwise', 'counter-clockwise']:
                agent.turn_right(90 if self.current_figure == 'clockwise' else -90)
            elif self.current_figure == 'twitchy':
                agent.turn_right(twitchy_turn)
            agent.cached_heading = agent.heading

    def step(self):
        # For simplicity, start each step by having all agents face the center.
        for agent in World.agents:
            agent.face_xy(center_pixel())
            # Emergency action is going beyond the inner and outer limits.
        if self.take_emergency_action():
            return
        self.current_figure = gui_get('figure')
        self.do_a_step()

    def take_emergency_action(self):
        if self.reference_agent.distance_to_xy(center_pixel()) >= 250:
            self.grow_shrink('shrink')
            return True
        elif self.reference_agent.distance_to_xy(center_pixel()) <= 50:
            self.grow_shrink('grow')
            return True
        return False


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [[
                   sg.Combo(KNOWN_FIGURES, key='shape',
                            default_value='netlogo_figure', pad=((0, 9), (0, 0)),
                            tooltip='Shape of element'),
                   sg.Slider(key='nbr_agents', range=(1, 100), default_value=18, size=(10, 20),
                             orientation='horizontal', pad=((0, 0), (0, 20)),
                             tooltip='Number of elements'),
                   ],
                    # sg.Slider(range=(3, 10), key='sides', default_value=5, size=(8, 20),
                    #           orientation='horizontal', pad=((0, 0), (0, 20)))],

                  [sg.Text('Figure to trace'),
                   sg.Combo(['breathe', 'clockwise', 'counter-clockwise', 'twitchy'], key='figure',
                            default_value='clockwise')]
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Synchronized_Agent_World, 'Synchronized agents', gui_left_upper)
