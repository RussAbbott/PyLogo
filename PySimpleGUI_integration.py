import pygame
from pygame import Color
import PySimpleGUI as sg
import os

"""
    Demo of integrating PyGame with PySimpleGUI, the tkinter version
    A similar technique may be possible with WxPython
    To make it work on Linux, set SDL_VIDEODRIVER like
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""
# --------------------- PySimpleGUI window layout and creation --------------------
change = 'Change'
layout = [[sg.Text('Test of PySimpleGUI with PyGame')],
          [sg.Graph((500, 500), (0, 0), (500, 500),
                    background_color='black', key='-GRAPH-')],
          [sg.Button(change), sg.Exit()]]

window = sg.Window('PySimpleGUI + PyGame', layout, finalize=True)
graph = window['-GRAPH-']

# -------------- Magic code to integrate PyGame with tkinter -------
embed = graph.TKCanvas
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

# ----------------------------- PyGame Code -----------------------------

screen = pygame.display.set_mode((500, 500))

pygame.display.init()
pygame.display.update()

(x, y, radius) = (250, 250, 100)
color = (255, 255, 255)
while True:
    (event, values) = window.read(timeout=10)
    if event != "__TIMEOUT__" or values != {"-GRAPH-": (None, None)}:
        print(event, f'{"" if values == {"-GRAPH-": (None, None)} else values}')
    if event in (None, 'Exit'):
        window.close( )
        break
    elif event == change:
        radius = (radius+10) % 150 + 10
    screen.fill(Color('lightblue'))
    pygame.draw.circle(screen, color, (x, y), radius)
    pygame.display.update()

# window.close()
