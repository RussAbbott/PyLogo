
import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from copy import copy

from random import choice

from typing import List


class CA_World(OnOffWorld):

    ca_display_size = 151
    # bin_0_to_7 is ['000' .. '111']
    bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.pos_to_switch is a dictionary that maps positions in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py

        self.pos_to_switch = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        # print(self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        # You might also try rule 165.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()
        self.init = None

        self.ca_lines: List[List[int]] = []
        gui.WINDOW['rows'].update(value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial row
        """
        self.init = SimEngine.get_gui_value('init')
        if self.init == 'Random':
            # Set the initial row to random 1/0
            line = ...
        else:
            line = [0] * self.ca_display_size
            col = 0 if self.init == 'Left' else \
                  CA_World.ca_display_size // 2 if self.init == 'Center' else \
                  CA_World.ca_display_size - 1  # self.init == 'Right'
            line[col] = 1
        return line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        ...

    def handle_event_and_values(self):
        """
        This is called when a GUI widget is changed and isn't handled by the system.
        The key of the widget that changed is in SimEngine.event.
        If the changed widget has to do with the rule number or switches, make them all consistent.

        This is the function that will trigger all the code you write this week
        """
        if SimEngine.event in ...:
            ...

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all contain self.rule_nbr.
        """
        ...

    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string'].

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
        """
        ...

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches.
        """
        ...

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.

        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value).
        (new_value will be either True or False, i.e., 1 or 0.)

        This is the inverse of get_rule_nbr_from_switches().
        """
        ...

    def setup(self):
        """
        Make the slider, the switches, and the bin_string of the rule number consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are both different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are consistent,
        set self.ca__lines[0] as directed by SimEngine.get_gui_value('init').

        Copy (the setting on) that line to the bottom row of patches.
        """
        ...

    def step(self):
        """
        Take one step in the simulation.
        o Generate an additional line in self.ca_lines.
        o Copy self.ca_lines to the display
        """
        ...


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Right', 'Center', 'Left', 'Random'], key='init', default_value='Right')],
                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],
                 HOR_SEP(30)] + \
                 on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps positions in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
switches = [sg.CB(n+'\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True) for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switch settings.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((100, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal',
                             enable_events=True, pad=((10, 20), (0, 10))),
                   sg.Text('00000000 (binary)', key='bin_string', enable_events=True, pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
