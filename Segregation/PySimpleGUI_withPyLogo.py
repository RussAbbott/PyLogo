from os import environ
import pygame
from pygame import Color
from pygame.time import Clock
import PySimpleGUI as psg
from random import randint

"""
    Demo of integrating PyGame with PySimpleGUI.
    A similar technique may be possible with WxPython.
    To make it work on Linux, set SDL_VIDEODRIVER as
    specified in http://www.pygame.org/docs/ref/display.html, in the
    pygame.display.init() section.
"""
# --------------------- PySimpleGUI window layout and creation --------------------
change = 'Change'
move = 'Move'
layout = [[psg.Text('Test of PySimpleGUI with PyGame')],
          [psg.Graph((818, 816), (0, 0), (818, 816), background_color='black', key='-GRAPH-')],
          [psg.Button(change), psg.Button(move), psg.Exit()]]

window = psg.Window('PySimpleGUI + PyGame', layout, finalize=True)
graph = window['-GRAPH-']

# -------------- Magic code to integrate PyGame with tkinter -------
embed = graph.TKCanvas
environ['SDL_WINDOWID'] = str(embed.winfo_id())
environ['SDL_VIDEODRIVER'] = 'windib'  # change this to 'x11' to make it work on Linux

# ----------------------------- PyGame Code -----------------------------

from SimpleModels import main
main()

#
# screen = pygame.display.set_mode((500, 500))
#
# pygame.init()
# # pygame.display.update()
#
# (x, y, radius) = (250, 250, 100)
# # color = (255, 255, 255)
# color = Color('indianred')
# clock = Clock()
# while True:
#     (event, values) = window.read(timeout=10)
#     # if event != "__TIMEOUT__" or values != {"-GRAPH-": (None, None)}:
#     #     print(event, f'{"" if values == {"-GRAPH-": (None, None)} else values}')
#     if event in (None, 'Exit'):
#         window.close()
#         break
#     elif event == change:
#         radius = (radius + 10) % 150 + 10
#     elif event == move:
#         for _ in range(20):
#             (x, y) = (x + randint(-10, 10), y + randint(-10, 10))
#             screen.fill(Color('lightblue'))
#             pygame.draw.circle(screen, color, (x, y), radius)
#             pygame.display.update()
#             clock.tick(3)
#     screen.fill(Color('lightblue'))
#     pygame.draw.circle(screen, color, (x, y), radius)
#     pygame.display.update()


# window.close()
