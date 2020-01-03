
import globals_and_utils as gu
from pygame.color import Color
from pygame.sprite import collide_rect

from PySimpleGUI_with_PyLogo import SimpleGUI

from random import randint, random

from sim_engine import World, Patch, SimEngine


class CollisionRect_Patch(Patch):

    def __init__(self, row_col: gu.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('green')

    def update_collision_color(self, turtles):
        collides = any([collide_rect(self, turtle) for turtle in turtles])
        fill_color = self.hit_color if collides else self.color
        self.image.fill(fill_color)


class CollisionRect_World(World):
    """
    A world in which the patches change to green when intersecting with a turtle.
    """

    def setup(self, values):
        super().setup(values)

        nbr_turtles = int(values['nbr_turtles'])
        for i in range(nbr_turtles):
            # Adds itself to self.turtles and to its patch's list of Turtles.
            turtle = self.turtle_class()

            # Give each turtle a random initial velocity.
            turtle.vel = gu.PixelVector2(randint(-2, 2), randint(-2, 2))

        for patch in self.patches.flat:
            patch.update_collision_color(self.turtles)

    def step(self, event, values):
        """
        Update the world by moving the turtle and indicating the patches that intersect the turtle
        """
        for turtle in self.turtles:
            while random() < 0.02 or turtle.vel.x == 0 == turtle.vel.y or abs(turtle.vel.x) + abs(turtle.vel.y) > 4:
                turtle.vel = gu.PixelVector2(randint(-2, 2), randint(-2, 2))
            turtle.move_by_vel(values['Bounce?'])

        for patch in self.patches.flat:
            # self.update_patch_color(patch, self.turtles)
            patch.update_collision_color(self.turtles)


def main():
    SimEngine.SIM_ENGINE = SimEngine()

    SimEngine.WORLD = CollisionRect_World(patch_class=CollisionRect_Patch)

    from PySimpleGUI import Checkbox, Slider, Text
    gui_elements = [Text('number of turtles'), Slider(key='nbr_turtles',
                                                      range=(1, 10),
                                                      default_value=3,
                                                      orientation='horizontal',
                                                      pad=((0, 50), (0, 20))),
                    Checkbox('Bounce?', key='Bounce?', tooltip='Bounce off the edges of the screen?')]

    caption = gu.extract_class_name(CollisionRect_World)
    simple_gui = SimpleGUI(gui_elements, caption=caption)
    simple_gui.idle_loop()


if __name__ == "__main__":
    main()
