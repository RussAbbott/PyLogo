
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
        self.STOP = 'Stop'
        self.SETUP = 'setup'
        self.GO_ONCE = 'go once'
        self.GO = 'go'

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
                       sg.Exit(button_color=('white', 'firebrick4'), key='Exit'),
                       sg.Text('FPS', pad=((100, 10), (0, 0))),
                       sg.Slider(key='fps', range=(1, 100), orientation='horizontal',
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
        self.fps = default_fps
        self.default_fps = default_fps


    @staticmethod
    def exit() -> bool:
        """
        Not work. Not getting keyboard events.
        """
        for ev in pg.event.get( ):
            if ev.type == pg.QUIT or \
                ev.type == pg.KEYDOWN and (ev.key == pg.K_ESCAPE or
                                           ev.key == pg.K_q or
                                           # The following tests for ctrl-d.
                                           # (See https://www.pygame.org/docs/ref/key.html)
                                           ev.key == pg.K_d and ev.mod & pg.KMOD_CTRL):
                return True
        return False

    def idle_loop(self):
        simEngine = se.SimEngine.SIM_ENGINE

        # Not getting any keyboard events. Always returns False.
        while not self.exit():

            (event, values) = self.window.read(timeout=10)
            self.fps = values['fps']

            if event in (None, 'Exit'):
                self.window.close()
                break

            if event == self.SETUP:
                simEngine.WORLD.setup(values)
                simEngine.draw(self.screen)

            if event == self.GO_ONCE:
                simEngine.WORLD.step()
                simEngine.draw(self.screen)

            if event == self.GO:
                # saved_fps = self.fps
                returned_value = self.run_model()
                # values['fps'] = self.default_fps
                if returned_value == 'Exit':
                    self.window.close( )
                    break

            simEngine.clock.tick(10)

    def read_values(self):
        (_, values) = self.window.read(timeout=10)
        return values

    def run_model(self):
        simEngine = se.SimEngine.SIM_ENGINE
        while True:
            (event, values) = self.window.read(timeout=10)
            self.fps = values['fps']

            if event in (None, 'Exit'):
                return 'Exit'
            if event == self.STOP or se.SimEngine.WORLD.done():
                break
            simEngine.ticks += 1
            se.SimEngine.WORLD.step()
            simEngine.draw(self.screen)
            simEngine.clock.tick(self.fps)

        se.SimEngine.WORLD.final_thoughts()
        return 'Normal'
