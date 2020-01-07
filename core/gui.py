
import os

import pygame as pg
from pygame.time import Clock

# By import this file itself, can avoid the use of globals
import PyLogo.core.gui as gui

import PySimpleGUI as sg

import tkinter as tk


# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
PATCH_SIZE = 10


def BLOCK_SPACING():
    return PATCH_SIZE + 1


PATCH_ROWS = 51
PATCH_COLS = 51


def SCREEN_PIXEL_WIDTH():
    return PATCH_COLS * BLOCK_SPACING() + 1


def SCREEN_PIXEL_HEIGHT():
    return PATCH_ROWS * BLOCK_SPACING() + 1


simple_gui = None


class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=15):
        # global simple_gui
        gui.simple_gui = self

        # global PATCH_SIZE
        gui.PATCH_SIZE = patch_size

        self.EXIT = 'Exit'
        self.GO = 'go'
        self.GO_ONCE = 'go once'
        self.GOSTOP = 'GoStop'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.clock = Clock()
        self.fps = 60
        self.idle_fps = 10

        self.screen_color = pg.Color(sg.RGB(50, 60, 60))

        self.caption = caption
        self.model_gui_elements = model_gui_elements

        screen_pixel_shape = (SCREEN_PIXEL_WIDTH(), SCREEN_PIXEL_HEIGHT())
        self.window: sg.PySimpleGUI.Window = self.make_window(caption, model_gui_elements, screen_pixel_shape)

        pg.init()
        # Everything is drawn to self.SCREEN
        self.SCREEN = pg.display.set_mode(screen_pixel_shape)

    def draw(self, element):
        # Fill the screen with the background color, draw the element, and update the display.
        self.SCREEN.fill(self.screen_color)
        element.draw( )
        pg.display.update( )

    def make_window(self, caption, model_gui_elements, screen_pixel_shape):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        lower_left_pixel = (SCREEN_PIXEL_HEIGHT() - 1, 0)
        upper_right_pixel = (0, SCREEN_PIXEL_WIDTH() - 1)
        col1 = [ *model_gui_elements,

                 [sg.Text('_' * 25)],

                 [sg.Button(self.SETUP, pad=((0, 10), (10, 0))),
                  sg.Button(self.GO_ONCE, disabled=True, button_color=('white', 'green'), pad=((0, 10), (10, 0))),
                  sg.Button(self.GO, disabled=True, button_color=('white', 'green'), pad=((0, 0), (10, 0)),
                            key=self.GOSTOP)],

                 [sg.Text('_' * 25)],

                 [sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT, pad=((70, 0), (10, 0)))] ]

        col2 = [[sg.Graph(screen_pixel_shape, lower_left_pixel, upper_right_pixel,
                          background_color='black', key='-GRAPH-')]]

        layout = [[sg.Column(col1), sg.Column(col2)]]
        window: sg.PySimpleGUI.Window = sg.Window(caption, layout, margins=(5, 20),
                                                  return_keyboard_events=True, finalize=True)
        graph: sg.PySimpleGUI.Graph = window['-GRAPH-']

        # -------------- Magic code to integrate PyGame with tkinter -------
        embed: tk.Canvas = graph.TKCanvas
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        return window
