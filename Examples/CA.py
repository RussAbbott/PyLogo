
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

    def set_on_or_off(self, on_or_off: bool):
        self.is_on = on_or_off
        self.set_color(OnOffPatch.on_color if self.is_on else OnOffPatch.off_color)


class CA_World(OnOffWorld):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_to_switch = {2**i: bin_str(i, 3) for i in range(8)}
        self.old_rule_nbr = 110
        self.set_switches_from_rule_nbr(self.old_rule_nbr)
        self.set_binary_nbr_from_rule_nbr(self.old_rule_nbr)

    def get_rule_nbr_from_switches(self):
        rule_nbr = 0
        (_event, values) = gui.WINDOW.read(timeout=10)
        for (pos, key) in self.pos_to_switch.items():
            if values[key]:
                rule_nbr += pos
        return rule_nbr

    @staticmethod
    def set_binary_nbr_from_rule_nbr(rule_nbr):
        binary_rule_nbr = bin_str(rule_nbr, 8)
        gui.WINDOW['Rule_nbr'].update(value=rule_nbr)
        new_bin_value = '(' + binary_rule_nbr + ')'
        gui.WINDOW['bin_string'].update(value=new_bin_value)


    def set_switches_from_rule_nbr(self, rule_nbr):
        for pos in self.pos_to_switch:
            gui.WINDOW[self.pos_to_switch[pos]].update(value=rule_nbr % 2)
            rule_nbr = rule_nbr // 2

    def setup(self):
        # Make the slider and switches consistent with each other. Give switches priority.
        # That is, if both are different from self.old_rule_nbr,
        # use the value derived from the switches.
        new_switches_nbr = self.get_rule_nbr_from_switches()
        if self.old_rule_nbr != new_switches_nbr:
            self.old_rule_nbr = new_switches_nbr
        else:
            new_rule_nbr = SimEngine.get_gui_value('Rule_nbr')
            self.set_switches_from_rule_nbr(new_rule_nbr)
            self.old_rule_nbr = new_rule_nbr
        self.set_binary_nbr_from_rule_nbr(self.old_rule_nbr)
        # The Slider, the switches, and the bin number are now consistent: all contain self.old_rule_nbr.

        # Does the user want to start with a random initial row?
        rand = SimEngine.get_gui_value('random')
        if rand:
            # If so, set the initial row to random on/off
            for patch in CA_World.patches_array[0]:
                # Don't wrap. Keep the end patches off.
                if choice([True, False]) and 0 < patch.row_col.col < gui.PATCH_COLS-1:
                    patch.set_on_or_off(True)

    def step(self):
        """ You write this """
        pass


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

ca_left_upper = [[sg.CB('Initialize to random?', key='random')], HOR_SEP(30)] + \
                 on_off_left_upper


# bin_7_to_0 is ['111' .. '000']
bin_7_to_0 = [bin_str(n, 3) for n in range(7, -1, -1)]

# switches are CheckBoxes from '111' to '000'
switches = [sg.CB(n+'\n 1', key=n, pad=((30, 0), (0, 0))) for n in bin_7_to_0]

ca_right_upper = [[sg.Text('Rule number', pad=((120, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal', pad=((10, 20), (0, 10))),
                   sg.Text('(00000000)', key='bin_string', pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(CA_World, '1D CA',
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           patch_class=CA_Patch, fps=10)