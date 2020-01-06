
from PyLogo.core.core_elements import Patch, Turtle
import PyLogo.core.gui as gui
import PyLogo.core.static_values as static

import pygame as pg
from pygame.time import Clock


class SimEngine:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=15):

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

        self.simple_gui = gui.SimpleGUI(model_gui_elements, caption=caption, patch_size=patch_size)
        self.window = self.simple_gui.window

        pg.init()

    def run_model(self):
        while True:
            (event, values) = self.window.read(timeout=10)
            # Allow the user to change the FPS dynamically.
            # self.fps = values[self.FPS]

            if event in (None, self.simple_gui.EXIT):
                return self.simple_gui.EXIT

            if event == 'GoStop':
                self.window['GoStop'].update(text='go', button_color=('white', 'green'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=False)
                self.window[self.simple_gui.SETUP].update(disabled=False)
                break

            if static.WORLD.done():
                self.window['GoStop'].update(text='go', disabled=True, button_color=('white', 'green'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=True)
                self.window[self.simple_gui.SETUP].update(disabled=False)
                break

            # static.TICKS are our local counter for the number of times we have gone around this loop.
            static.TICKS += 1
            static.WORLD.step(event, values)
            self.simple_gui.draw()

            # The next line limits how fast the simulation runs and is not a counter.
            self.clock.tick(self.fps)

        static.WORLD.final_thoughts()
        return self.NORMAL

    def start(self, world_class, patch_class=Patch, turtle_class=Turtle):
        world_class(patch_class=patch_class, turtle_class=turtle_class)

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
                static.WORLD.setup(values)
                self.simple_gui.draw()

            if event == self.simple_gui.GO_ONCE:
                static.TICKS += 1
                static.WORLD.step(event, values)
                self.simple_gui.draw()

            if event == self.simple_gui.GOSTOP:  # self.simple_gui.GO:
                self.window[self.simple_gui.GOSTOP].update(text='stop', button_color=('white', 'red'))
                self.window[self.simple_gui.GO_ONCE].update(disabled=True)
                self.window[self.simple_gui.SETUP].update(disabled=True)
                returned_value = self.run_model()
                if returned_value == self.simple_gui.EXIT:
                    # self.desired_patch_size = values[self.PATCH_SIZE_STRING]
                    # desired_patch_size = values[self.PATCH_SIZE_STRING]
                    self.window.close()
                    break

            self.clock.tick(self.idle_fps)
