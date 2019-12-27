
from pygame import Color

from random import choice, random

from turtles_and_patches import BasicWorld, SimEngine, Turtle


# globals [
#   percent-similar  ; on the average, what percent of a turtle's neighbors
#                    ; are the same color as that turtle?
#   percent-unhappy  ; what percent of the turtles are unhappy?
# ]

# percent_similar = None
# percent_unhappy = None


class SegregationTurtle(Turtle):
    
    def __init__(self):
        super().__init__()
        self.happy = None
        self.turtles_nearby = None
        self.similar_nearby = None
        self.others_nearby = None
        self.happy = None

    def update(self):
        """
        to update-turtles
          ask turtles [
            ; in next two lines, we use "neighbors" to test the eight patches
            ; surrounding the current patch
            set similar-nearby count (turtles-on neighbors)  with [ color = [ color ] of myself ]
            set other-nearby count (turtles-on neighbors) with [ color != [ color ] of myself ]
            set total-nearby similar-nearby + other-nearby
            set happy? similar-nearby >= (%-similar-wanted * total-nearby / 100)
            ; add visualization here
            if visualization = "old" [ set shape "default" set size 1.3 ]
            if visualization = "square-x" [
              ifelse happy? [ set shape "square" ] [ set shape "X" ]
            ]
          ]
        end
        """
        self.turtles_nearby = set(tur for patch in self.patch( ).neighbors(n=8) for tur in patch.turtles())
        self.similar_nearby = set(tur for tur in self.turtles_nearby if tur.color == self.color)
        self.others_nearby = self.turtles_nearby - self.similar_nearby
        self.happy = len(self.similar_nearby)/len(self.turtles_nearby) >= SimEngine.WORLD.pct_similar_wanted/100

# turtles-own [
#   happy?           ; for each turtle, indicates whether at least %-similar-wanted percent of
#                    ;   that turtle's neighbors are the same color as the turtle
#   similar-nearby   ; how many neighboring patches have a turtle with my color?
#   other-nearby     ; how many have a turtle of another color?
#   total-nearby     ; sum of previous two variables
# ]




class SegregationWorld(BasicWorld):

    def __init__(self, nbr_turtles=0):
        super().__init__()
        self.density = None
        self.pct_similar_wanted = None

    def setup(self, density=90, pct_similar_wanted=40):
        """
        to setup
          clear-all
          ; create turtles on random patches.
          ask patches [
            set pcolor white
            if random 100 < density [   ; set the occupancy density
              sprout 1 [
                set color one-of ['blue' 'orange']
                set size 1
              ]
            ]
          ]
          update-turtles
          update-globals
          reset-ticks
        end
        """
        self.clear_all()
        for patch in self.patches:
            patch.color = Color('white')
            if random()*100 < density:
                turtle = SegregationTurtle()
                turtle.color = choice([Color('blue'), Color('orange')])
                turtle.move_to_patch(patch)
        self.update()

    def update(self):
        for turtle in self.turtles:
            turtle.update()
        # self.move_player()
        # for block in self.blocks:
        #     block.color = block.hit_color if collide_rect(block, self.player) else block.idle_color





if __name__ == "__main__":
    SimEngine.SIM_ENGINE = SimEngine(caption="Segregation Model")
    SimEngine.WORLD = SegregationWorld()
    SimEngine.WORLD.setup(density=90, pct_similar_wanted=40)
    SimEngine.SIM_ENGINE.run_model()
