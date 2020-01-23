from pygame.color import Color

from PyLogo.core.world_patch_block import Patch, World
from PyLogo.core.utils import hex_string_to_rgb

from random import randint


class Life_Patch(Patch):

    def __init__(self, *args, **kw_args):
        super().__init__(*args, color=Color('blue'), **kw_args)
        self.live_neighbors = 0
        self.is_alive = False
        self.fg_color = None
        
    def count_live_neighbors(self):
        self.live_neighbors = sum([1 for p in self.neighbors_8() if p.is_alive])
        
    def set_alive_or_dead(self, alive_or_dead: bool):
        self.is_alive = alive_or_dead
        self.set_color(self.fg_color if self.is_alive else self.base_color)


class Life_World(World):

    def mouse_click(self, xy):
        patch = self.pixel_to_patch(xy)
        patch.set_alive_or_dead(not patch.is_alive)

    def setup(self):
        bg_color_string = self.get_gui_value('background')
        bg_color = (0, 0, 0) if bg_color_string == '' else hex_string_to_rgb(bg_color_string)
        fg_color_string = self.get_gui_value('foreground')
        fg_color = (255, 255, 255) if fg_color_string == '' else hex_string_to_rgb(fg_color_string)
        for patch in self.patches:
            patch.set_color(bg_color)
            patch.base_color = bg_color
            patch.fg_color = fg_color
            patch.set_alive_or_dead(randint(0, 100) < 5)


    def step(self):
        # Count the live neighbors in the current state.
        for patch in self.patches:
            patch.count_live_neighbors()

        # Determine and set whether each patch is_alive in the next state.
        for patch in self.patches:
            is_alive = patch.live_neighbors == 3 or patch.is_alive and patch.live_neighbors == 2
            patch.set_alive_or_dead(is_alive)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('Initial density'),
                sg.Slider(key='density', range=(0, 50), resolution=5, size=(10, 20),
                          default_value=10, orientation='horizontal', pad=((0, 0), (0, 20)),
                          tooltip='The ratio of households to housing units')],

                [sg.Text('Select a foreground color'),
                 sg.ColorChooserButton('foreground')
                 ],

                [sg.Text('Select a background color'),
                 sg.ColorChooserButton('background')
                 ]
                ]


if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Life_World, 'Game of Life', gui_elements, patch_class=Life_Patch, bounce=None)
