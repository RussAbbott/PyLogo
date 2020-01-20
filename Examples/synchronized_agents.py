
import PyLogo.core.utils as utils
from PyLogo.core.world_patch_block import World

from math import pi

from random import choice, randint, random


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
            r = self.reference_agent.distance_to_xy(utils.center_pixel())
            self.go_in_circle(r)
        elif self.current_figure == 'breathe':
            self.breathe()
        elif self.current_figure == 'random':
            self.go_randomly()
        else:
            print(f'Error. No current figure: ({self.current_figure})')

    def go_in_circle(self, r):
        """ Recall that at the start of each step the agent is set to point to the center. """
        for agent in self.agents:
            agent.turn_left(90 if self.current_figure == 'clockwise' else -90)
            agent.forward(2 * pi * r / 360)

    def go_randomly(self):
        random_delta = randint(-5, 5) if random() < 0.25 else 0
        for agent in self.agents:
            agent.set_heading(agent.cached_heading)
            agent.turn_right(random_delta)
            agent.forward()
            agent.cached_heading = agent.heading

    def grow_shrink(self, grow_or_shrink):
        offset = choice([-30, 30])
        for agent in self.agents:
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
        for agent in self.agents:
            agent.cached_heading = agent.heading
            agent.speed = 1
            agent.forward(100)
            self.current_figure = self.get_gui_value('figure')
            self.breathing_phase = 'inhale'
            if self.current_figure in ['clockwise', 'counter-clockwise']:
                agent.turn_right(90 if self.current_figure == 'clockwise' else -90)

    def step(self):
        # For simplicity, start each step by facing the center.
        for agent in self.agents:
            agent.face_xy(utils.center_pixel())
        if self.take_emergency_action():
            return
        self.current_figure = self.get_gui_value('figure')
        self.do_a_step()
        
    def take_emergency_action(self):
        if self.reference_agent.distance_to_xy(utils.center_pixel()) >= 250:
            self.grow_shrink('shrink')
            return True
        elif self.reference_agent.distance_to_xy(utils.center_pixel()) <= 50:
            self.grow_shrink('grow')
            return True
        return False


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('nbr of agents'),
                 sg.Slider(key='nbr_agents', range=(1, 100), default_value=16, size=(8, 20),
                           orientation='horizontal', pad=((0, 0), (0, 20)))],

                [sg.Text('Figure to trace'),
                 sg.Combo(['breathe', 'clockwise', 'counter-clockwise', 'random'], key='figure',
                          default_value='clockwise')]
                ]

if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Synchronized_Agent_World, 'Synchronized agents', gui_elements, bounce=None)
