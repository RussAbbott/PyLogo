
import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from random import choice


class CA_Patch(OnOffPatch):

    def __init__(self, *args, **kw_args):
        super().__init__(*args, **kw_args)
        self.is_on = False


class CA_World(OnOffWorld):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.pos_to_switch is a dictionary that maps positions in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        self.pos_to_switch = {2**i: bin_str(i, 3) for i in range(8)}
        # print(self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        self.rule_nbr = 110
        self.set_switches_from_rule_nbr(self.rule_nbr)
        self.set_binary_nbr_from_rule_nbr(self.rule_nbr)

    @staticmethod
    def fill_row_randomly(row_nbr):
        """
        Fill row row_nbr of CAs with random on/off.
        This implementation doesn't wrap around the way NetLogo does. The two end cells of
        every row are always off.
        Note the use of a slice to pick out the cells in row row_nbr other than the end cells.
        gui.PATCH_COLS is the number of columns of patches. So the end cells are 0 and gui.PATCH_COLS-1
        """
        for patch in CA_World.patches_array[row_nbr, 1:gui.PATCH_COLS-1]:
            ...

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        """
        ...

    @staticmethod
    def get_patch_on_off(patch):
        """
        Find and return the value of this cell implied by the associated three cells in the preceding row
        according to the current rule. All on/off values are booleans: on == True; off == False.
        """
        ...

    def propagate_to_row(self, row_nbr):
        """
        Find and set on/off the values of all cells in this row (except the end cells)
        implied by the previous row and the current rule.
        """
        ...

    @staticmethod
    def set_binary_nbr_from_rule_nbr(rule_nbr):
        """
        Translate the rule number (self.rule_nbr) into a binary string and put it into
        the gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string'].

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
        """
        ...

    def set_switches_from_rule_nbr(self, rule_nbr):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i].
        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value)
        """
        ...

    def setup(self):
        """
        Make the slider and switches consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are
        consistent, set the initial row (the borrom row) of patches as directed
        by SimEngine.get_gui_value('init') (The bottom row is row gui.PATCH_ROWS - 1.)
        """
        ...

    def step(self):
        """
        Take one step in the simulation.
        o copy all patch on/off settings to the row above it.
        o set the bottom row as directed by the row above it.
        """
        ...


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
This appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Random', 'Left', 'Center', 'Right', 'None'], key='init', default_value='Right')],
                 HOR_SEP(30)] + \
                 on_off_left_upper


# bin_7_to_0 is ['111' .. '000']
bin_7_to_0 = [bin_str(n, 3) for n in range(7, -1, -1)]

# switches are CheckBoxes from '111' to '000'
switches = [sg.CB(n+'\n 1', key=n, pad=((30, 0), (0, 0))) for n in bin_7_to_0]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switch settings.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((120, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal', pad=((10, 20), (0, 10))),
                   sg.Text('(00000000)', key='bin_string', pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo
    PyLogo(CA_World, '1D CA',
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           patch_class=CA_Patch, fps=10, patch_size=5, board_rows_cols=(150, 150))
