
import PyLogo.core.core_elements as core
from PyLogo.core.sim_engine import PyLogo, SimEngine
import PyLogo.core.utils as utils

from math import pi

from random import randint, random


class Synchronized_Turtle_World(core.World):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_turtle = None
        self.current_figure = None
        self.breathing_phase = 'inhale'

    def do_one_step(self):
        if self.current_figure in ['clockwise', 'counter-clockwise']:
            r = self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL())
            self.go_in_circle(r)
        elif self.current_figure == 'breathe':
            self.breathe()
        elif self.current_figure == 'random':
            self.go_randomly()
        else:
            print(f'Error. No current figure: ({self.current_figure})')

    def breathe(self):
        for turtle in self.turtles:
            if self.breathing_phase == 'inhale':
                turtle.turn_left(180)
            turtle.forward()

    def go_in_circle(self, r):
        for turtle in self.turtles:
            turtle.turn_left(90 if self.current_figure == 'clockwise' else -90)
            turtle.forward(2 * pi * r / 360)

    def go_randomly(self):
        for turtle in self.turtles:
            turtle.heading = turtle.cached_heading
            turtle.forward()

        if random() < 0.05:
            angle = randint(-180, 180)
            for turtle in self.turtles:
                turtle.turn_right(angle)

        for turtle in self.turtles:
            turtle.cached_heading = turtle.heading

    def grow_shrink(self, grow_or_shrink):
        for turtle in self.turtles:
            if grow_or_shrink == 'grow':
                turtle.turn_right(180)
            turtle.forward()
            # Set the breathing phase whether or not we are currently breathing.
            self.breathing_phase = 'inhale' if grow_or_shrink == 'grow' else 'exhale'

    def setup(self):
        nbr_turtles = self.get_gui_value('nbr_turtles')
        self.create_ordered_turtles(nbr_turtles)
        self.reference_turtle = list(self.turtles)[0]
        for turtle in self.turtles:
            turtle.cached_heading = turtle.heading
            turtle.speed = 1
            turtle.forward(100)
            turtle.turn_right(90)

    def step(self):
        # For simplicity, start each step by facing the center.
        for turtle in self.turtles:
            turtle.face_xy(utils.CENTER_PIXEL( ))
        if self.take_emergency_action():
            return
        self.current_figure = self.get_gui_value('figure')
        self.do_one_step()
        
    def take_emergency_action(self):
        if self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL()) >= 250:
            self.grow_shrink('shrink')
            return True
        elif self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL()) <= 50:
            self.grow_shrink('grow')
            return True
        return False


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('nbr of turtles'),
                 sg.Slider(key='nbr_turtles', range=(1, 100), default_value=16, size=(8, 20),
                           orientation='horizontal', pad=((0, 0), (0, 20)))],

                [sg.Text('Figure to trace'),
                 sg.Combo(['breathe', 'clockwise', 'counter-clockwise', 'random'], key='figure',
                          default_value='clockwise')]
                ]

if __name__ == "__main__":
    from PyLogo.core.sim_engine import PyLogo
    PyLogo(Synchronized_Turtle_World, gui_elements, 'Synchronized turtles', bounce=None)
