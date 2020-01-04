
from core_elements import Patch
import sim_engine as se

from pySimpleGUI_with_PyLogo import SimpleGUI

from pygame import Color

from random import choice, randint

from core_elements import World, Turtle


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
        Determine whether this turtle is happy.
        """
        turtles_nearby_list = [tur for patch in self.patch().neighbors_8() for tur in patch.turtles]
        self.similar_nearby_count = len([tur for tur in turtles_nearby_list if tur.color == self.color])
        self.total_nearby_count = len(turtles_nearby_list)
        # Isolated turtles, i.e., with no nearby neighbors, are not considered happy. Also, don't divide by 0.
        self.is_happy = self.total_nearby_count > 0 and \
                        self.similar_nearby_count/self.total_nearby_count >= se.WORLD.pct_similar_wanted/100


class SegregationWorld(World):
    """
      percent-similar: on the average, what percent of a turtle's neighbors are the same color as that turtle?
      percent-unhappy: what percent of the turtles are unhappy?
    """
    def __init__(self, patch_class=Patch, turtle_class=SegregationTurtle):
        super().__init__(patch_class=patch_class, turtle_class=turtle_class)
        self.density = None
        self.pct_similar_wanted = None
        self.percent_similar = None
        self.percent_unhappy = None
        self.empty_patches = None

    def done(self):
        return all(tur.is_happy for tur in self.turtles)

    def draw(self):
        for patch in self.patches.flat:
            if not patch.turtles:
                patch.draw()
        for turtle in self.turtles:
            turtle.draw()

    def find_new_spot(self, turtle):
        """
        Keep track of the empty patches instead of wandering around looking for one.
        """
        new_patch = self.empty_patches.pop()
        old_patch = turtle.patch()
        self.empty_patches.add(old_patch)
        turtle.move_to_patch(new_patch)

    def move_unhappy_turtles(self):
        for tur in self.turtles:
            if not tur.is_happy:
                self.find_new_spot(tur)

    def setup(self, values):
        super().setup(values)
        self.pct_similar_wanted = values['% similar wanted']
        density = values['density']

        # Initially all the patches are empty.
        self.empty_patches = set(patch for patch in self.patches.flat)
        for patch in self.patches.flat:
            patch.set_color(Color('white'))

            # Create the Turtles. The density is approximate.
            if randint(0, 99) < density:
                turtle = SegregationTurtle()
                turtle.set_color(choice([Color('blue'), Color('orange')]))
                turtle.move_to_patch(patch)
                self.empty_patches.remove(patch)

        self.update_all()

    def step(self, event, values):
        self.move_unhappy_turtles()
        self.update_all()

    def update_globals(self):
        similar_neighbors_count = sum(tur.similar_nearby_count for tur in self.turtles)
        total_neighbors_count = sum(tur.total_nearby_count for tur in self.turtles)
        percent_similar = round(100 * similar_neighbors_count / total_neighbors_count)
        if se.TICKS == 0:
            print()
        print(f'\t{se.TICKS:2}. '
              f'agents: {len(self.turtles)}; similar: {percent_similar}%; ', end='')

        unhappy_count = len([tur for tur in self.turtles if not tur.is_happy])
        percent_unhappy = round(100 * unhappy_count / len(self.turtles), 2)
        print(f'unhappy: {unhappy_count:3}; unhappy: {percent_unhappy}%.')

    def update_all(self):
        # Update turtles
        for turtle in self.turtles:
            turtle.update()

        # Update globals
        self.update_globals()



def main():

    from PySimpleGUI import Slider, Text
    gui_elements = [Text('density'),
                    Slider(key='density', range=(50, 95), default_value=95,
                           orientation='horizontal', pad=((0, 50), (0, 20)),
                           tooltip='The ratio of households to housing units'),

                    Text('% similar wanted'),
                    Slider(key='% similar wanted', range=(1, 60), default_value=35,
                           orientation='horizontal', pad=((0, 50), (0, 20)),
                           tooltip='The percentage of similar people to make someone happy.')]

    simple_gui = SimpleGUI(gui_elements, caption="Segregation model")
    simple_gui.start(SegregationWorld)


if __name__ == "__main__":
    main( )
