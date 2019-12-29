
from pygame import Color

from random import choice, randint

from turtles_and_patches import BasicWorld, SimEngine, Turtle


class SegregationTurtle(Turtle):

    """
    turtles-own [
      happy?           ; for each turtle, indicates whether at least %-similar-wanted percent of
                       ;   that turtle's neighbors are the same color as the turtle
      similar-nearby   ; how many neighboring patches have a turtle with my color?
      other-nearby     ; how many have a turtle of another color?
      total-nearby     ; sum of previous two variables
    ]
    """
    def __init__(self):
        super().__init__()
        self.is_happy = None
        self.total_nearby_count = None
        self.similar_nearby_count = None
        self.is_happy = None

    def update(self):
        """
        ; in next two lines, we use "neighbors" to test the eight patches
        ; surrounding the current patch
        set similar-nearby count (turtles-on neighbors)  with [ color = [ color ] of myself ]
        set other-nearby count (turtles-on neighbors) with [ color != [ color ] of myself ]
        set total-nearby similar-nearby + other-nearby
        set happy? similar-nearby >= (%-similar-wanted * total-nearby / 100)
        end
        """
        turtles_nearby_list = [tur for patch in self.patch().neighbors_8() for tur in patch.turtles]
        self.similar_nearby_count = len([tur for tur in turtles_nearby_list if tur.color == self.color])
        self.total_nearby_count = len(turtles_nearby_list)
        # Isolated turtles are not considered happy.
        # Also, don't divide by 0.
        self.is_happy = self.total_nearby_count > 0 and \
                        self.similar_nearby_count/self.total_nearby_count >= SimEngine.WORLD.pct_similar_wanted/100

        patch = self.patch()
        on_boundary = 0 in patch.row_col
        if on_boundary and self.similar_nearby_count == 0 and self.is_happy:
            print(str(self), self.is_happy)



class SegregationWorld(BasicWorld):

    """
    globals [
      percent-similar  ; on the average, what percent of a turtle's neighbors
                       ; are the same color as that turtle?
      percent-unhappy  ; what percent of the turtles are unhappy?
    ]
    """

    def __init__(self):
        super().__init__()
        self.density = None
        self.pct_similar_wanted = None
        self.percent_similar = None
        self.percent_unhappy = None
        # Make a copy of the patches. Initially all the patches are empty.
        self.empty_patches = set(patch for patch in self.patches.flat)

    def go_once(self):
        """
        if all? turtles [ happy? ] [ stop ]
        move-unhappy-turtles
        update-turtles
        update-globals
        """
        if all(tur.is_happy for tur in self.turtles):
            SimEngine.SIM_ENGINE.exit()
            return

        self.move_unhappy_turtles()

        self.update_turtles()
        self.update_globals()

    def find_new_spot(self, tur):
        old_empty_patches = len(self.empty_patches)
        new_patch = self.empty_patches.pop()
        old_patch = tur.patch()
        if old_patch in self.empty_patches:
            print(f' ==> {old_patch} already in self.empty_patches.  From {tur.pixel_pos}')
        self.empty_patches.add(old_patch)
        if old_empty_patches != len(self.empty_patches):
            print(f'{old_empty_patches} -> {len(self.empty_patches)}.')
        tur.move_to_patch(new_patch)

    def move_unhappy_turtles(self):
        for tur in self.turtles:
            if not tur.is_happy:
                self.find_new_spot(tur)

    def setup(self, density=90, pct_similar_wanted=30):
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
        self.pct_similar_wanted = pct_similar_wanted
        self.clear_all()
        for patch in self.patches.flat:
            patch.set_color(Color('white'))
            # The density is approximate
            if randint(0, 99) < density:
                turtle = SegregationTurtle()
                turtle.set_color(choice([Color('blue'), Color('orange')]))
                turtle.move_to_patch(patch)
                self.empty_patches.remove(patch)

        self.update_turtles()
        self.update_globals()

    def print_counts(self, id=''):
        """ For debugging  """
        blues = len([t for t in self.turtles if t.color == Color("blue")])
        oranges = len([t for t in self.turtles if t.color == Color("orange")])
        empty = len(self.empty_patches)
        print(f'{id}   blues: {blues}, orange: {oranges}, empty patches: {empty}, '
              f'total: {blues + oranges + empty}, =? {len(self.patches.flat)}')

    def step(self):
        self.go_once()

    def update_globals(self):
        similar_neighbors_count = sum(tur.similar_nearby_count for tur in self.turtles)
        total_neighbors_count = sum(tur.total_nearby_count for tur in self.turtles)
        percent_similar = round(100 * similar_neighbors_count / total_neighbors_count)
        print(f'{SimEngine.SIM_ENGINE.ticks:2}. '
              f'agents: {len(self.turtles)}; similar: {percent_similar}%; ', end='')

        unhappy_count = len([tur for tur in self.turtles if not tur.is_happy])
        percent_unhappy = round(100 * unhappy_count / len(self.turtles), 2)
        print(f'unhappy: {unhappy_count:3}; unhappy: {percent_unhappy}%.')

    def update_turtles(self):
        for turtle in self.turtles:
            turtle.update()


if __name__ == "__main__":
    SimEngine.SIM_ENGINE = SimEngine(caption="Segregation Model", fps=5)
    SimEngine.WORLD = SegregationWorld()
    SimEngine.WORLD.setup(density=95, pct_similar_wanted=40)
    SimEngine.SIM_ENGINE.run_model()
