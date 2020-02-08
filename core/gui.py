
# This file contains code that implements the GUI.

import os

import pygame as pg
from pygame.time import Clock

# By importing this file itself, can avoid the use of globals
# noinspection PyUnresolvedReferences
import core.gui as gui

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


FPS_VALUES = values = [1, 3, 6, 10, 15, 25, 40, 60]


def set_fps(val):
    # Select the value in FPS_VALUES closest to val.
    new_val = min([(abs(v - val),  v) for v in FPS_VALUES])[1]
    WINDOW['fps'].update(new_val)


# This variable will be available to refer to the SCREEN object from elsewhere in the code.
# Note that it can't be imported directly because imports occur before the SCREEN is created.
SCREEN = None
WINDOW = None


class SimpleGUI:

    def __init__(self, model_gui_elements, caption="Basic Model", patch_size=15, bounce=None, fps=None):

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
        gui.WINDOW = self.make_window(caption, model_gui_elements, screen_shape_width_height, bounce=bounce, fps=fps)

        pg.init()

        # All graphics are drawn to gui.SCREEN, which is a global variable.
        gui.SCREEN = pg.display.set_mode(screen_shape_width_height)

    def fill_screen(self):
        SCREEN.fill(self.screen_color)

    def make_window(self, caption, model_gui_elements, screen_shape_width_height, bounce=True, fps=None):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        bounce_checkbox_line = ''
        if bounce is not None:
            bounce_checkbox_line = [sg.Checkbox('Bounce?', key='Bounce?', default=bounce,
                                    tooltip='Bounce back from the edges of the screen?')]

        fps_combo_line = ''
        if fps:
            fps_combo_line = [sg.Text('Frames/second', tooltip='The maximum frames/second.', pad=((0, 10), (10, 0))),
                              sg.Combo(key='fps', values=FPS_VALUES,
                                       background_color='limegreen', default_value=fps,
                                       tooltip='The maximum frames/second.', pad=((0, 0), (10, 0)))
                              ]

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

        # layout is the actual layout of the window. The stuff above organizes it into component parts.
        # col1 is the control buttons, sliders, etc.
        # col2 is the screen on which the model is portrayed, i.e., the patches and the agents.
        # layout is a single "GUI line" with these two components in sequence.
        layout = [[sg.Column(col1), sg.Column(col2)]]

        window: sg.PySimpleGUI.Window = sg.Window(caption, layout, margins=(5, 20),
                                                  use_default_focus=False,
                                                  return_keyboard_events=True, finalize=True)
        graph: sg.PySimpleGUI.Graph = window['-GRAPH-']

        # -------------- Magic code to integrate PyGame with tkinter -------
        embed: tk.Canvas = graph.TKCanvas
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        # Read the window to make the widgets show up.
        # window.read(timeout=10)

        return window
