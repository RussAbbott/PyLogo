
import PyLogo.core.core_elements as core
import PyLogo.core.gui as gui

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

        self.WORLD = None

        self.simple_gui = gui.SimpleGUI(model_gui_elements, caption=caption, patch_size=patch_size)
        self.window = gui.simple_gui.window

        pg.init()

    def run_model(self):
        while True:
            (event, values) = self.window.read(timeout=10)

            if event in (None, gui.simple_gui.EXIT):
                return gui.simple_gui.EXIT

            if event == 'GoStop':
                self.window[gui.simple_gui.GO_ONCE].update(disabled=False)
                break

            if self.WORLD.done():
                self.window['GoStop'].update(disabled=True)
                break

            # TICKS are our local counter for the number of times we have gone around this loop.
            self.WORLD.increment_ticks()

            self.WORLD.save_values_and_step(event, values)

            self.simple_gui.draw(self.WORLD)

            # The next line limits how fast the simulation runs and is not a counter.
            self.clock.tick(self.fps)

        self.WORLD.final_thoughts()
        return self.NORMAL

    def start(self, world_class, patch_class=core.Patch, turtle_class=core.Turtle):
        self.WORLD = world_class(patch_class=patch_class, turtle_class=turtle_class)

        # Let events come through pygame to this level.
        pg.event.set_grab(False)

        # Give event a value so that the while loop can look at it the first time through.
        event = None
        while event not in [self.ESCAPE, self.q, self.Q,
                            self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)

            if event in (None, gui.simple_gui.EXIT):
                self.window.close()
                break

            if event == gui.simple_gui.SETUP:
                self.window[gui.simple_gui.GOSTOP].update(disabled=False)
                self.window[gui.simple_gui.GO_ONCE].update(disabled=False)
                self.WORLD.reset_all()
                self.WORLD.save_values_and_setup(event, values)
                self.simple_gui.draw(self.WORLD)

            if event == gui.simple_gui.GO_ONCE:
                self.WORLD.increment_ticks()
                self.WORLD.save_values_and_step(event, values)()
                self.simple_gui.draw(self.WORLD)

            if event == gui.simple_gui.GOSTOP:
                self.window[gui.simple_gui.GOSTOP].update(text='stop', button_color=('white', 'red'))
                self.window[gui.simple_gui.GO_ONCE].update(disabled=True)
                self.window[gui.simple_gui.SETUP].update(disabled=True)
                returned_value = self.run_model()
                self.window['GoStop'].update(text='go', button_color=('white', 'green'))
                self.window[gui.simple_gui.SETUP].update(disabled=False)
                if returned_value == gui.simple_gui.EXIT:
                    self.window.close()
                    break

            self.clock.tick(self.idle_fps)
