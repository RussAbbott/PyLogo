
# This file is the simulation engine. The engine consists of two loops. The top loop runs when the model is not
# running. It's in that loop where the user clicks, setup, go, exit, etc.
# The model loop runs the model. Once around that loop for each model tick.

from core.gui import SimpleGUI

import pygame as pg
from pygame.time import Clock


class SimEngine:

    event = None
    values = None

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=11, bounce=None, fps=None):

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

        self.simple_gui = SimpleGUI(model_gui_elements, caption=caption, patch_size=patch_size, bounce=bounce, fps=fps)
        self.window = self.simple_gui.window
        self.graph_point = None

    def draw_world(self):
        # Fill the screen with the background color, draw the world, and update the display.
        self.simple_gui.fill_screen()
        self.world.draw()
        pg.display.update()

    @staticmethod
    def get_gui_event():
        return SimEngine.event

    @staticmethod
    def get_gui_event_and_values():
        return (SimEngine.event, SimEngine.values)

    @staticmethod
    def get_gui_value(key):
        value = SimEngine.values.get(key, None)
        return int(value) if isinstance(value, float) and value == int(value) else value

    def model_loop(self):
        # Run this loop until the model signals it is finished or until the user stops it by pressing the Stop button.
        while True:
            (SimEngine.event, SimEngine.values) = self.window.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            fps = SimEngine.values.get('fps', None)
            if fps:
                self.fps = fps

            if SimEngine.event == self.simple_gui.GOSTOP:
                # Enable the GO_ONCE button
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                break

            elif self.world._done():
                self.window['GoStop'].update(disabled=True)
                break

            elif SimEngine.event == '__TIMEOUT__':
                # Take a step in the simulation.
                # TICKS are our local counter for the number of times we have gone around this loop.
                self.world.increment_ticks()
                # self.world.save_event_and_values(SimEngine.event, SimEngine.values)
                self.world.step()
                # The next line limits how fast the simulation runs. It is not a counter.
                self.clock.tick(self.fps)
            else:
                # self.world.save_event_and_values(SimEngine.event, SimEngine.values)
                self.world.handle_event_and_values()

            self.draw_world()

        return self.NORMAL

    def top_loop(self, world_class, patch_class, agent_class):
        self.world = world_class(patch_class, agent_class)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        # Give event a value so that the while loop can look at it the first time through.
        # event = None
        while SimEngine.event not in [self.ESCAPE, self.q, self.Q,
                                      self.CTRL_D, self.CTRL_d]:
            (SimEngine.event, SimEngine.values) = self.window.read(timeout=10)

            if SimEngine.event in (None, self.simple_gui.EXIT):
                self.window.close()
                break

            if SimEngine.event == '__TIMEOUT__':
                continue

            # self.world.save_event_and_values(event, values)

            if SimEngine.event == self.simple_gui.GRAPH:
                self.world.mouse_click(SimEngine.values['-GRAPH-'])

            elif SimEngine.event == self.simple_gui.SETUP:
                self.window[self.simple_gui.GOSTOP].update(disabled=False)
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                self.world.reset_all()
                self.world.setup()

            elif SimEngine.event == self.simple_gui.GO_ONCE:
                self.world.increment_ticks()
                self.world.step()

            elif SimEngine.event == self.simple_gui.GOSTOP:
                self.window[self.simple_gui.GOSTOP].update(text='stop', button_color=('white', 'red'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=True)
                self.window[self.simple_gui.SETUP].update(disabled=True)
                returned_value = self.model_loop()
                self.window['GoStop'].update(text='go', button_color=('white', 'green'))
                self.window[self.simple_gui.SETUP].update(disabled=False)
                self.world.final_thoughts()
                if returned_value == self.simple_gui.EXIT:
                    self.window.close()
                    break
            else:
                self.world.handle_event_and_values()

            self.draw_world()

            self.clock.tick(self.idle_fps)
