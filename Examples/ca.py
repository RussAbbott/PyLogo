
from __future__ import annotations

from copy import copy
from itertools import chain, repeat
from random import choice

import numpy as np

import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import OnOffPatch, OnOffWorld, on_off_left_upper
from core.sim_engine import SimEngine
from core.utils import bin_str


class CA_World(OnOffWorld):

    ca_display_size = 225

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

        # self.pos_to_switch0 = {2**i: bin_str(i, 3) for i in range(8)}
        self.pos_to_switch = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        # print(self.pos_to_switch0 == self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        # (You might also try rule 165.)
        # The following sets the local variable self.rule_nbr. It doesn't change the 'Rule_nbr' slider widget.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()

        # self.ca_lines is a list of lines, each of which is a list or string of 0/1. Each line
        # representsa state of the CA, i.e., all the symbols in the line. self.ca_list contains
        # the entire history of the CA.
        self.lists = None
        self.padding_element = None
        self.ca_lines = []
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line.
        It is a random line if SimEngine.gui_get('Random?').
        It is a line (of length ca_display_size) of 0's if SimEngine.gui_get('init_line') == ''.
        Otherwise it is the string in SimEngine.gui_get('init_line') converted into 0's and 1's.
        (' ' and '0' are converted to 0; everything else is converted to 1.)
        However, if the rule includes 000 -> 1,pad the line with 0's on both ends to fill the display.
        How much to put on each end depends on the user-specific initial line and the requested justification.
        """
        if SimEngine.gui_get('Random?'):
            line = [choice([0, 1]) for _ in range(self.ca_display_size)] if self.lists else \
                   ''.join([choice(['0', '1']) for _ in range(self.ca_display_size)])
        else:
            padding = self.padding_element * (self.ca_display_size)
            if SimEngine.gui_get('init_line') == '':
                line = padding
            else:
                line_0 = SimEngine.gui_get('init_line')
                # Convert line_0 to 0's and 1's
                # Treat '0' and ' ' as "not on".
                line = [0 if c in ' 0' else 1 for c in line_0] if self.lists else \
                       ''.join(['0' if c in ' 0' else '1' for c in line_0])
                if SimEngine.gui_get('000'):
                    justification = SimEngine.gui_get('justification')
                    line_len = len(line)
                    actual_padding = padding[line_len:]
                    line = actual_padding + line if justification == 'Right' else \
                           line + actual_padding if justification == 'Left' else \
                           actual_padding[len(actual_padding)//2:] + line + actual_padding[len(actual_padding)//2:]
        return line

    # Used only for the list case
    @staticmethod
    def drop_extraneous_0s_from_ends_of_new_line(new_line):
        """
        Drop the end cell at each end of new_line if it is 0. Keep it otherwise.
        Return the result.
        Args:
            new_line: ca_state with perhaps extraneous 0 cells at the ends

        Returns: trimmed ca_state without extraneous 0 cells at the ends.
        """
        # Drop the 0's at the ends that are 0.
        if not new_line[0]:
            new_line.pop(0)
        if not new_line[-1]:
            new_line.pop(-1)
        return new_line

    # Used only for the list case
    def extend_ca_lines_if_needed(self, new_line):
        """
        new_line is one cell longer at each then than ca_lines[-1]. If those extra
        cells are 0, delete them. If they are 1, insert a 0 cell at the corresponding
        end of each line in ca_lines
        """
        # new_line is longer than the original line by one on each end.
        # Extend the other lines in self.ca_lines for the ends that are non-zero
        if new_line[0] or new_line[-1]:
            for line in self.ca_lines:
                if new_line[0]:
                    line.insert(0, 0)
                if new_line[-1]:
                    line.append(0)

    def generate_new_line_from_current_line(self, prev_line):
        """
        The argument is (a copy of) the current line. We call it prev_line because that's the role
        it plays in this method.

        Generate the new line in these steps.
        1. Add '00' or (0, 0) to both ends of prev_line. (We do that because we want to allow the
        new line to extend the current line on either end. So start with a default extension.
        In addition, we need a triple to generate the symbols at the end of the new line.)
        Strings are immutable; string concatenation (+) does not change the original strings.

        2. Apply the rules (i.e., the switches) to the triples extracted from the line resulting from step 1.

            a. Look up the truth value of each triple. Is its switch on or off?
            b. Convert that boolean first to an int (0 or 1) and then to a character ('0' or '1').
            These two steps are done in a single list comprehension. The result is new_line_chars: List[str].
            Each element of new_line_chars is a string of one character, either '0' or '1'.

            c. Use join to combine that list of characters into a new string.

        This produces a line which is one symbol shorter than the current prev_line on each end.
        That is, it is one symbol longer on each end than the original current line. It may have
        0 or 1 at each end.

        Args:
            prev_line: The current state of the CA.
        Returns: The next state of the CA.
        """
        # Extend the current line two to the left and right.
        # Want to be able to generate one additional value at each end.
        if self.lists:
            prev_line.insert(0, 0)
            prev_line.insert(0, 0)
            prev_line.extend([0, 0])
            triples = [''.join(map(str, prev_line[i:i + 3])) for i in range(len(prev_line) - 2)]
            new_line = [int(SimEngine.gui_get(triple)) for triple in triples]
        else:
            prev_line = '00' + prev_line + '00'

            # For each triple of characters in the prev_line, look up the setting of the corresponding switch.
            # (SimEngine.gui_get(prev_line[i:i + 3]))
            # Convert its Truth value (rule is on/off) to an int and then to a one character str.
            new_line_chars = [str(int(SimEngine.gui_get(prev_line[i:i + 3]))) for i in range(len(prev_line) - 2)]

            # Finally, join those strings together into a new string.
            new_line = ''.join(new_line_chars)
        return new_line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        rule_nbr = 0
        (_event, values) = gui.WINDOW.read(timeout=10)
        for (pos, key) in self.pos_to_switch.items():
            if values[key]:
                rule_nbr += pos
        return rule_nbr

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle color change requests.
        super().handle_event(event)

        # Handle rule nbr change events, either switches or rule_nbr slider
        if event in ['Rule_nbr'] + CA_World.bin_0_to_7:
            self.make_switches_and_rule_nbr_consistent()

        # When the user checks the 'Random?' box, the Input line area should disappear.
        # When the user unchecks the 'Random?' box, the Input line area should re-appear.
        elif event == 'Random?':
            disabled = SimEngine.gui_get('Random?')
            SimEngine.gui_set('init_line', visible=not disabled, value='1')

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all should contain self.rule_nbr.
        """
        new_switches_nbr = self.get_rule_nbr_from_switches()
        if self.rule_nbr != new_switches_nbr:
            self.rule_nbr = new_switches_nbr
        else:
            self.rule_nbr = SimEngine.gui_get('Rule_nbr')
            self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()

    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string']. Include
        the parentheses around the binary number.

        Use SimEngine.gui_set('bin_string', value=new_value) to update the value of the widget.
        """
        binary_rule_nbr = bin_str(self.rule_nbr, 8)
        SimEngine.gui_set('Rule_nbr', value=self.rule_nbr)
        new_bin_value = binary_rule_nbr + ' (binary)'
        SimEngine.gui_set('bin_string', value=new_bin_value)

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches. There are two issues.
        1. Is self.ca_lines longer/shorter than the number of Patch rows in the display?
        2. Are there more/fewer symbols-per-line than Patches-per-row?
        What do you do in each case?

        This is the most difficult method. Here is the outline I used.
        """
        # Get the current setting of 'justification'.
        justification = SimEngine.gui_get('justification')

        # Get the two relevant widths.
        display_width = gui.PATCH_COLS

        # All the lines in self.ca_lines are the same length.
        ca_line_width = len(self.ca_lines[0])

        # How many blanks must be prepended to a line to be displayed to fill a display row?
        # Will be 0 if the ca_line is at least as long as the display row or the line is left-justified.
        left_padding_needed = 0 if ca_line_width >= display_width or justification == 'Left' else \
                              (display_width - ca_line_width)//2  if justification == 'Center' else \
                              display_width - ca_line_width     # if justification == 'Right'

        # Use [0]*n to get a list of n 0s to use as left padding.
        left_padding = self.padding_element * left_padding_needed

        # Which symbols of the ca_line are to be displayed?
        # More to the point, what is index of the first symbol of the line to be displayed?
        # Will be 0 if left_padding is the empty list. Otherwise compute the values for the other cases.
        left_ca_line_index = 0 if display_width >= ca_line_width or justification == 'Left' else \
                             (ca_line_width - display_width)//2  if justification == 'Center' else \
                             ca_line_width - display_width     # if justification == 'Right'

        # Reverse both self.ca_lines and CA_World.patches_array.
        ca_lines_to_display = reversed(self.ca_lines)
        patch_rows_to_display_on = np.flip(CA_World.patches_array, axis=0)

        # Now we can use zip to match up ca_lines_to_display and patch_rows_to_display on.
        # In both cases we are starting at the bottom and working our way up.
        ca_lines_patch_rows = zip(ca_lines_to_display, patch_rows_to_display_on)

        # zip is given two iterables and produces a sequence of pairs of elements, one from each.
        # An important feature of zip is that it stops whenever either of its arguments ends.
        # In particular, the two arguments needn't be the same length. Zip simply uses all the elements
        # of the shorter argument and pairs them with the initial elements of the longer argument.

        # We can now step through the corresponding pairs.
        for (ca_line, patch_row) in ca_lines_patch_rows:
            # The values in ca_line are to be displayed on patch_row.
            # The issue now is how to align them.

            # Which symbols of ca_line should be displayed?
            # We display all the symbols starting at left_ca_line_index (computed above).
            # Use a slice to identify these symbols.
            ca_line_portion = ca_line[left_ca_line_index:]

            # For the complete display line and the desired justification,
            # we may need to pad ca_line_portion to the left or right (or both).
            # We need left_padding (computed above) to the left and an arbitrary sequence of 0's to the right.
            # (Use repeat() from itertools for the padding on the right. It doesn't matter if it's too long!)

            # Put the three pieces together to get the full line.
            # Use chain() from itertools to combine the three parts of the line:
            #                   left_padding, ca_line_portion, right_padding.
            padded_line = chain(left_padding, ca_line_portion, repeat('0'))

            # padded_line has the right number of 0's at the left. It then contains the symbols from ca_line
            # to be displayed. If we need more symbols to display, padded_line includes an unlimted number of
            # trailing 0's.

            # Since padded_line will be displayed on patch_row, we can use zip again to pair up the values
            # from padded_line with the Patches in patch_row. Since padded_line includes an unlimited number
            # of 0's at the end, zip will stop when it reaches the last Patch in patch_row.

            ca_values_patchs = zip(padded_line, patch_row)

            # Step through these value/patch pairs and put the values into the associated Patches.
            for (ca_val, patch) in ca_values_patchs:
                # Use the set_on_off() method of OnOffPatch to set the patch based on ca_val.
                patch.set_on_off(int(ca_val))

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.

        Set that switch as follows: SimEngine.gui_set(self.pos_to_switch[pos], value=new_value).
        (new_value will be either True or False, i.e., 1 or 0.)

        This is the inverse of get_rule_nbr_from_switches().
        """
        rule_nbr = self.rule_nbr
        for pos in self.pos_to_switch:
            SimEngine.gui_set(self.pos_to_switch[pos], value=rule_nbr % 2)
            rule_nbr = rule_nbr // 2

    def setup(self):
        """
        Make the slider, the switches, and the bin_string of the rule number consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are both different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are consistent,
        set self.ca_lines[0] to the line generated by build_initial_line.
        """
        self.lists = SimEngine.gui_get('lists_or_strings') == 'Lists'
        self.padding_element = [0] if self.lists else '0'

        self.make_switches_and_rule_nbr_consistent()

        for patch in CA_World.patches:
            patch.set_on_off(False)

        initial_line = self.build_initial_line()

        self.ca_lines = [initial_line]

        self.set_display_from_lines()

    def step(self):
        """
        Take one step in the simulation.
        (a) Generate an additional line for the ca. (Use a copy of self.ca_lines[-1].)
        (b) Extend all lines in ca_lines if the new line is longer (with additional 1's) than its predecessor.
        (c) Trim the new line and add it to the end of self.ca_lines.
        (d) Refresh display from values in self.ca_lines.
        """
        # (a)
        new_line: str = self.generate_new_line_from_current_line(copy(self.ca_lines[-1]))

        # (b)
        # Extend lines in self.ca_lines at each end as needed. (Don't extend for extra 0's at the ends.)
        if self.lists:
            self.extend_ca_lines_if_needed(new_line)
        else:  # Strings
            line_end = {'1': '0', '0': ''}
            # If either end is '1', add '0' to that end of all strings.
            # Can't drop the 0's first because we would lose track of which end was extended.
            if '1' in (new_line[0], new_line[-1]):
                # Use the line_end dictionary to look up values for left_end and right_end
                left_end = line_end[new_line[0]]
                right_end = line_end[new_line[-1]]
                self.ca_lines = [left_end + line + right_end for line in self.ca_lines]

        # (c)
        if self.lists:
            trimmed_new_line = self.drop_extraneous_0s_from_ends_of_new_line(new_line)
        else:  # Strings
            start = 0 if new_line[0] == '1' else 1
            end = len(new_line) if new_line[-1] == '1' else len(new_line) - 1
            trimmed_new_line: str = new_line[start:end]

        # Add trimmed_new_line to the end of self.ca_lines
        self.ca_lines.append(trimmed_new_line)

        # (d)
        # Refresh the display from self.ca_lines
        self.set_display_from_lines()
        # Update the 'rows' widget.
        SimEngine.gui_set('rows', value=len(self.ca_lines))


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
"""
ca_left_upper = [[sg.Text('Row justification'),
                  sg.Combo(values=['Left', 'Center', 'Right'], key='justification', default_value='Right')],

                 HOR_SEP(30),

                 [sg.Text('Initial row:', pad=(None, (20, 0)),
                          tooltip="0's and 1's for the initial row. An empty \n" +
                                  "string will set the initial row to all 0's."),
                  sg.Input(default_text="1", key='init_line', size=(20, 1), text_color='white',
                           background_color='steelblue4', justification='center')],

                 [sg.CB('Random?', key='Random?', enable_events=True, pad=((65, 0), None),
                        tooltip="Set the initial row to random 0's and 1's.")],

                 HOR_SEP(30, pad=(None, None)),

                 [sg.Text('Rows:', pad=(None, (10, 0))), sg.Text('     0', key='rows', pad=(None, (10, 0)))],

                 [sg.Text('Lists or Strings', pad=(None, None)),
                  sg.Combo(values=['Lists', 'Strings'], key='lists_or_strings', default_value='Lists')],

                 HOR_SEP(30, pad=(None, (0, 10)))

                 ] + on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n+'\n 1', key=n, pad=((60, 0), (0, 0)), enable_events=True) for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switch settings.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((250, 0), (20, 10))),
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
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper, auto_setup=False,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
