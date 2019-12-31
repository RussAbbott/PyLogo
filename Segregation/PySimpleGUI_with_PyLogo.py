from os import environ
import PySimpleGUI as psg
from SimpleModels import main

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

if __name__ == "__main__":
    main()
