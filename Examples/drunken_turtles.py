

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

    def setup(self, values):
        nbr_turtles = int(values['nbr_turtles'])
        self.create_ordered_turtles(nbr_turtles)
        self.reference_turtle = list(self.turtles)[0]
        for turtle in self.turtles:
            turtle.speed = 1
            print(f'pos: {turtle}')
            turtle.forward(100)
            print(f'pos: {turtle}')
            turtle.turn_right(90)
            print(f'pos: {turtle}')
        # for turtle in sorted(self.turtles, key=lambda t: t.heading):
        #     print(f'pos: {turtle}')
        print( )

    def step(self, event, values):
        """
      ask turtles [fd speed]
      let dist-turtle-0-to-0-0 [distancexy 0 0] of turtle 0
      if dist-turtle-0-to-0-0 > outer - turtle-size / 2 [ask turtles [ facexy 0 0 fd 1 ]]
      if random 100 < 15  [ask turtles [rt 25]]
      if random 100 < 15  [ask turtles [lt 25]]

        to  move - along - circle[r]
            fd(pi * r / 180) * (speed / 50)
            rt  speed / 50

        end
        """
        r = 100
        for turtle in self.turtles:
            # turtle.forward(r)
            # turtle.forward((pi * r / 180)  * (turtle.speed/5 ))
            turtle.forward(2 * pi * r / 360)
            turtle.turn_right(1/360)
            print(f'pos: {turtle}')

        # for turtle in self.turtles:
        #     turtle.forward()
        #
        # if self.reference_turtle.distance_to_xy(utils.CENTER_PIXEL()) >= 300:
        #     for turtle in self.turtles:
        #         turtle.face_xy(utils.CENTER_PIXEL())
        #         turtle.forward(1)
        #
        # turned = False
        # if random() < 0.15:
        #     turned = True
        #     for turtle in self.turtles:
        #         turtle.turn_right(25)
        # elif random() < 0.15:
        #     turned = True
        #     for turtle in self.turtles:
        #         turtle.turn_left(25)
        #
        # if turned:
        #     print()
        #     for turtle in sorted(self.turtles, key=lambda t: t.heading):
        #         print(f'heading: {turtle.heading}; dist: {round(turtle.distance_to_xy(utils.CENTER_PIXEL()))}')
        #     print()
        #

def main():

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [[Text('number of turtles')],
                    [Slider(key='nbr_turtles', range=(int(1), int(72)), default_value=1,
                            orientation='horizontal', pad=((0, 50), (0, 20)))],
                    [Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]]

    sim_engine = SimEngine(gui_elements, caption='Synchronized drunken turtles')
    sim_engine.start(DrunkenTurtle_World)


if __name__ == "__main__":
    main()
