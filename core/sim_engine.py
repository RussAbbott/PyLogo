
from PyLogo.core.gui import SimpleGUI

import pygame as pg
from pygame.time import Clock


class SimEngine:

    sim_engine = None

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=11, bounce=True):

        SimEngine.sim_engine = self
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

        self.simple_gui = SimpleGUI(model_gui_elements, caption=caption, patch_size=patch_size, bounce=bounce)
        self.window = self.simple_gui.window

        pg.init()

    def draw_world(self):
        # Fill the screen with the background color, draw the world, and update the display.
        self.simple_gui.fill_screen()
        self.world.draw()
        pg.display.update()

    def run_model(self):
        while True:
            (event, values) = self.window.read(timeout=10)

            if event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            if event == 'GoStop':
                # Disable the GO_ONCE button
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                break

            if self.world.done():
                self.window['GoStop'].update(disabled=True)
                break

            # TICKS are our local counter for the number of times we have gone around this loop.
            self.world.increment_ticks()
            self.world.save_values_and_step(event, values)
            self.draw_world()
            # The next line limits how fast the simulation runs. It is not a counter.
            self.clock.tick(self.fps)

        # self.world.final_thoughts()
        return self.NORMAL

    def start(self, world_class, patch_class, turtle_class):
        self.world = world_class(patch_class, turtle_class)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        # Give event a value so that the while loop can look at it the first time through.
        event = None
        while event not in [self.ESCAPE, self.q, self.Q,
                            self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)

            if event in (None, self.simple_gui.EXIT):
                self.window.close()
                break

            if event == self.simple_gui.SETUP:
                self.window[self.simple_gui.GOSTOP].update(disabled=False)
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                self.world.reset_all()
                self.world.save_values_and_setup(event, values)
                self.draw_world()

            if event == self.simple_gui.GO_ONCE:
                self.world.increment_ticks()
                self.world.save_values_and_step(event, values)
                self.draw_world()

            if event == self.simple_gui.GOSTOP:
                self.window[self.simple_gui.GOSTOP].update(text='stop', button_color=('white', 'red'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=True)
                self.window[self.simple_gui.SETUP].update(disabled=True)
                returned_value = self.run_model()
                self.window['GoStop'].update(text='go', button_color=('white', 'green'))
                self.window[self.simple_gui.SETUP].update(disabled=False)
                self.world.final_thoughts()
                if returned_value == self.simple_gui.EXIT:
                    self.window.close()
                    break

            self.clock.tick(self.idle_fps)
