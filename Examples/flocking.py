
"""
turtles-own [
  flockmates         ;; agentset of nearby turtles
  nearest-neighbor   ;; closest one of our flockmates
]

to setup
  clear-all
  create-turtles population
    [ set color yellow - 2 + random 7  ;; random shades look nice
      set size 1.5  ;; easier to see
      setxy random-xcor random-ycor
      set flockmates no-turtles ]
  reset-ticks
end

to go
  ask turtles [ flock ]
  ;; the following line is used to make the turtles
  ;; animate more smoothly.
  repeat 5 [ ask turtles [ fd 0.2 ] display ]
  ;; for greater efficiency, at the expense of smooth
  ;; animation, substitute the following line instead:
  ;;   ask turtles [ fd 1 ]
  tick
end

to flock  ;; turtle procedure
  find-flockmates
  if any? flockmates
    [ find-nearest-neighbor
      ifelse distance nearest-neighbor < minimum-separation
        [ separate ]
        [ align
          cohere ] ]
end

to find-flockmates  ;; turtle procedure
  set flockmates other turtles in-radius vision
end

to find-nearest-neighbor ;; turtle procedure
  set nearest-neighbor min-one-of flockmates [distance myself]
end

;;; SEPARATE

to separate  ;; turtle procedure
  turn-away ([heading] of nearest-neighbor) max-sep-turn
end

;;; ALIGN

to align  ;; turtle procedure
  turn-towards average-flockmate-heading max-align-turn
end

to-report average-flockmate-heading  ;; turtle procedure
  ;; We can't just average the heading variables here.
  ;; For example, the average of 1 and 359 should be 0,
  ;; not 180.  So we have to use trigonometry.
  let x-component sum [dx] of flockmates
  let y-component sum [dy] of flockmates
  ifelse x-component = 0 and y-component = 0
    [ report heading ]
    [ report atan x-component y-component ]
end

;;; COHERE

to cohere  ;; turtle procedure
  turn-towards average-heading-towards-flockmates max-cohere-turn
end

to-report average-heading-towards-flockmates  ;; turtle procedure
  ;; "towards myself" gives us the heading from the other turtle
  ;; to me, but we want the heading from me to the other turtle,
  ;; so we add 180
  let x-component mean [sin (towards myself + 180)] of flockmates
  let y-component mean [cos (towards myself + 180)] of flockmates
  ifelse x-component = 0 and y-component = 0
    [ report heading ]
    [ report atan x-component y-component ]
end

;;; HELPER PROCEDURES

to turn-towards [new-heading max-turn]  ;; turtle procedure
  turn-at-most (subtract-headings new-heading heading) max-turn
end

to turn-away [new-heading max-turn]  ;; turtle procedure
  turn-at-most (subtract-headings heading new-heading) max-turn
end

;; turn right by "turn" degrees (or left if "turn" is negative),
;; but never turn more than "max-turn" degrees
to turn-at-most [turn max-turn]  ;; turtle procedure
  ifelse abs turn > max-turn
    [ ifelse turn > 0
        [ rt max-turn ]
        [ lt max-turn ] ]
    [ rt turn ]
end
"""

from pygame import Color

from PyLogo.core.agent import Agent
import PyLogo.core.gui as gui
import PyLogo.core.utils as utils
from PyLogo.core.world_patch_block import World

from random import uniform


class Flocking_Agent(Agent):

    def __init__(self):
        center_pixel = utils.Pixel_xy(uniform(0, gui.SCREEN_PIXEL_WIDTH()), uniform(0, gui.SCREEN_PIXEL_HEIGHT()))
        color = utils.color_random_variation(Color('yellow'))
        super().__init__(center_pixel=center_pixel, color=color, scale=1)

    def align(self, flockmates):
        max_align_turn = self.get_gui_value('max-align-turn')
        average_flockmate_heading = self.average_flockmate_heading(flockmates)
        amount_to_turn = utils.turn_toward_amount(self.heading, average_flockmate_heading, max_align_turn)
        self.turn_right(amount_to_turn)

    def average_flockmate_heading(self, flockmates):
        return self.average_of_headings(flockmates, lambda fm: fm.heading)

    def average_heading_toward_flockmates(self, flockmates):
        return self.average_of_headings(flockmates, lambda fm: self.heading_toward(fm))

    def cohere(self, flockmates):
        max_cohere_turn = self.get_gui_value('max-cohere-turn')
        avg_heading_toward_flockmates = self.average_heading_toward_flockmates(flockmates)
        amount_to_turn = utils.turn_toward_amount(self.heading, avg_heading_toward_flockmates, max_cohere_turn)
        self.turn_right(amount_to_turn)

    def flock(self):
        # NetLogo allows one to specify the units within the Gui widget.
        # Here we do it explicitly by multiplying by gui.BLOCK_SPACING().
        vision_limit_in_pixels = self.get_gui_value('vision') * gui.BLOCK_SPACING()
        flockmates = self.agents_in_radius(vision_limit_in_pixels)
        if len(flockmates) > 0:
            nearest_neighbor = min(flockmates, key=lambda flockmate: self.distance_to(flockmate))

            min_separation = self.get_gui_value('minimum separation') * gui.BLOCK_SPACING()
            if self.distance_to(nearest_neighbor) < min_separation:
                self.separate(nearest_neighbor)
            else:
                self.align(flockmates)
                self.cohere(flockmates)

    def separate(self, nearest_neighbor):
        max_separate_turn = self.get_gui_value('max-sep-turn')
        amount_to_turn = utils.turn_away_amount(self.heading, nearest_neighbor.heading, max_separate_turn)
        self.turn_right(amount_to_turn)


class Flocking_World(World):

    def setup(self):
        nbr_agents = self.get_gui_value('population')
        self.create_agents(nbr_agents)

    def step(self):
        # self.agents is the set of agents kept by the world
        for agent in self.agents:
            # agent.flock() resets agent's heading. Agent doesn't move.
            agent.flock()
            # Here's where agent actually moves. The actual move depends on the speed and the heading.
            speed = self.get_gui_value('speed')
            agent.forward(speed)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [
                [sg.Text('population', pad=((0, 5), (20, 0))),
                 sg.Slider(key='population', range=(0, 50), resolution=1, default_value=15,
                           orientation='horizontal', size=(10, 20))],

                [sg.Text('vision', pad=((0, 5), (20, 0)),
                         tooltip='The number of patch-lengths that define the current flockmates'),
                 sg.Slider(key='vision', range=(0, 20), resolution=0.5, default_value=5, orientation='horizontal',
                           size=(10, 20), tooltip='The number of patch-lengths that define the current flockmates')],

                [sg.Text('speed', pad=((0, 5), (20, 0)),
                         tooltip='The speed of the agents'),
                 sg.Slider(key='speed', range=(0, 10), resolution=0.5, default_value=2, orientation='horizontal',
                           size=(10, 20), tooltip='The speed of the agents')],

                gui.HOR_SEP(30),

                [sg.Text('min separation', pad=((0, 5), (20, 0)),
                         tooltip='The minimum acceptable patch-lengths to nearest neighbor'),
                 sg.Slider(key='minimum separation', resolution=0.5, range=(1, 5), default_value=1,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The minimum acceptable patch-lengths to nearest neighbor')],

                [sg.Text('max-sep-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn '
                                 'to move away from its nearest neighbor'),
                 sg.Slider(key='max-sep-turn', range=(0, 20), resolution=0.5, default_value=1.5,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn '
                                   'to move away from its nearest neighbor')],

                gui.HOR_SEP(30),

                [sg.Text('max-cohere-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn to stay with its flockmates'),
                 sg.Slider(key='max-cohere-turn', range=(0, 20), resolution=0.5, default_value=3,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn to stay with its flockmates')],

                [sg.Text('max-align-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn when aligning with flockmates'),
                 sg.Slider(key='max-align-turn', range=(0, 20), resolution=0.5, default_value=5,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn when aligning with flockmates')],

                ]


if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Flocking_World, 'Flocking', gui_elements, agent_class=Flocking_Agent, bounce=None)
