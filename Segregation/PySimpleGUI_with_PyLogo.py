
import os

import pygame as pg

# from pygame import display, event, K_d, K_ESCAPE, KMOD_CTRL, K_q, KEYDOWN, QUIT


import PySimpleGUI as sg

import sim_engine as se

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
                       sg.Text(self.FPS, pad=((100, 10), (0, 0))),
                       sg.Slider(key=self.FPS, range=(1, 100), orientation='horizontal',
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
        se.SimEngine.SCREEN_RECT = self.screen.get_rect()
        self.default_fps = default_fps
        self.fps = default_fps

    def idle_loop(self):
        simEngine = se.SimEngine.SIM_ENGINE

        # Not getting any keyboard events. Always returns False.
        pg.event.set_grab(False)
        event = None
        while event not in [self.ESCAPE, self.q, self.Q, self.CTRL_D, self.CTRL_d]:
            (event, values) = self.window.read(timeout=10)
            # if event != '__TIMEOUT__':
            #     print(f'{type(event)}: {event}')

            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                self.window.close()
                break

            if event == self.SETUP:
                simEngine.WORLD.setup(values)
                simEngine.draw(self.screen)

            if event == self.GO_ONCE:
                simEngine.WORLD.step()
                simEngine.draw(self.screen)

            if event == self.GO:
                returned_value = self.run_model()
                if returned_value == self.EXIT:
                    self.window.close( )
                    break

            simEngine.clock.tick(self.idle_fps)

    def run_model(self):
        simEngine = se.SimEngine.SIM_ENGINE
        while True:
            (event, values) = self.window.read(timeout=10)
            self.fps = values[self.FPS]

            if event in (None, self.EXIT):
                return self.EXIT
            if event == self.STOP or se.SimEngine.WORLD.done():
                break
            simEngine.ticks += 1
            se.SimEngine.WORLD.step()
            simEngine.draw(self.screen)
            simEngine.clock.tick(self.fps)

        se.SimEngine.WORLD.final_thoughts()
        return self.NORMAL
