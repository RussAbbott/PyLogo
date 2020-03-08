
# This file is the simulation engine. The engine consists of two loops. The top loop runs when the model is not
# running. It's in that loop where the user clicks, setup, go, exit, etc.
# The model loop runs the model. Once around that loop for each model tick.

import core.gui as gui
from core.gui import SimpleGUI

import pygame as pg
from pygame.time import Clock


class SimEngine:

    event = None
    values = None

    def __init__(self, gui_left_upper, caption="Basic Model", gui_right_upper=None,
                 patch_size=11, board_rows_cols=(51, 51), bounce=None, fps=None):

        # Constants for the main loop in start() below.
        self.CTRL_D = 'D:68'
        self.CTRL_d = 'd:68'
        self.ESCAPE = 'Escape:27'
        self.FPS = 'FPS'
        self.NORMAL = 'normal'
        self.Q = 'Q'
        self.q = 'q'

        self.clock = Clock()
        self.fps = 60
        self.idle_fps = 10

        self.world = None

        self.simple_gui = SimpleGUI(gui_left_upper, caption=caption, gui_right_upper=gui_right_upper,
                                    patch_size=patch_size, board_rows_cols=board_rows_cols, bounce=bounce, fps=fps)
        self.graph_point = None

    def draw_world(self):
        # Fill the screen with the background color, draw the world, and update the display.
        self.simple_gui.fill_screen()
        self.world.draw()
        pg.display.update()

    @staticmethod
    def gui_get(key):
        """
        Widgets typically have a 'disabled' property. The following makes
        it possibleto use 'enabled' as the negation of 'disabled'.
        """
        flip = key == 'enabled'
        if not SimEngine.values:
            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
        value = SimEngine.values.get(key, None) if not flip else not SimEngine.values.get('disabled', None)
        return int(value) if isinstance(value, float) and value == int(value) else value

    @staticmethod
    def gui_set(key, **kwargs):
        # Replacement of 'enabled' with 'disabled' is done in gui.gui-set.
        gui.gui_set(key, **kwargs)

    def model_loop(self):
        # Run this loop until the model signals it is finished or until the user stops it by pressing the Stop button.
        while True:
            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            fps = SimEngine.values.get('fps', None)
            if fps:
                self.fps = fps

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == self.simple_gui.GRAPH:
                self.world.mouse_click(SimEngine.values['-GRAPH-'])

            if SimEngine.event == self.simple_gui.GOSTOP:
                # Enable the GO_ONCE button
                # gui.WINDOW[self.simple_gui.GO_ONCE].update(disabled=False)
                SimEngine.gui_set(self.simple_gui.GO_ONCE, disabled=False)
                break

            elif self.world._done():
                # gui.WINDOW['GoStop'].update(disabled=True)
                SimEngine.gui_set('GoStop', disabled=True)
                break

            elif SimEngine.event == '__TIMEOUT__':
                # This increments the World's tick counter for the number of times we have gone around this loop.
                # Examples.starburst uses it to decide when to "explode." Look at its step method.
                self.world.increment_ticks()
                # Take a step in the simulation.
                self.world.step()
                # This line limits how fast the simulation runs. It is not a counter.
                self.clock.tick(self.fps)

            else:
                self.world.handle_event(SimEngine.event)

            self.draw_world()

        return self.NORMAL

    @staticmethod
    def set_grab_anywhere(allow_grab_anywhere):
        if allow_grab_anywhere:
            gui.WINDOW.grab_any_where_on()
        else:
            gui.WINDOW.grab_any_where_off()

    def top_loop(self, the_world):
        self.world = the_world
        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        while SimEngine.event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:

            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                gui.WINDOW.close()
                break

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == '__TIMEOUT__':
                continue

            if SimEngine.event == self.simple_gui.GRAPH:
                self.world.mouse_click(SimEngine.values['-GRAPH-'])

            elif SimEngine.event == self.simple_gui.SETUP:
                SimEngine.gui_set(self.simple_gui.GOSTOP, disabled=False)
                SimEngine.gui_set(self.simple_gui.GO_ONCE, disabled=False)
                self.world.reset_all()
                self.world.setup()

            elif SimEngine.event == self.simple_gui.GO_ONCE:
                self.world.increment_ticks()
                self.world.step()

            elif SimEngine.event == self.simple_gui.GOSTOP:
                SimEngine.gui_set(self.simple_gui.GOSTOP, text='stop', button_color=('white', 'red'))
                SimEngine.gui_set(self.simple_gui.GO_ONCE, disabled=True)
                SimEngine.gui_set(self.simple_gui.SETUP, disabled=True)
                returned_value = self.model_loop()
                SimEngine.gui_set(self.simple_gui.GOSTOP, text='go', button_color=('white', 'green'))
                SimEngine.gui_set(self.simple_gui.SETUP, disabled=False)
                self.world.final_thoughts()
                if returned_value == self.simple_gui.EXIT:
                    gui.WINDOW.close()
                    break
            else:
                # For anything else, e.g., a button the user defined.
                self.world.handle_event(SimEngine.event)

            self.draw_world()

            self.clock.tick(self.idle_fps)
