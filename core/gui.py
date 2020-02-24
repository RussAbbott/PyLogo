
import os

import pygame as pg
from pygame.color import Color
from pygame.draw import line
from pygame.font import SysFont
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

# By importing this file itself, can avoid the use of globals
# noinspection PyUnresolvedReferences
import core.gui as gui

import PySimpleGUI as sg

from typing import Optional, Tuple, Union

import tkinter as tk


# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
# PATCH_SIZE should be odd so that there is a center pixel: (HALF_PATCH_SIZE(), HALF_PATCH_SIZE()).
# Assumes that the upper left corner is at (relative) (0, 0).
# If PATCH_SIZE == 3, then HALF_PATCH_SIZE() == 3//2 == 1, and center pixel == (1, 1)
PATCH_SIZE = 11


# BOARD_SHAPE is the shape of the board
PATCH_ROWS = 51
PATCH_COLS = 51



def BLOCK_SPACING():
    return PATCH_SIZE + 1


def HALF_PATCH_SIZE():
    return PATCH_SIZE//2



def HOR_SEP(length=25, pad=((0, 0), (10, 10))):
    return [sg.Text('_' * length, text_color='black', pad=pad)]



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


def gui_set(key, **kwargs):
    widget = WINDOW[key]
    widget.update(**kwargs)


def set_fps(val):
    # Select the value in FPS_VALUES closest to val.
    new_val = min(FPS_VALUES, key=lambda v: abs(v - val))
    # WINDOW['fps'].update(value=new_val)
    gui_set('fps', value=new_val)


# The WINDOW variable will be available to refer to the WINDOW object from elsewhere in the code.
# Neither the WINDOW nor the SCREEN can be imported directly because imports occur before they are created.
WINDOW: sg.PySimpleGUI.Window


# The following are from pygame.
SCREEN: Surface
FONT: SysFont


# These pygame functions draw to the SCREEN, which is a pygame Surface.
def blit(image: Surface, rect: Union[Rect, Tuple]):
    gui.SCREEN.blit(image, rect)


def draw_line(start_pixel, end_pixel, line_color: Color = Color('white'), width: int = 1):
    line(gui.SCREEN, line_color, start_pixel, end_pixel, width)


class SimpleGUI:

    def __init__(self, gui_left_upper, gui_right_upper=None, caption="Basic Model",
                 patch_size=15, board_rows_cols=(51, 51), bounce=None, fps=None):

        gui.PATCH_SIZE = patch_size if patch_size % 2 == 1 else patch_size + 1
        gui.PATCH_ROWS = board_rows_cols[0] if board_rows_cols[0] % 2 == 1 else board_rows_cols[0] + 1
        gui.PATCH_COLS = board_rows_cols[1] if board_rows_cols[1] % 2 == 1 else board_rows_cols[1] + 1

        self.EXIT = 'Exit'
        self.GO = 'go'
        self.GO_ONCE = 'go once'
        self.GOSTOP = 'GoStop'
        self.GRAPH = '-GRAPH-'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.clock = pg.time.Clock()
        self.fps = 60
        self.idle_fps = 10

        self.screen_color = pg.Color(sg.RGB(50, 60, 60))

        self.caption = caption

        self.screen_shape_width_height = (SCREEN_PIXEL_WIDTH(), SCREEN_PIXEL_HEIGHT())

        # All these gui.<variable> elements are globals in this file.
        gui.WINDOW = self.make_window(caption, gui_left_upper, gui_right_upper=gui_right_upper, bounce=bounce, fps=fps)

        pg.init()
        gui.FONT = SysFont(None, int(1.5 * gui.BLOCK_SPACING()))

        # All graphics are drawn to gui.SCREEN, which is a global variable.
        gui.SCREEN = pg.display.set_mode(self.screen_shape_width_height)

    def fill_screen(self):
        gui.SCREEN.fill(self.screen_color)

    def make_window(self, caption, gui_left_upper, gui_right_upper=None, bounce=True, fps=None):
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


        exit_button_line = [sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT, pad=((0, 0), (10, 0))),
                            sg.Checkbox('Grab anywhere', key='Grab', default=False, pad=((40, 0), (10, 0)))]

        col1 = [ *gui_left_upper,
                 gui.HOR_SEP(),
                 setup_go_line,
                 bounce_checkbox_line,
                 fps_combo_line,
                 gui.HOR_SEP(),
                 exit_button_line
                 ]

        lower_left_pixel_xy = (0, self.screen_shape_width_height[1]-1)
        upper_right_pixel_xy = (self.screen_shape_width_height[0]-1, 0)

        if gui_right_upper is None:
            gui_right_upper = [[]]

        # graph is a drawing area, a screen on which the model is portrayed, i.e., the patches and the agents.
        # It consists mainly of a TKCanvas.
        graph = sg.Graph(self.screen_shape_width_height, lower_left_pixel_xy, upper_right_pixel_xy,
                         background_color='black', key='-GRAPH-', enable_events=True)
        col2 = gui_right_upper + [[graph]]

        # layout is the actual layout of the window. The stuff above organizes it into component parts.
        # col1 is the control buttons, sliders, etc.
        # col2 is the graph plus whatever the user wants to put above it.
        # layout is a single "GUI line" with these two components in sequence.
        layout = [[sg.Column(col1), sg.Column(col2)]]

        # window is a window with that layout.
        window = sg.Window(caption, layout, margins=(5, 20), use_default_focus=False, grab_anywhere=False,
                           return_keyboard_events=True, finalize=True)

        # -------------- Magic code to integrate PyGame with tkinter -------
        w_id = graph.TKCanvas.winfo_id( )
        os.environ['SDL_WINDOWID'] = str(w_id)
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

        return window
