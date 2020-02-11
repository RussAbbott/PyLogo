
import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from random import choice


class CA_World(OnOffWorld):

    ca_left_extension_length = 0
    ca_display_size = 225

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.pos_to_switch is a dictionary that maps positions in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py
        self.pos_to_switch = {2**i: bin_str(i, 3) for i in range(8)}
        # print(self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        # You might also try rule 165.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr(self.rule_nbr)
        self.set_binary_nbr_from_rule_nbr(self.rule_nbr)

        self.ca_list = [0] * CA_World.ca_display_size
        self.rows = 0

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        ...

    def pad_ca_list_ends_with_0s(self):
        """
        If either end of self.ca_list is 1, tack 0 onto that end (perhaps both).
        Also return the prev_list derived from that list
        """
        ...

    def propagate_ca_list_to_bottom_row(self):
        """
        Find and set on/off the values of all cells in this row (except the end cells)
        implied by the previous row and the current rule.
        o Use get_patch_on_off(patch) to find the value for each patch.
        o Use patch.set_on_off() to set patch to on or off. (patch.set_on_off() is defined in on_off.py.)
        """
        ca_prev_list = self.pad_ca_list_ends_with_0s()
        # At this point:
        # self.ca_prev_list: 0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0
        # self.ca_list:       0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0
        # self.ca_list[i] depends on self.ca_prev_list[i:i+3].
        # That's because self.ca_prev_list[0] is one to the left of self.ca_list[0]

        # Update the elements of self.ca_list according to self.ca_prev_list and the current rule.

        # If self.ca_list[i] corresponds to a patch, update the patch also.

        ...

    @staticmethod
    def set_binary_nbr_from_rule_nbr(rule_nbr):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string'].

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
        """
        ...

    def set_switches_from_rule_nbr(self, rule_nbr):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i].

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
        set self.ca_list as directed by SimEngine.get_gui_value('init').

        Copy those values to the bottom row of patches.
        (The bottom row is row gui.PATCH_ROWS - 1.)

        Increment self.rows
        """
        ...

    def step(self):
        """
        Take one step in the simulation.
        o Copy all cell/patch on/off settings to the row above it.
        o Set the bottom row of cells/patches as directed by the row above it.
        Do this by updating self.ca_list and then copying it to the bottom row of patches.
        use self.propagate_ca_list_to_bottom_row() for this step

        Increment self.rows
        """
        ...


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Right', 'Center', 'Left', 'Random', 'All off'], key='init', default_value='Right')],
                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],
                 HOR_SEP(30)] + \
                 on_off_left_upper


# bin_0_to_7 is ['000' .. '111']
bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

# The switches are CheckBoxes with keys from bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access through their keys.
# The pos_to_switch dictionary maps positions in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
switches = [sg.CB(n+'\n 1', key=n, pad=((60, 0), (0, 0))) for n in reversed(bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switch settings.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((250, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal', pad=((10, 20), (0, 10))),
                   sg.Text('00000000 (binary)', key='bin_string', pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch. We could define a CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
