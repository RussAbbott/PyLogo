
import PyLogo.core.static_values as static
from PyLogo.core.core_elements import World, Patch, Turtle
from PyLogo.core.sim_engine import SimpleGUI

from pygame import Color

from random import choice, randint


class SegregationTurtle(Turtle):

    def __init__(self):
        super().__init__()
        self.is_happy = None
        self.pct_similar = None

    def find_new_spot_if_unhappy(self, empty_patches):
        """
        If this turtle is happy, do nothing.
        If it's unhappy move it to an empty patch where it is happy if one can be found.
        Otherwise, move it to any empty patch.

        Keep track of the empty patches instead of wandering around looking for one.
        The original NetLogo code doesn't check to see if the turtle would be happy in its new spot.
        (Doing so doesn't guarantee that the formerly happy new neighbors in the new spot remain happy!)
        """
        if not self.is_happy:
            # Keep track of current patch. Will add to empty patches after this Turtle moves.
            current_patch = self.patch()
            # Find one of the best available patches.
            best_patch = max(empty_patches, key=lambda patch: self.pct_similarity_satisfied_here(patch))
            empty_patches.remove(best_patch)
            empty_patches.add(current_patch)
            self.move_to_patch(best_patch)

    def pct_similar_here(self, patch) -> int:
        """
        Returns an integer between 0 and 100 for the percent similar to neighbors.
        Returns 100 if no neighbors,
        """
        self.move_to_patch(patch)
        turtles_nearby_list = [tur for patch in self.patch().neighbors_8() for tur in patch.turtles]
        total_nearby_count = len(turtles_nearby_list)
        # Isolated turtles, i.e., with no nearby neighbors, are considered to have 100% similar neighbors.
        if total_nearby_count == 0:
            return 100
        similar_nearby_count = len([tur for tur in turtles_nearby_list if tur.color == self.color])
        similarity = round(100 * similar_nearby_count / total_nearby_count)
        return similarity

    def pct_similarity_satisfied_here(self, patch) -> float:
        """
        Returns the degree to which the similarity here satisfies pct_similar_wanted.
        Returns a fraction between 0 and 1.
        Never more than 1. Doesn't favor more similar patches over sufficiently similar patches.
        """
        return min(1.0, self.pct_similar_here(patch)/static.WORLD.pct_similar_wanted)


    def update(self):
        """
        Determine pct_similar and whether this turtle is happy.
        """
        self.pct_similar = self.pct_similar_here(self.patch())
        self.is_happy = self.pct_similar >= static.WORLD.pct_similar_wanted


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
        percent_similar = round(sum(turtle.pct_similar for turtle in self.turtles)/len(self.turtles))
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
                    Slider(key='% similar wanted', range=(1, 100), default_value=30,
                           orientation='horizontal', pad=((0, 50), (0, 20)),
                           tooltip='The percentage of similar people to make someone happy.')]

    simple_gui = SimpleGUI(gui_elements, caption="Segregation model")
    simple_gui.start(SegregationWorld)


if __name__ == "__main__":
    main( )
