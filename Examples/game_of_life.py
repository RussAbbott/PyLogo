from pygame.color import Color

import PyLogo.core.gui as gui
from PyLogo.core.gui import HOR_SEP
from PyLogo.core.utils import hex_string_to_rgb, rgb_to_hex_string
from PyLogo.core.world_patch_block import Patch, World

import PySimpleGUI as sg

from random import randint


class Life_Patch(Patch):

    bg_color = Color('black')
    fg_color = Color('white')

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)
        self.live_neighbors = 0
        self.is_alive = False

    def count_live_neighbors(self):
        self.live_neighbors = sum([1 for p in self.neighbors_8() if p.is_alive])
        
    def set_alive_or_dead(self, alive_or_dead: bool):
        self.is_alive = alive_or_dead
        self.set_color(Life_Patch.fg_color if self.is_alive else Life_Patch.bg_color)


class Life_World(World):

    WHITE = '#ffffff'
    BLACK = '#000000'

    fg_color_chooser = sg.ColorChooserButton('foreground', button_color=(WHITE, WHITE))
    bg_color_chooser = sg.ColorChooserButton('background', button_color=(BLACK, BLACK))

    SELECT_FOREGROUND_TEXT = 'Select foreground color'
    SELECT_BACKGROUND_TEXT = 'Select background color'

    def get_color_and_update_button(self, button, default_color_string, values=None):
        if not values:
            values = self.values
        key = button.get_text()
        color_string = values.get(key, '')
        if color_string in {'None', '', None}:
            color_string = default_color_string
        button.update(button_color=(color_string, color_string))
        color = hex_string_to_rgb(color_string)
        return color

    def get_colors(self):
        Life_Patch.bg_color = self.get_color_and_update_button(
                                            self.bg_color_chooser,
                                            default_color_string=rgb_to_hex_string(Life_Patch.bg_color))
        Life_Patch.fg_color = self.get_color_and_update_button(
                                            self.fg_color_chooser,
                                            default_color_string=rgb_to_hex_string(Life_Patch.fg_color))

    def handle_event_and_values(self):
        """
        This handles the color chooser, although in a round-about way because the color chooser
        can't generate events.
        """
        # Determine and select the desired color chooser.
        button = Life_World.fg_color_chooser if self.event == Life_World.SELECT_FOREGROUND_TEXT else \
                 Life_World.bg_color_chooser
        # Run it
        button.click()
        # Get the color choice by reading the window.
        (_event, values) = gui.WINDOW.read(timeout=10)

        # The default color_string is the string of the current color.
        default_color_string = rgb_to_hex_string(Life_Patch.fg_color
                                                 if self.event == Life_World.SELECT_FOREGROUND_TEXT
                                                 else Life_Patch.bg_color)
        color = self.get_color_and_update_button(button, default_color_string, values)

        # Set the color to the new choice
        if self.event == Life_World.SELECT_FOREGROUND_TEXT:
            Life_Patch.fg_color = color
        else:
            Life_Patch.bg_color = color

        # Update the patches.
        for patch in self.patches:
            patch.set_alive_or_dead(patch.is_alive)

    def mouse_click(self, xy):
        patch = self.pixel_to_patch(xy)
        patch.set_alive_or_dead(not patch.is_alive)

    def setup(self):
        self.get_colors()
        density = self.get_gui_value('density')
        for patch in self.patches:
            is_alive = randint(0, 100) < density
            patch.set_alive_or_dead(is_alive)

    def step(self):
        # Count the live neighbors in the current state.
        for patch in self.patches:
            patch.count_live_neighbors()

        # Determine and set whether each patch is_alive in the next state.
        self.get_colors()
        for patch in self.patches:
            is_alive = patch.live_neighbors == 3 or patch.is_alive and patch.live_neighbors == 2
            patch.set_alive_or_dead(is_alive)


# ############################################## Define GUI ############################################## #
gui_elements = [[sg.Text('Initial density'),
                sg.Slider(key='density', range=(0, 80), resolution=5, size=(10, 20),
                          default_value=35, orientation='horizontal', pad=((0, 0), (0, 20)),
                          tooltip='The ratio of alive cells to all cells')],

                [sg.Button('Select foreground color'), Life_World.fg_color_chooser],

                [sg.Button('Select background color'), Life_World.bg_color_chooser],

                HOR_SEP(),

                [sg.Text('Cells can be toggled when\nthe system is stopped.')],
                ]


if __name__ == "__main__":
    from PyLogo.core.agent import PyLogo
    PyLogo(Life_World, 'Game of Life', gui_elements, patch_class=Life_Patch, bounce=None, fps=10)
