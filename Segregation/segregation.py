import PySimpleGUI as sg

from PySimpleGUI_with_PyLogo import SimpleGUI

from pygame import Color

from random import choice, randint

import sim_engine as se


class SegregationTurtle(se.Turtle):

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
                        self.similar_nearby_count/self.total_nearby_count >= se.SimEngine.WORLD.pct_similar_wanted/100


class SegregationWorld(se.BasicWorld):

    """
    globals [
      percent-similar  ; on the average, what percent of a turtle's neighbors
                       ; are the same color as that turtle?
      percent-unhappy  ; what percent of the turtles are unhappy?
    ]
    """

    def __init__(self):
        super().__init__(turtle_class=SegregationTurtle)
        self.density = None
        self.pct_similar_wanted = None
        self.percent_similar = None
        self.percent_unhappy = None
        # Make a copy of the patches. Initially all the patches are empty.
        self.empty_patches = None  # set(patch for patch in self.patches.flat)
        # Don't wrap around. (Shouldn't occur. But this will check for cases when it does.)
        se.SimEngine.WORLD.wrap = False

    def done(self):
        return all(tur.is_happy for tur in self.turtles)

    def draw(self, screen):
        for patch in self.patches.flat:
            if not patch.turtles:
                patch.draw(screen)
        for turtle in self.turtles:
            turtle.draw(screen)

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
        # new_patch.set_color(tur.color)

    def go_once(self):
        """
        if all? turtles [ happy? ] [ stop ]
        move-unhappy-turtles
        update-turtles
        update-globals
        """
        self.move_unhappy_turtles()

        self.update_turtles()
        self.update_globals()

    def move_unhappy_turtles(self):
        for tur in self.turtles:
            if not tur.is_happy:
                self.find_new_spot(tur)

    def print_counts(self, id=''):
        """ For debugging  """
        blues = len([t for t in self.turtles if t.color == Color("blue")])
        oranges = len([t for t in self.turtles if t.color == Color("orange")])
        empty = len(self.empty_patches)
        print(f'{id}   blues: {blues}, orange: {oranges}, empty patches: {empty}, '
              f'total: {blues + oranges + empty}, =? {len(self.patches.flat)}')

    @staticmethod
    def print_patch_details(patch):
        patch_color = 'blue' if patch.color == Color('blue') else 'orange'
        print(f'Patch{patch.row_col}, {patch_color}:  ', end='')
        for tur in patch.turtles:
            tur_color = 'blue' if tur.color == Color('blue') else 'orange'
            print(f'Turtle{tur.patch().row_col}, {tur.similar_nearby_count}, {tur.total_nearby_count} '
                  f'{tur.is_happy}, {tur_color}')
        print()

    def setup(self, values):  # density=90, pct_similar_wanted=30):
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
        self.pct_similar_wanted = values['% similar wanted']
        density = values['density']
        self.clear_all()
        # Make a copy of the patches. Initially all the patches are empty.
        self.empty_patches = set(patch for patch in self.patches.flat)
        for patch in self.patches.flat:
            patch.set_color(Color('white'))

            # The density is approximate.
            if randint(0, 99) < density:
                turtle = SegregationTurtle()
                turtle.set_color(choice([Color('blue'), Color('orange')]))
                turtle.move_to_patch(patch)
                self.empty_patches.remove(patch)

        self.update_turtles()
        self.update_globals()

    def step(self):
        self.go_once()

    def update_globals(self):
        similar_neighbors_count = sum(tur.similar_nearby_count for tur in self.turtles)
        total_neighbors_count = sum(tur.total_nearby_count for tur in self.turtles)
        percent_similar = round(100 * similar_neighbors_count / total_neighbors_count)
        print(f'\t{se.SimEngine.SIM_ENGINE.ticks:2}. '
              f'agents: {len(self.turtles)}; similar: {percent_similar}%; ', end='')

        unhappy_count = len([tur for tur in self.turtles if not tur.is_happy])
        percent_unhappy = round(100 * unhappy_count / len(self.turtles), 2)
        print(f'unhappy: {unhappy_count:3}; unhappy: {percent_unhappy}%.')

    def update_turtles(self):
        for turtle in self.turtles:
            turtle.update()


def main():
    se.SimEngine.SIM_ENGINE = se.SimEngine()  # caption="Segregation Model", fps=4)

    se.SimEngine.WORLD = SegregationWorld()

    gui_elements = [sg.Text('density'), sg.Slider(key='density',
                                                  range=(1, 100),
                                                  default_value=95,
                                                  orientation='horizontal',
                                                  pad=((0, 50), (0, 20))),
                    sg.Text('% similar wanted'), sg.Slider(key='% similar wanted',
                                                           range=(1, 100),
                                                           default_value=30,
                                                           orientation='horizontal',
                                                           pad=((0, 50), (0, 20)))]

    simple_gui = SimpleGUI(gui_elements, caption="Segregation model")
    simple_gui.idle_loop()


if __name__ == "__main__":
    main( )
