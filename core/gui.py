
import os

import pygame as pg
from pygame.time import Clock

# By importing this file itself, can avoid the use of globals
# noinspection PyUnresolvedReferences
import PyLogo.core.gui as gui

import PySimpleGUI as sg

import tkinter as tk


# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
# PATCH_SIZE should be odd so that there is a center pixel: (HALF_PATCH_SIZE(), HALF_PATCH_SIZE()).
# Assumes that the upper left corner is at (relative) (0, 0).
# If PATCH_SIZE == 3, then HALF_PATCH_SIZE() == 3//2 == 1, and center pixel == (1, 1)
PATCH_SIZE = 11


def BLOCK_SPACING():
    return PATCH_SIZE + 1


def HALF_PATCH_SIZE():
    return PATCH_SIZE//2


PATCH_ROWS = 51
PATCH_COLS = 51


def HOR_SEP(length=25):
    return [sg.Text('_' * length, text_color='black')]



def SCREEN_PIXEL_WIDTH():
    """
    Includes pixel x coordinates range(SCREEN_PIXEL_WIDTH())
    """
    return PATCH_COLS * BLOCK_SPACING() + 1


def SCREEN_PIXEL_HEIGHT():
    """
    Includes pixel y coordinates range(SCREEN_PIXEL_HEIGHT())
    """
    return PATCH_ROWS * BLOCK_SPACING() + 1


simple_gui = None


class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=15, bounce=True, fps=None):
        gui.simple_gui = self

        gui.PATCH_SIZE = patch_size

        self.EXIT = 'Exit'
        self.GO = 'go'
        self.GO_ONCE = 'go once'
        self.GOSTOP = 'GoStop'
        self.GRAPH = '-GRAPH-'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.clock = Clock()
        self.fps = 60
        self.idle_fps = 10

        self.screen_color = pg.Color(sg.RGB(50, 60, 60))

        self.caption = caption
        self.model_gui_elements = model_gui_elements

        screen_shape_width_height = (SCREEN_PIXEL_WIDTH(), SCREEN_PIXEL_HEIGHT())
        self.window: sg.PySimpleGUI.Window = self.make_window(caption, model_gui_elements,
                                                              screen_shape_width_height,
                                                              bounce=bounce, fps=fps)

        pg.init()
        # Everything is drawn to self.SCREEN
        self.SCREEN = pg.display.set_mode(screen_shape_width_height)

    def fill_screen(self):
        self.SCREEN.fill(self.screen_color)

    def make_window(self, caption, model_gui_elements, screen_shape_width_height, bounce=True, fps=None):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        # hor_separator_line = [sg.Text('_' * 25, text_color='black')]

        bounce_checkbox_line = ''
        if bounce is not None:
            bounce_checkbox_line = [sg.Checkbox('Bounce?', key='Bounce?', default=bounce,
                                    tooltip='Bounce back from the edges of the screen?')]

        fps_combo_line = ''
        if fps:
            fps_combo_line = [sg.Text('Frames/second', tooltip='The maximum frames/second.', pad=((0, 10), (10, 0))),
                              sg.Combo(key='fps', values=[1, 3, 6, 10, 20, 40, 60],
                                 background_color='limegreen', default_value=fps,
                                 tooltip='The maximum frames/second.', pad=((0, 0), (10, 0)))]

        setup_go_line = [
            sg.Button(self.SETUP, pad=((0, 10), (10, 0))),
            sg.Button(self.GO_ONCE, disabled=True, button_color=('white', 'green'), pad=((0, 10), (10, 0))),
            sg.Button(self.GO, disabled=True, button_color=('white', 'green'), pad=((0, 30), (10, 0)),
                      key=self.GOSTOP)   ]


        exit_button_line = [sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT, pad=((70, 0), (10, 0)))]

        col1 = [ *model_gui_elements,
                 gui.HOR_SEP(),
                 setup_go_line,
                 bounce_checkbox_line,
                 fps_combo_line,
                 gui.HOR_SEP(),
                 exit_button_line
                 ]

        lower_left_pixel_xy = (0, screen_shape_width_height[1]-1)
        upper_right_pixel_xy = (screen_shape_width_height[0]-1, 0)
        col2 = [[sg.Graph(screen_shape_width_height, lower_left_pixel_xy, upper_right_pixel_xy,
                          background_color='black', key='-GRAPH-', enable_events=True)]]

        layout = [[sg.Column(col1), sg.Column(col2)]]
        window: sg.PySimpleGUI.Window = sg.Window(caption, layout, margins=(5, 20),
                                                  return_keyboard_events=True, finalize=True)
        graph: sg.PySimpleGUI.Graph = window['-GRAPH-']

        # -------------- Magic code to integrate PyGame with tkinter -------
        embed: tk.Canvas = graph.TKCanvas
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        return window
