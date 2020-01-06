
import os

import PyLogo.core.utils as utils
import PyLogo.core.static_values as static

import pygame as pg
from pygame.time import Clock

import PySimpleGUI as sg

import tkinter as tk


"""
    Demo of integrating PyGame with PySimpleGUI.
    A similar technique may be possible with WxPython.
    To make it work on Linux, set SDL_VIDEODRIVER as
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""


# # Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
# PATCH_SIZE = 10
#
#
# def BLOCK_SPACING():
#     return PATCH_SIZE + 1
#
#
class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=15):

        # print(f'(SimpleGUI __init__) static.BLOCK_SPACING(): {static.BLOCK_SPACING()}')
        static.PATCH_SIZE = patch_size
        # print(f'(SimpleGUI __init__) static.BLOCK_SPACING(): {static.BLOCK_SPACING()}')

        # Constants for the main loop in start() below.
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

        self.clock = Clock()
        self.fps = 60
        self.idle_fps = 10

        # self.PATCH_SIZE_STRING = 'Patch size'

        # self.lower_left_pixel = (static.SCREEN_PIXEL_HEIGHT() - 1, 0)
        # self.upper_right_pixel = (0, static.SCREEN_PIXEL_WIDTH() - 1)
        self.screen_color = pg.Color(sg.RGB(50, 60, 60))

        self.caption = caption
        self.model_gui_elements = model_gui_elements

        screen_pixel_shape = (static.SCREEN_PIXEL_WIDTH(), static.SCREEN_PIXEL_HEIGHT())
        self.window: sg.PySimpleGUI.Window = self.make_window(caption, model_gui_elements, screen_pixel_shape)

        pg.init()
        # Everything is drawn to static.SCREEN
        static.SCREEN = pg.display.set_mode(screen_pixel_shape)
        utils.SCREEN_RECT = static.SCREEN.get_rect()
        # print(utils.SCREEN_RECT)

    def draw(self):
        # Fill the screen with the background color, then: draw patches, draw turtles on top, update the display.
        static.SCREEN.fill(self.screen_color)
        static.WORLD.draw( )
        pg.display.update( )

    def make_window(self, caption, model_gui_elements, screen_pixel_shape):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        lower_left_pixel = (static.SCREEN_PIXEL_HEIGHT() - 1, 0)
        upper_right_pixel = (0, static.SCREEN_PIXEL_WIDTH() - 1)
        # print(screen_pixel_shape, lower_left_pixel, upper_right_pixel)
        col = \
            [   # sg.Graph(SHAPE, lower-left, upper-right,
                # [sg.Graph(screen_pixel_shape, lower_left_pixel, upper_right_pixel,
                #           background_color='black', key='-GRAPH-')],

                *model_gui_elements,

                [sg.Button(self.SETUP, pad=((0, 10), (50, 0))),
                 sg.Button(self.GO_ONCE, pad=((0, 10), (50, 0))),
                 sg.Button(self.GO, pad=((0, 0), (50, 0)))],

                 # [sg.Text(self.FPS, pad=((0, 0), (50, 0)), tooltip='Frames per second'),
                 # sg.Combo(key=self.FPS, values=[5, 10, 25, 50, 100], pad=((0, 0), (50, 0)), default_value=50,
                 #          background_color='skyblue',
                 #          tooltip='Frames per second')],
                 #
                 [sg.Button(self.STOP, button_color=('white', 'darkblue'), pad=((0, 10), (20, 0))),
                  sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT, pad=((0, 30), (20, 0)))],

            ]
        layout = [[sg.Graph(screen_pixel_shape, lower_left_pixel, upper_right_pixel,
                            background_color='black', key='-GRAPH-'), sg.Column(col)]]
        window: sg.PySimpleGUI.Window = sg.Window(caption, layout, finalize=True, return_keyboard_events=True)
        # print(type(window))
        graph: sg.PySimpleGUI.Graph = window['-GRAPH-']
        # print(type(graph))
        # -------------- Magic code to integrate PyGame with tkinter -------
        embed: tk.Canvas = graph.TKCanvas
        # print(type(embed))
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        return window
