
from __future__ import annotations

import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from copy import copy

from itertools import chain, repeat

from random import choice

from typing import List


class CA_World(OnOffWorld):

    ca_display_size = 151

    # bin_0_to_7 is ['000' .. '111']
    bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.pos_to_switch is a dictionary that maps position values in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py

        # The following two lines do the same thing. Explain how both work.
        pos_to_switch_a = {2**i: bin_str(i, 3) for i in range(8)}
        pos_to_switch_b = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        assert pos_to_switch_a == pos_to_switch_b
        self.pos_to_switch = ...  # pos_to_switch_a or pos_to_switch_b

        # The rule number used for this run, initially set to 110 as the default rule.
        # (You might also try rule 165.)
        # The following sets the local variable self.rule_nbr. It doesn't change the 'Rule_nbr' slider widget.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()

        # self.ca_lines is a list of lines, each of which is a list of 0/1. Each line represents
        # a state of the CA, i.e., all the cells in the line. self.ca_list contains the entire
        # history of the CA.
        self.ca_lines: List[List[int]] = []
        # gui.WINDOW['rows'].update(value=len(self.ca_lines))
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line
        """
        init = SimEngine.gui_get('init')
        if init == 'Random':
            # Set the initial row to random 1/0.
            # You complete this line.
            line = ...
        else:
            line_length = self.ca_display_size if SimEngine.gui_get('000') else 1
            line = [0] * line_length
            col = 0                if init == 'Left' else \
                  line_length // 2 if init == 'Center' else \
                  line_length - 1   # init == 'Right'
            line[col] = 1
        return line

    @staticmethod
    def drop_extraneous_0s_from_ends_of_new_line(new_line):
        """
        Drop the end cell at each end of new_line if it is 0. Keep it otherwise.
        Return the result.
        Args:
            new_line: ca_state with perhaps extraneous 0 cells at the ends

        Returns: trimmed ca_state without extraneous 0 cells at the ends.
        """
        ...

    def extend_ca_lines_if_needed(self, new_line):
        """
        new_line is one cell longer at each then than ca_lines[-1]. If those extra
        cells are 0, delete them. If they are 1, insert a 0 cell at the corresponding
        end of each line in ca_lines
        """
        ...

    @staticmethod
    def generate_new_line_from_current_line(prev_line):
        """
        The argument is (a copy of) the current line, i.e., copy(self.ca_lines[-1]).
        We call it prev_line because that's the role it plays in this method.
        Generate the new line in these steps.
        1. Add 0 to both ends of prev_line. (We do that because we want to allow the
        new line to extend the current line on either end. So start with a default extension.
        2. Insert an additional 0 at each end of prev_line. That's because we need a triple
        to generate the cells at the end of the new line. So, by this time the original
        line has been extended by [0, 0] on both ends.
        3. Apply the rules (i.e., the switches) to the result of step 2. This produces a line
        which is one cell shorter than the current prev_line on each end. That is, it is
        one cell longer on each end than the original prev_line.
        4. Return that newly generated line. It may have 0 or 1 at each end.
        Args:
            prev_line: The current state of the CA.
        Returns: The next state of the CA.
        """
        ...
        return new_line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        ...

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and isn't handled by the system.
        The key of the widget that changed is in event.
        If the changed widget has to do with the rule number or switches, make them all consistent.

        This is the function that will trigger all the code you write this week
        """
        # Handle color change requests.
        super().handle_event(event)

        if event in ['Rule_nbr'] + CA_World.bin_0_to_7:
            self.make_switches_and_rule_nbr_consistent()

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all should contain self.rule_nbr.
        """
        ...

    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string']. Include
        the parentheses around the binary number.

        Use SimEngine.gui_set('bin_string', value=new_value) to update the value of the widget.
        """
        ...

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches. There are two issues.
        1. Are the ca_lines longer/shorter than the Patch rows?
        2. Are there more/fewer lines than Patch row?
        What do you do in each case?

        This is the most difficult method. Here is the outline I used.
        """
        # Check to see if the user changed this value.
        init = SimEngine.gui_get('init')

        # Get the two relevant widths.
        display_width = gui.PATCH_COLS
        ca_line_width = len(self.ca_lines[0])

        # How many blanks must be prepended to the line to be displayed to fill the display row?
        # Will be 0 if the ca_line is at least as long as the display row or the line is left-justified.
        left_padding_needed = 0 if ca_line_width >= display_width or init == 'Left' else ...

        # Use [0]*n to get a sequence of n 0s.
        left_padding = ...

        # Which elements of the ca_line to be displayed?
        # More to the point, what is index of the first element of the line to be displayed?
        # Will be 0 if the display width is greater than or equal to the line width or we are left-justifying.
        left_ca_line_index = 0 if display_width >= ca_line_width or init == 'Left' else ...

        # Get the two relevant heights.
        display_height = gui.PATCH_ROWS
        nbr_ca_lines = len(self.ca_lines)

        # Which is the first line from self.ca_lines to display.
        # Will be 0 if display_height >= nbr_ca_lines
        first_ca_line_to_display = 0 if display_height >= nbr_ca_lines else ...

        # On which Patch row, do we start displaying lines from ca_lines?
        # Will be 0 if nbr_ca_lines >= display_height
        first_patches_row_nbr = 0 if nbr_ca_lines >= display_height else ...

        # We now have all the relevant values for deciding how to paint the ca_lines onto the Patch display.
        ca_lines_to_display = ...

        # This is a slice from CA_World.patches_array
        patch_rows_to_display_on = CA_World.patches_array[...]

        # Zip the ca_lines to be displayed together with the Patch rows where they are to be displayed.
        ca_lines_patch_rows = zip(ca_lines_to_display, patch_rows_to_display_on)

        # Step through the corresponding pairs.
        for (ca_line, patch_row) in ca_lines_patch_rows:

            # Which elements from ca_lines[ca_line] should be displayed?
            # We display the elements starting at left_ca_line_index.
            ca_line_portion = ...

            # For the complete display line, we may need to pad ca_line_portion to the left or right.
            # We need left_padding_needed 0s to the left and an arbitrary sequence of 0s to the right.
            # (Use repeat from itertools for the padding on the right. It doesn't matter if it's too long!)

            # Put the three pieces together to get the full line.
            # Use chain from itertools to combine the three parts of the line:
            #       left_padding, ca_line_portion, right_padding.
            padded_line = chain(..., ..., ...)

            # Where will the padded_line be displayed? On patch_row.

            # Zip the values from the padded_line with the Patches that will display them.
            # (The second parameter to zip, i.e., the Patches, limits the number of values to be displayed.
            # That's why it doesn't matter if the first parameter is too long.)
            ca_values_patchs = zip(padded_line, patch_row)

            # Step through these value-patch pairs and put the values into the associated Patches.
            for (ca_val, patch) in ca_values_patchs:
                # Use the set_on_off method of OnOffPatch to set the patch to ca_val.
                ...

        # Update the 'rows' widget.
        ...

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.

        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value).
        Set that switch as follows: SimEngine.gui_set(self.pos_to_switch[pos], value=new_value).
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
        set self.ca_lines[0] as directed by SimEngine.gui_get('init').

        Copy (the settings on) that line to the bottom row of patches.
        Note that the lists in self.ca_lines are lists of 0/1. They are not lists of Patches.
        """
        ...

    def step(self):
        """
        Take one step in the simulation.
        (a) Generate an additional line for the ca. (Use a copy of self.ca_lines[-1].)
        (b) Extend all lines in ca_lines if the new line is longer than its predecessor.
        (c) Trim the new line and add to self.ca_lines
        (d) Copy self.ca_lines to the display
        """
        # (a)
        new_line = ... # The new state derived from self.ca_lines[-1]

        # (b)
        ... # Extend lines in self.ca_lines at each end as needed.

        # (c)
        trimmed_new_line = ... # Drop extraneous 0s at the end of new_line
        ... # Add trimmed_new_line to the end of self.ca_lines

        # (d)
        ... # Refresh the display from self.ca_lines


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Left', 'Center', 'Right', 'Random'], key='init', default_value='Right')],
                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],
                 HOR_SEP(30)] + \
                 on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True) for n in reversed(CA_World.bin_0_to_7)]

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

    # Note that we are using OnOffPatch as the Patch class. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
