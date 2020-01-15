
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
  turn-away ([heading] of nearest-neighbor) max-separate-turn
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
from statistics import mean


class Flocking_Agent(Agent):

    def __init__(self):
        screen_height = gui.SCREEN_PIXEL_HEIGHT()
        screen_width = gui.SCREEN_PIXEL_WIDTH()
        center_pixel = utils.PixelVector(uniform(0, screen_width), uniform(0, screen_height))
        color = utils.color_random_variation(Color('yellow'))
        super().__init__(center_pixel=center_pixel, color=color, scale=1)
        self.speed = 2

    def align(self, flockmates):
        max_align_turn = self.get_gui_value('max-align-turn')
        average_flockmate_heading = self.average_flockmate_heading(flockmates)
        self.turn_toward_or_away(average_flockmate_heading, max_align_turn)

    def average_flockmate_heading(self, flockmates):
        # dx and dy are the x and y components of traveling one unit in the heading direction.
        x = mean([utils.dx(flockmate.heading) for flockmate in flockmates])
        y = mean([utils.dy(flockmate.heading) for flockmate in flockmates])
        if x == 0 == y:
            return self.heading
        else:
            return utils.angle_to_heading((-1)*utils.atan2(y, x))

    def average_heading_toward_flockmates(self, flockmates):
        x = mean([utils.dx(self.heading_toward(flockmate)) for flockmate in flockmates])
        y = mean([utils.dy(self.heading_toward(flockmate)) for flockmate in flockmates])
        if x == 0 == y:
            return self.heading
        else:
            return utils.angle_to_heading((-1)*utils.atan2(y, x))

    def cohere(self, flockmates):
        max_cohere_turn = self.get_gui_value('max-cohere-turn')
        avg_heading_toward_flockmates = self.average_heading_toward_flockmates(flockmates)
        self.turn_toward_or_away(avg_heading_toward_flockmates, max_cohere_turn)

    def flock(self):
        self.speed = self.get_gui_value('speed')
        vision_limit_in_pixels = self.get_gui_value('vision') * gui.BLOCK_SPACING()
        flockmates = [agent for agent in self.the_world().agents
                      if agent is not self and self.distance_to(agent) < vision_limit_in_pixels]
        if len(flockmates) == 0:
            return
        nearest_neighbor = min(flockmates, key=lambda fm: self.distance_to(fm))

        if self.distance_to(nearest_neighbor) < self.get_gui_value('minimum separation') * gui.BLOCK_SPACING():
            self.separate(nearest_neighbor)
        else:
            self.align(flockmates)
            self.cohere(flockmates)

    def separate(self, nearest_neighbor):
        max_separate_turn = self.get_gui_value('max-separate-turn')
        self.turn_toward_or_away(nearest_neighbor.heading, max_separate_turn, toward=False)

    def turn_toward_or_away(self, new_heading, max_turn, toward=True):
        heading_delta = utils.subtract_headings(new_heading, self.heading)
        if not toward:
            heading_delta = 180 + heading_delta
        amount_to_turn = utils.turn_amount(heading_delta, max_turn)
        self.turn_right(amount_to_turn)


class Flocking_World(World):

    def setup(self):
        nbr_agents = self.get_gui_value('population')
        self.create_agents(nbr_agents)

    def step(self):
        for boid in self.agents:
            boid.flock()
            boid.forward()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [
                [sg.Text('population', pad=((0, 5), (20, 0))),
                 sg.Slider(key='population', range=(5, 250), resolution=5, default_value=20,
                           orientation='horizontal', size=(10, 20))],

                [sg.Text('vision', pad=((0, 5), (20, 0)),
                         tooltip='The number of patch-lengths that define the current flockmates'),
                 sg.Slider(key='vision', range=(1, 20), resolution=0.5, default_value=10, orientation='horizontal',
                           size=(10, 20), tooltip='The number of patch-lengths that define the current flockmates')],

                [sg.Text('speed', pad=((0, 5), (20, 0)),
                         tooltip='The speed of the agents'),
                 sg.Slider(key='speed', range=(0, 5), resolution=0.5, default_value=1, orientation='horizontal',
                           size=(10, 20), tooltip='The speed of the agents')],

                gui.HOR_SEP(30),

                [sg.Text('minimum separation', pad=((0, 5), (20, 0)),
                         tooltip='The minimum acceptable patch-lengths to nearest neighbor'),
                 sg.Slider(key='minimum separation', range=(1, 5), resolution=0.5, default_value=2, size=(10, 20),
                           orientation='horizontal',
                           tooltip='The minimum acceptable patch-lengths to nearest neighbor')],

                [sg.Text('max-separate-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn '
                                 'to move away from its nearest neighbor'),
                 sg.Slider(key='max-separate-turn', range=(1, 20), resolution=0.5, default_value=1.5,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn '
                                   'to move away from its nearest neighbor')],

                gui.HOR_SEP(30),

                [sg.Text('max-cohere-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn to stay with its flockmates'),
                 sg.Slider(key='max-cohere-turn', range=(1, 20), resolution=0.25, default_value=3,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn to stay with its flockmates')],

                [sg.Text('max-align-turn', pad=((0, 5), (20, 0)),
                         tooltip='The most degrees (in angles) an agent can turn when aligning with flockmates'),
                 sg.Slider(key='max-align-turn', range=(0, 20), resolution=0.25, default_value=5,
                           orientation='horizontal', size=(10, 20),
                           tooltip='The most degrees (in angles) an agent can turn when aligning with flockmates')],

                ]


if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Flocking_World, 'Flocking', gui_elements, agent_class=Flocking_Agent, bounce=None)
