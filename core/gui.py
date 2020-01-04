
import PyLogo.core.static_values as static

import os

import PySimpleGUI as sg

"""
    Demo of integrating PyGame with PySimpleGUI.
    A similar technique may be possible with WxPython.
    To make it work on Linux, set SDL_VIDEODRIVER as
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""


def make_window(sim_engine, caption, model_gui_elements):
    """
    Create the window, including sg.Graph, the drawing surface.
    """
    # --------------------- PySimpleGUI window layout and creation --------------------
    sim_engine.lower_left_pixel = (static.SCREEN_PIXEL_HEIGHT - 1, 0)
    sim_engine.upper_right_pixel = (0, static.SCREEN_PIXEL_WIDTH - 1)
    sim_engine.screen_pixel_shape = (static.SCREEN_PIXEL_WIDTH, static.SCREEN_PIXEL_HEIGHT)
    layout = \
        [   # sg.Graph(SHAPE, lower-left, upper-right,
            [sg.Graph(sim_engine.screen_pixel_shape, sim_engine.lower_left_pixel, sim_engine.upper_right_pixel,
                      background_color='black', key='-GRAPH-')],

            model_gui_elements,

            [sg.Button(sim_engine.SETUP), sg.Button(sim_engine.GO_ONCE),
             sg.Button(sim_engine.GO, pad=((0, 50), (0, 0))),

             sg.Button(sim_engine.STOP, button_color=('white', 'darkblue')),
             sg.Exit(button_color=('white', 'firebrick4'), key=sim_engine.EXIT),

             sg.Text(sim_engine.FPS, pad=((100, 10), (0, 0)), tooltip='Frames per second'),
             sg.Slider(key=sim_engine.FPS, range=(1, 100), orientation='horizontal', tooltip='Frames per second',
                       default_value=sim_engine.default_fps, pad=((0, 0), (0, 20)))]
    ]
    window = sg.Window(caption, layout, finalize=True, grab_anywhere=True, return_keyboard_events=True)
    graph = window['-GRAPH-']
    # -------------- Magic code to integrate PyGame with tkinter -------
    embed = graph.TKCanvas
    os.environ['SDL_WINDOWID'] = str(embed.winfo_id( ))
    os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

    return window