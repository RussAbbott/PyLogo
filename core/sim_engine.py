
import pygame as pg
from pygame.time import Clock

import core.gui as gui
from core.gui import FPS, GOSTOP, GO_ONCE, SimpleGUI


class SimEngine:

    event = None
    fps = 60
    values = None

    def __init__(self, gui_left_upper, caption="Basic Model", gui_right_upper=None,
                 patch_size=11, board_rows_cols=(51, 51), clear=None, bounce=None, fps=None):

        # Constants for the main loop in start() below.
        self.CTRL_D = 'D:68'
        self.CTRL_d = 'd:68'
        self.ESCAPE = 'Escape:27'
        self.NORMAL = 'normal'
        self.Q = 'Q'
        self.q = 'q'

        self.clock = Clock()
        SimEngine.fps = fps if fps else 60
        self.idle_fps = 10

        self.world = None

        self.simple_gui = SimpleGUI(gui_left_upper, caption=caption, gui_right_upper=gui_right_upper,
                                    patch_size=patch_size, board_rows_cols=board_rows_cols,
                                    clear=clear, bounce=bounce, fps=fps)
        self.graph_point = None

    def draw_world(self):
        """ Fill the screen with the background color, draw the world, and update the display. """
        self.simple_gui.fill_screen()
        self.world.draw()
        pg.display.update()

    @staticmethod
    def gui_get(key):
        """
        Widgets typically have a 'disabled' property. The following makes
        it possible to use 'enabled' as the negation of 'disabled'.
        """
        flip = key == 'enabled'
        if not SimEngine.values:
            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
        value = SimEngine.values.get(key, None) if not flip else not SimEngine.values.get('disabled', None)
        return int(value) if isinstance(value, float) and value == int(value) else value

    # @staticmethod
    # def gui_set(key, **kwargs):
    #     # Replacement of 'enabled' with 'disabled' is done in gui.gui-set.
    #     gui.gui_set(key, **kwargs)
    #
    @staticmethod
    def gui_set(key, **kwargs):
        """
        Widgets typically have a 'disabled' property. The following makes
        it possible to use 'enabled' as the negation of 'disabled'.
        """
        if 'enabled' in kwargs:
            value = kwargs.get('enabled')
            kwargs['disabled'] = not bool(value)
            kwargs.pop('enabled')
        widget = gui.WINDOW[key]
        widget.update(**kwargs)

    def model_loop(self):

        # Run this loop until the model signals it is finished or until the user stops it by pressing the Stop button.
        while True:
            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == FPS:
                SimEngine.fps = SimEngine.gui_get(FPS)

            if SimEngine.event == self.simple_gui.GRAPH:
                self.world.mouse_click(SimEngine.values['-GRAPH-'])

            if SimEngine.event == GOSTOP:
                SimEngine.gui_set(GO_ONCE, enabled=True)
                break

            elif self.world._done():
                SimEngine.gui_set(GOSTOP, enabled=False)
                break

            elif SimEngine.event == '__TIMEOUT__':
                # This increments the World's tick counter for the number of times we have gone around this loop.
                # Examples.starburst uses it to decide when to "explode." Look at its step method.
                self.world.increment_ticks()
                # Take a step in the simulation.
                self.world.step()
                # This line limits how fast the simulation runs. It is not a counter.
                self.clock.tick(SimEngine.fps)

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

    def top_loop(self, the_world, auto_setup=False):
        self.world = the_world
        self.draw_world()

        # Keep setup enabled in case the user wants to change from the default setup.
        # if auto_setup:
        #     SimEngine.gui_set('setup', enabled=False)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        while SimEngine.event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:

            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                gui.WINDOW.close()
                break

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == FPS:
                SimEngine.fps = SimEngine.gui_get(FPS)

            if not auto_setup and SimEngine.event == '__TIMEOUT__':
                continue

            if SimEngine.event == self.simple_gui.GRAPH:
                self.world.mouse_click(SimEngine.values['-GRAPH-'])

            elif auto_setup or SimEngine.event == self.simple_gui.SETUP:
                auto_setup = False
                SimEngine.gui_set(GOSTOP, enabled=True)
                SimEngine.gui_set(GO_ONCE, enabled=True)
                if SimEngine.gui_get('Clear?') in [True, None]:
                    self.world.reset_all()
                self.world.setup()

            elif SimEngine.event == GO_ONCE:
                self.world.increment_ticks()
                self.world.step()

            elif SimEngine.event == GOSTOP:
                SimEngine.gui_set(GOSTOP, text='stop', button_color=('white', 'red'))
                SimEngine.gui_set(GO_ONCE, enabled=False)
                SimEngine.gui_set(self.simple_gui.SETUP, enabled=False)
                returned_value = self.model_loop()
                SimEngine.gui_set(GOSTOP, text='go', button_color=('white', 'green'))
                SimEngine.gui_set(self.simple_gui.SETUP, enabled=True)
                self.world.final_thoughts()
                if returned_value == self.simple_gui.EXIT:
                    gui.WINDOW.close()
                    break
            else:
                # For anything else, e.g., a button the user defined.
                self.world.handle_event(SimEngine.event)

            self.draw_world()

            self.clock.tick(self.idle_fps)
