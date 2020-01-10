

"""
    turtles-own [speed]

    ;breed [circle-drawers cirdle-drawer]

    globals [turtle-size outer]

    to startup
      setup
    end

    to setup
      clear-all
      set turtle-size 5 ;; easier to see
      create-ordered-turtles number-of-turtles [
        set size turtle-size
        set speed 1
      ]
    ;  ask white-turtle [set color white]
      set outer 50
    ;  draw-circle outer white
      reset-ticks
    end

    ;to draw-circle [radius circle-color]
    ;  ask patches [if distancexy 0 0 >= 50 [set pcolor white]]
    ;  ;; Drawing this circle smoothes out the edges.
    ;  create-ordered-circle-drawers 360 [
    ;    set speed 0.35  ;; this is the size of each step the turtles take in a tick
    ;    fd radius  ;; move turtles to perimeter of circle
    ;    rt 90  ;; turtles face tangent to the circle
    ;    set color circle-color
    ;    set pen-size 10
    ;    pen-down
    ;    fd 2 * pi * radius / 360  ;; Each circle-drawer moves 1/360 around the circumference
    ;    die
    ;  ]
    ;end

    to go
      ask turtles [fd speed]
      let dist-turtle-0-to-0-0 [distancexy 0 0] of turtle 0
      if dist-turtle-0-to-0-0 > outer - turtle-size / 2 [ask turtles [ facexy 0 0 fd 1 ]]
      if random 100 < 15  [ask turtles [rt 25]]
      if random 100 < 15  [ask turtles [lt 25]]
      tick
    end

    to toggle-turtle-sizes
      if [size] of white-turtle = turtle-size [
        ask turtles [set size turtle-size / 2]
        ask white-turtle [set size turtle-size * 1.5]
        stop
      ]
      ask turtles [set size turtle-size]
    end

    to-report white-turtle
      report turtle (count turtles - 1)
    end
"""

import PyLogo.core.core_elements as core
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils

from math import pi

from random import random


class DrunkenTurtle_World(core.World):

    def __init__(self, patch_class=core.Patch, turtle_class=core.Turtle):
        super().__init__(patch_class=patch_class, turtle_class=turtle_class)
        self.reference_turtle = None
        self.current_figure_counter = 0
        self.current_figure = 'random'

    def setup(self):
        nbr_turtles = int(self.get_gui_value('nbr_turtles'))
        self.create_ordered_turtles(nbr_turtles)
        self.reference_turtle = list(self.turtles)[0]
        for turtle in self.turtles:
            turtle.speed = 1
            turtle.forward(100)
            turtle.turn_right(90)

    def go_in_circle(self, r):
        for turtle in self.turtles:
            turtle.forward(2 * pi * r / 360)
            turtle.turn_right(1)

    def go_randomly(self):
        for turtle in self.turtles:
            turtle.forward()

        if random() < 0.15:
            for turtle in self.turtles:
                turtle.turn_right(25)
        elif random() < 0.15:
            for turtle in self.turtles:
                turtle.turn_left(25)

    def grow_shrink(self):
        for turtle in self.turtles:
            turtle.face_xy(utils.CENTER_PIXEL())
            if self.current_figure == 'grow':
                turtle.turn_right(180)
            turtle.forward()

    def get_figure(self):
        self.current_figure = self.get_gui_value('figure')
        self.current_figure_counter = 100

    def step(self):
        if self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL()) >= 250 and self.current_figure != 'shrink':
            self.current_figure = 'shrink'
            self.current_figure_counter = 1

        elif self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL()) <= 50 and self.current_figure != 'grow':
            self.current_figure = 'grow'
            self.current_figure_counter = 1

        elif self.current_figure_counter == 0:
            self.get_figure()

        else:
            self.current_figure_counter -= 1

        if self.current_figure == 'circle':
            r = 100
            self.go_in_circle(r)
        elif self.current_figure == 'random':
            self.go_randomly( )
        elif self.current_figure == 'grow' or self.current_figure == 'shrink':
            self.grow_shrink()
        else:
            print(f'Error no figure: ({self.current_figure}, {self.current_figure_counter})')


def main():

    from PySimpleGUI import Checkbox, Combo, Slider, Text
    gui_elements = [[Text('nbr of turtles'),
                     Slider(key='nbr_turtles', range=(1, 100), default_value=16, size=(8, 20),
                            orientation='horizontal', pad=((0, 0), (0, 20)))],

                    [Text('Figure to trace'), Combo(['circle', 'random', 'square'], key='figure',
                                                    default_value='random')]
                    ]

    sim_engine = SimEngine(gui_elements, caption='Synchronized drunken turtles')
    sim_engine.start(DrunkenTurtle_World)


if __name__ == "__main__":
    main()
