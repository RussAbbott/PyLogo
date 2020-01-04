
from core_elements import Patch, Turtle
import sim_engine as se

import os

import pygame as pg

import PySimpleGUI as sg

"""
    Demo of integrating PyGame with PySimpleGUI.
    A similar technique may be possible with WxPython.
    To make it work on Linux, set SDL_VIDEODRIVER as
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""


class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model",
                 screen_pixel_width=816, screen_pixel_height=816,
                 default_fps=60):
        # --------------------- PySimpleGUI window layout and creation --------------------
        self.DISPLAY_SHAPE = (screen_pixel_width, screen_pixel_height)
        self.LOWER_LEFT_PIXEL = (self.DISPLAY_SHAPE[1]-1, 0)
        self.UPPER_RIGHT_PIXEL = (0, self.DISPLAY_SHAPE[0]-1)

        self.CTRL_D = 'D:68'
        self.CTRL_d = 'd:68'
        self.ESCAPE = 'Escape:27'
        self.EXIT = 'Exit'
        self.FPS = 'FPS'
        self.GO = 'go'
        self.GO_ONCE = 'go once'
        self.NORMAL = 'normal'
        self.Q = 'Q'
        self.q = 'q'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.idle_fps = 10

        layout = [     # [sg.Text('Test of PySimpleGUI with PyGame')],
                       # [sg.Graph(screen-shape, (0, 0), shape,
                       # sg.Graph(SHAPE, lower-left, upper-right,
                      [sg.Graph(self.DISPLAY_SHAPE,
                                self.LOWER_LEFT_PIXEL, self.UPPER_RIGHT_PIXEL,
                                background_color='black',
                                key='-GRAPH-')],

                      model_gui_elements,

                      [sg.Button(self.SETUP), sg.Button(self.GO_ONCE), sg.Button(self.GO, pad=((0, 50), (0, 0))),
                       sg.Button(self.STOP, button_color=('white', 'darkblue')),
                       sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT),
                       sg.Text(self.FPS, pad=((100, 10), (0, 0)), tooltip='Frames per second'),
                       sg.Slider(key=self.FPS, range=(1, 100), orientation='horizontal', tooltip='Frames per second',
                                 default_value=default_fps, pad=((0, 0), (0, 20)))]
                 ]

        self.window = sg.Window(caption, layout, finalize=True, return_keyboard_events=True)
        self.graph = self.window['-GRAPH-']

        # -------------- Magic code to integrate PyGame with tkinter -------
        embed = self.graph.TKCanvas
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        # # ----------------------------- PyGame Code -----------------------------
        pg.init()
        self.screen = pg.display.set_mode(self.DISPLAY_SHAPE)
        # se.SCREEN_RECT = self.screen.get_rect()
        # se.CENTER_PIXEL = se.PixelVector2(round(self.DISPLAY_SHAPE[0]/2), round(self.DISPLAY_SHAPE[1]/2))
        self.default_fps = default_fps
        self.fps = default_fps

    def run_model(self):
        # simEngine = se.SIM_ENGINE
        while True:
            (event, values) = self.window.read(timeout=10)
            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                return self.EXIT
            if event == self.STOP or se.WORLD.done():
                break
            se.TICKS += 1
            se.WORLD.step(event, values)
            se.draw(self.screen)
            se.CLOCK.tick(self.fps)

        se.WORLD.final_thoughts()
        return self.NORMAL

    def start(self, world_class, patch_class=Patch, turtle_class=Turtle):
        # simEngine = se.SIM_ENGINE

        world_class(patch_class=patch_class, turtle_class=turtle_class)

        # Not getting any keyboard events. Always returns False.
        pg.event.set_grab(False)
        event = None
        while event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)

            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                self.window.close()
                break

            if event == self.SETUP:
                se.WORLD.setup(values)
                se.draw(self.screen)

            if event == self.GO_ONCE:
                se.WORLD.step(event, values)
                se.draw(self.screen)

            if event == self.GO:
                returned_value = self.run_model()
                if returned_value == self.EXIT:
                    self.window.close()
                    break

            se.CLOCK.tick(self.idle_fps)
