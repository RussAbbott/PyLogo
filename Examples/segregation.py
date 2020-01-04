
import PyLogo.core.static_values as static
from PyLogo.core.core_elements import World, Patch, Turtle
from PyLogo.core.sim_engine import SimpleGUI

from pygame import Color

from random import choice, randint


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

    def find_new_spot_if_unhappy(self, empty_patches):
        """
        If this turtle is unhappy, move it to an empty patch where it is happy.
        Keep track of the empty patches instead of wandering around looking for one.
        The original NetLogo code doesn't check to see if the turtle would be happy in its new spot.
        (Doing so doesn't guarantee that the formerly happy new neighbors in the new spot remain happy!)
        """
        while not self.is_happy:
            new_patch = empty_patches.pop()
            old_patch = self.patch()
            empty_patches.add(old_patch)
            self.move_to_patch(new_patch)
            self.update()

    def nearby_turtles(self):
        turtles_nearby_list = [tur for patch in self.patch().neighbors_8() for tur in patch.turtles]
        return turtles_nearby_list

    def update(self):
        """
        Determine whether this turtle is happy.
        """
        turtles_nearby_list = [tur for patch in self.patch().neighbors_8() for tur in patch.turtles]
        self.similar_nearby_count = len([tur for tur in turtles_nearby_list if tur.color == self.color])
        self.total_nearby_count = len(turtles_nearby_list)

        # Isolated turtles, i.e., with no nearby neighbors, are not considered happy. Also, don't divide by 0.
        self.is_happy = self.total_nearby_count > 0 and \
                        self.similar_nearby_count/self.total_nearby_count >= static.WORLD.pct_similar_wanted/100


class SegregationWorld(World):
    """
      percent-similar: on the average, what percent of a turtle's neighbors are the same color as that turtle?
      percent-unhappy: what percent of the turtles are unhappy?
    """
    def __init__(self, patch_class=Patch, turtle_class=SegregationTurtle):
        super().__init__(patch_class=patch_class, turtle_class=turtle_class)

        self.empty_patches = None
        self.pct_similar_wanted = None
        self.percent_similar = None
        self.percent_unhappy = None

    def done(self):
        return all(tur.is_happy for tur in self.turtles)

    def draw(self):
        for patch in self.patches.flat:
            if not patch.turtles:
                patch.draw()
        for turtle in self.turtles:
            turtle.draw()

    def setup(self, values):
        super().setup(values)
        self.pct_similar_wanted = values['% similar wanted']
        density = values['density']

        self.empty_patches = set()
        for patch in self.patches.flat:
            patch.set_color(Color('white'))

            # Create the Turtles. The density is approximate.
            if randint(0, 100) <= density:
                turtle = SegregationTurtle()
                turtle.set_color(choice([Color('blue'), Color('orange')]))
                turtle.move_to_patch(patch)
            else:
                self.empty_patches.add(patch)

        self.update_all()

    def step(self, event, values):
        for turtle in self.turtles:
            turtle.find_new_spot_if_unhappy(self.empty_patches)
        self.update_all()

    def update_all(self):
        # Update Turtles
        for turtle in self.turtles:
            turtle.update()

        # Update Globals
        similar_neighbors_count = sum(tur.similar_nearby_count for tur in self.turtles)
        total_neighbors_count = sum(tur.total_nearby_count for tur in self.turtles)
        percent_similar = round(100 * similar_neighbors_count / total_neighbors_count)
        if static.TICKS == 0:
            print()
        print(f'\t{static.TICKS:2}. agents: {len(self.turtles)};  %-similar: {percent_similar}%;  ', end='')

        unhappy_count = len([tur for tur in self.turtles if not tur.is_happy])
        percent_unhappy = round(100 * unhappy_count / len(self.turtles), 2)
        print(f'nbr-unhappy: {unhappy_count:3};  %-unhappy: {percent_unhappy}.')


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
