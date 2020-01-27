
from core.pairs import center_pixel
from core.world_patch_block import World

from math import pi

from random import choice, randint


class Synchronized_Agent_World(World):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_agent = None
        self.current_figure = None
        self.breathing_phase = 'inhale'

    def breathe(self):
        for agent in self.agents:
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
        for agent in self.agents:
            agent.turn_left(90 if self.current_figure == 'clockwise' else -90)
            agent.forward(2 * pi * r / 360)

    def go_twitchily(self):
        twitchy_delta = randint(-90, 90) if self.ticks % 30 == 0 else 0
        for agent in self.agents:
            agent.set_heading(agent.cached_heading)
            agent.turn_right(twitchy_delta)
            agent.forward()
            agent.cached_heading = agent.heading

    def grow_shrink(self, grow_or_shrink):
        offset = choice([-30, 30])
        for agent in self.agents:
            # At each step, the agents start pointing to the center.
            if grow_or_shrink == 'grow':
                agent.turn_right(180)
            agent.forward()
            agent.cached_heading = agent.heading + offset
            # Set the breathing phase whether or not we are currently breathing.
            self.breathing_phase = 'inhale' if grow_or_shrink == 'grow' else 'exhale'

    def setup(self):
        nbr_agents = self.get_gui_value('nbr_agents')
        self.create_ordered_agents(nbr_agents)
        self.reference_agent = list(self.agents)[0]
        twitchy_turn = randint(0, 360)
        for agent in self.agents:
            agent.cached_heading = agent.heading
            agent.speed = 1
            agent.forward(100)
            self.current_figure = self.get_gui_value('figure')
            self.breathing_phase = 'inhale'
            if self.current_figure in ['clockwise', 'counter-clockwise']:
                agent.turn_right(90 if self.current_figure == 'clockwise' else -90)
            elif self.current_figure == 'twitchy':
                agent.turn_right(twitchy_turn)

    def step(self):
        # For simplicity, start each step by facing the center.
        for agent in self.agents:
            agent.face_xy(center_pixel())
        if self.take_emergency_action():
            return
        self.current_figure = self.get_gui_value('figure')
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
gui_elements = [[sg.Text('nbr of agents'),
                 sg.Slider(key='nbr_agents', range=(1, 100), default_value=18, size=(8, 20),
                           orientation='horizontal', pad=((0, 0), (0, 20)))],

                [sg.Text('Figure to trace'),
                 sg.Combo(['breathe', 'clockwise', 'counter-clockwise', 'twitchy'], key='figure',
                          default_value='clockwise')]
                ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Synchronized_Agent_World, 'Synchronized agents', gui_elements, bounce=None)
