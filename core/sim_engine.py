
from time import sleep

import pygame as pg
from pygame.time import Clock

import core.gui as gui
from core.gui import FPS, GOSTOP, GO_ONCE, SimpleGUI


class SimEngine:

    auto_setup = None

    event = None
    fps = 60
    values = None

    simple_gui = None
    world = None
    

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

        SimEngine.simple_gui = SimpleGUI(gui_left_upper, caption=caption, gui_right_upper=gui_right_upper,
                                         patch_size=patch_size, board_rows_cols=board_rows_cols,
                                         clear=clear, bounce=bounce, fps=fps)
        self.graph_point = None

    @staticmethod
    def draw_world():
        """ Fill the screen with the background color, draw the world, and update the display. """
        SimEngine.simple_gui.fill_screen()
        SimEngine.world.draw()
        pg.display.update()

    @staticmethod
    def gui_get(key):
        """
        Widgets typically have a 'disabled' property. The following makes
        it possible to use 'enabled' as the negation of 'disabled'.
        """
        if not SimEngine.values:
            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
        value = SimEngine.values.get(key, None) if key != 'enabled' else not SimEngine.values.get('disabled', None)
        return int(value) if value != float('inf') and isinstance(value, float) and value == int(value) else value

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

            if SimEngine.event in (None, SimEngine.simple_gui.EXIT):
                return SimEngine.simple_gui.EXIT

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == FPS:
                SimEngine.fps = SimEngine.gui_get(FPS)

            if SimEngine.event.startswith(SimEngine.simple_gui.GRAPH):
                SimEngine.world.mouse_click(SimEngine.values['-GRAPH-'])

            if SimEngine.event == GOSTOP:
                SimEngine.gui_set(GO_ONCE, enabled=True)
                break

            elif SimEngine.world.done:
                SimEngine.gui_set(GOSTOP, enabled=True)
                SimEngine.gui_set(GO_ONCE, enabled=True)
                break

            elif SimEngine.event == '__TIMEOUT__':
                # This increments the World's tick counter for the number of times we have gone around this loop.
                # Examples.starburst uses it to decide when to "explode." Look at its step method.
                SimEngine.world.increment_ticks()
                # Take a step in the simulation.
                SimEngine.world.step()
                # This line limits how fast the simulation runs. It is not a counter.
                self.clock.tick(SimEngine.fps)

            else:
                SimEngine.world.handle_event(SimEngine.event)

            SimEngine.draw_world()

        return self.NORMAL

    @staticmethod
    def set_grab_anywhere(allow_grab_anywhere):
        if allow_grab_anywhere:
            gui.WINDOW.grab_any_where_on()
        else:
            gui.WINDOW.grab_any_where_off()

    def top_loop(self, the_world, auto_setup=False):
        SimEngine.world = the_world
        SimEngine.draw_world()
        SimEngine.auto_setup = auto_setup

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        while SimEngine.event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:

            (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)

            if SimEngine.event in (None, SimEngine.simple_gui.EXIT):
                gui.WINDOW.close()
                break

            self.set_grab_anywhere(self.gui_get('Grab'))

            if SimEngine.event == FPS:
                SimEngine.fps = SimEngine.gui_get(FPS)

            if not SimEngine.auto_setup and SimEngine.event == '__TIMEOUT__':
                continue

            if SimEngine.event.startswith(SimEngine.simple_gui.GRAPH):
                SimEngine.world.mouse_click(SimEngine.values['-GRAPH-'])

            elif SimEngine.auto_setup or SimEngine.event == SimEngine.simple_gui.SETUP:
                gui_set(SimEngine.simple_gui.SETUP, enabled=False)
                gui_set(GO_ONCE, enabled=False)
                SimEngine.world.reset_all()
                returned_value = SimEngine.world.setup()
                gui_set(SimEngine.simple_gui.SETUP, enabled=True)
                gui_set(GOSTOP, text='go', button_color=('white', 'green'), enabled=True)
                gui_set(GO_ONCE, enabled=True)
                SimEngine.auto_setup = False
                if returned_value == SimEngine.simple_gui.EXIT:
                    gui.WINDOW.close()
                    break

            elif SimEngine.event == GO_ONCE:
                SimEngine.gui_set(GOSTOP, text='stop', button_color=('white', 'red'), enabled=False)
                SimEngine.gui_set(GO_ONCE, enabled=False)
                SimEngine.gui_set(SimEngine.simple_gui.SETUP, enabled=False)
                SimEngine.world.increment_ticks()
                SimEngine.world.step()
                SimEngine.gui_set(SimEngine.simple_gui.SETUP, enabled=True)
                SimEngine.gui_set(GOSTOP, text='go', button_color=('white', 'green'), enabled=True)
                SimEngine.gui_set(GO_ONCE, enabled=True)

            elif SimEngine.event == GOSTOP:
                SimEngine.gui_set(GOSTOP, text='stop', button_color=('white', 'red'))
                SimEngine.gui_set(GO_ONCE, enabled=False)
                SimEngine.gui_set(SimEngine.simple_gui.SETUP, enabled=False)
                returned_value = self.model_loop()
                SimEngine.gui_set(GOSTOP, text='go', button_color=('white', 'green'), enabled=True)
                SimEngine.gui_set(GO_ONCE, enabled=True)
                SimEngine.gui_set(SimEngine.simple_gui.SETUP, enabled=True)
                SimEngine.world.final_thoughts()
                if returned_value == SimEngine.simple_gui.EXIT:
                    gui.WINDOW.close()
                    break
            else:
                # For anything else, e.g., a button the user defined.
                SimEngine.world.handle_event(SimEngine.event)

            SimEngine.draw_world()

            self.clock.tick(self.idle_fps)


# def draw_links(links, world_links_set, sleep_time=0.6):
#     cached_world_links_set = world_links_set
#
#     world_links_set = set()
#     gui_set(gui.GOSTOP, text='pause', button_color=('white', 'red'), enabled=True)
#     gui_set(gui.GO_ONCE, enabled=False)
#     gui_set(SimEngine.simple_gui.SETUP, enabled=False)
#     gui_set(SimEngine.simple_gui.EXIT, enabled=False)
#     paused = False
#     while links:
#
#         (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
#         if SimEngine.event == gui.GOSTOP:
#             gui_set(gui.GOSTOP,
#                     text='pause' if paused else 'continue',
#                     button_color=('white', 'red' if paused else 'green')
#                     )
#             paused = not paused
#             SimEngine.draw_world()
#         if not paused:
#             lnk = links.pop(0)
#             if lnk in world_links_set:
#                 world_links_set.remove(lnk)
#             world_links_set.add(lnk)
#             print(f'Drawing {lnk} (width, color): {(lnk.width, lnk.color)}')
#             SimEngine.draw_world()
#         if sleep_time:
#             sleep(sleep_time)
#     gui_set(SimEngine.simple_gui.EXIT, enabled=True)
#     gui_set(gui.GOSTOP, text='stop', button_color=('white', 'red'), enabled=True)
#     print()
#
#
def gui_get(key):
    """
    Widgets typically have a 'disabled' property. The following makes
    it possible to use 'enabled' as the negation of 'disabled'.
    """
    if SimEngine.values is None:
        (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
    value = SimEngine.values.get(key, None) if key != 'enabled' else not SimEngine.values.get('disabled', None)
    return int(value) if value != float('inf') and isinstance(value, float) and value == int(value) else value


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
    if widget is None:
        print(f'No widget with key {key}')
    widget.update(**kwargs)
