from math import copysign

from pygame.color import Color

import core.gui as gui
from core.graph_basics import Basic_Graph_Node, Basic_Graph_World
from core.gui import CIRCLE, NODE, SCREEN_PIXEL_WIDTH
from core.link import Link
from core.pairs import Pixel_xy, Velocity


class Braess_Link(Link):
    """
    A Braess_Link links two Braess_Nodes together. This is used mainly for springs.
    There are special subclasses for rigid bars and strings.
    """

    # When the system reaches equilibrium, this becomes False
    some_link_changed = None

    def __init__(self, node_1, node_2, **kwargs):
        super().__init__(node_1, node_2, **kwargs)
        (self.node_1, self.node_2) = (self.agent_1, self.agent_2)
        # This is the resting length. All standard links have this as their default length.
        self.length = Braess_World.dist_unit
        if not (isinstance(self, Braess_Bar) or isinstance(self, Braess_String)):
            self.node_2.move_to_xy(Pixel_xy((self.node_2.x, self.node_1.y + self.length)))
        self.color = Color('green')
        self.width = 2

    # ########################################################################################################

    # This is a strange andometimes convenient Python feature. The following define node_1 and node_2 as
    # getters and setters for agent_1 and agent_2.
    @property
    def node_1(self):
        return self.agent_1

    @node_1.setter
    def node_1(self, val):
        self.agent_1 = val

    @property
    def node_2(self):
        return self.agent_2

    @node_2.setter
    def node_2(self, val):
        self.agent_2 = val

    # ########################################################################################################

    def adjust_nodes(self):
        """
        If the actual length doesn't match the proper length, move Node_2 vertically (up or down) until
        it does match. Each step moves Node_2 by at most 1 pixel.
        """
        actual_length = self.node_1.distance_to(self.node_2)
        discrepancy = self.proper_length() - actual_length
        adjusted_discrepancy = copysign(min(1, abs(discrepancy)), discrepancy)
        if abs(adjusted_discrepancy) > 0:
            Braess_Link.some_link_changed = True
            # Note that x and y have been defined to be getters for the (x, y) center pixels.
            new_center_pixel = Pixel_xy((self.node_2.x, self.node_2.y + adjusted_discrepancy))
            self.node_2.move_to_xy(new_center_pixel)

    def proper_length(self):
        divisor = len(Braess_World.weight.lnk_nbrs())
        prpr_len = self.length + Braess_World.mass() / divisor
        return prpr_len


class Braess_Bar(Braess_Link):
    """
    A Braess_Bar is a rigid horizontal bar. It remains horizontal
    """

    def __init__(self, node_1, node_2, **kwargs):
        super().__init__(node_1, node_2, **kwargs)
        self.length = Braess_World.dist_unit/2
        self.color = Color('violet')

    def adjust_nodes(self):
        """ Move node_2 up or down to match node_1. """
        if self.node_1.y != self.node_2.y:
            self.node_2.move_to_xy(Pixel_xy((self.node_2.x, self.node_1.y)))


class Braess_String(Braess_Link):
    """
    A Braess_String is a rigid vertical link. It retains its length whenever one of its ends is moved.
    """

    def __init__(self, node_1, node_2, **kwargs):
        super().__init__(node_1, node_2, **kwargs)
        self.length = self.node_1.distance_to(self.node_2)
        self.color = Color('white')
        self.width = 1

    def proper_length(self):
        return self.length


class Braess_Node(Basic_Graph_Node):

    def __init__(self, location, pinned=False, shape_name=NODE, **kwargs):
        kwargs['color'] = Color('slateblue' if shape_name == CIRCLE else 'orange')
        kwargs['shape_name'] = shape_name
        super().__init__(**kwargs)
        # A Node may be pinned, i.e., fixed in placed. The top-most nodes are always pinned.
        self.pinned = pinned
        self.move_to_xy(location)


class Braess_World(Basic_Graph_World):

    dist_unit = 100

    # The weight is the weight hanging from the springs
    weight = None

    # The system is in either of two states: series or parallel
    state = None

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)
        self.x = int(SCREEN_PIXEL_WIDTH()/2)
        self.x_offset = 50

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle link/node creation/deletion request events.
        if event == 'Cut string':
            self.setup_2()

    @staticmethod
    def mass():
        """
        This is the value by which the weight pulls down on the springs.
        In state 1 (series) each node is pulled by the full weight, which is equal to the dist_unit.
        We define the weight in terms of the dist_unit because springs expand linearly with the weight
        pulling on them.
        """
        return Braess_World.dist_unit / Braess_World.state

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """
        Set up for state 1.
        """

        self.top_spring_node_1 = Braess_Node(Pixel_xy( (self.x, 20) ), pinned=True)
        self.top_spring_node_2 = Braess_Node(Pixel_xy( (self.x, self.top_spring_node_1.y +
                                                           Braess_World.dist_unit) ) )
        self.top_spring = Braess_Link(self.top_spring_node_1, self.top_spring_node_2)

        self.bottom_spring_node_1 = Braess_Node(Pixel_xy( (self.x,
                                                           self.top_spring_node_2.y +
                                                           Braess_World.dist_unit/2) ) )
        self.string_1 = Braess_String(self.top_spring_node_2, self.bottom_spring_node_1)

        bar_y = self.bottom_spring_node_1.y + Braess_World.dist_unit

        self.bar_node_center = Braess_Node(Pixel_xy( (self.x, bar_y) ))

        self.bottom_spring = Braess_Link(self.bottom_spring_node_1, self.bar_node_center)

        self.bar_node_left = Braess_Node(Pixel_xy( (self.x - self.x_offset, bar_y) ) )
        self.bar_node_right = Braess_Node(Pixel_xy( (self.x + self.x_offset, bar_y) ) )

        self.bar_left = Braess_Bar(self.bar_node_center, self.bar_node_left)
        self.bar_right = Braess_Bar(self.bar_node_center, self.bar_node_right)

        Braess_World.weight = Braess_Node(Pixel_xy( (self.x, bar_y + Braess_World.dist_unit/2)),
                                                     shape_name=CIRCLE)

        self.weight_string = Braess_String(self.bar_node_center, Braess_World.weight)

        # These are the links whose lengths are adjusted as the weight pulls on them.
        self.adjustable_links = [self.top_spring, self.string_1, self.bottom_spring,
                                 self.bar_left, self.bar_right, self.weight_string]

        Braess_Link.some_link_changed = True
        Braess_World.state = 1

    # noinspection PyAttributeOutsideInit
    def setup_2(self):
        """
        Set up for state 2. State 2 reuses and in some cases repurposes the elements of state 1.
        It also creates a new Node and a new String.
        """

        # Move the stop spring to the right by x_offset
        self.top_spring_node_1.move_by_dxdy(Velocity((self.x_offset, 0)))
        self.top_spring_node_2.move_by_dxdy(Velocity((self.x_offset, 0)))

        # Change string_1 to link to the node as the right of the bar rather than the center
        self.string_1.agent_2 = self.bar_node_right
        # Redefine its length as its current length
        self.string_1.length = self.string_1.node_1.distance_to(self.string_1.node_2)

        # The left string is a new element in state 2. It consists of a new Node and a new String.
        self.top_left_string_node = Braess_Node(Pixel_xy((self.x - self.x_offset, 20)), pinned=True)
        self.bottom_spring_node_1.move_by_dxdy(Velocity((- self.x_offset, 0)))
        self.left_string = Braess_String(self.top_left_string_node, self.bottom_spring_node_1)

        # Add the new string to the adjustable links.
        self.adjustable_links.insert(2, self.left_string)

        # Move the bottom of spring 2 to the left end of the bar.
        self.bottom_spring.agent_2 = self.bar_node_left

        # Invert agent_1 and agent_2 in the two bars. By convention agent_1 position determines agent_2's position.
        (self.bar_right.agent_1, self.bar_right.agent_2) = (self.bar_right.agent_2, self.bar_right.agent_1)
        (self.bar_left.agent_1, self.bar_left.agent_2) = (self.bar_left.agent_2, self.bar_left.agent_1)

        Braess_Link.some_link_changed = True
        Braess_World.state = 2

    def step(self):
        if Braess_Link.some_link_changed:
            # This keeps track of whether any adjustable link has changed. (Or have they reached equilibrium?)
            # When a link changes length, Braess_Link.some_link_changed is set to True.
            # See Braess_Link.adjust_nodes.)
            Braess_Link.some_link_changed = False
            for lnk in self.adjustable_links:
                lnk.adjust_nodes()
        else:
            # If no adjustable link changed on the previous step, we're done. "click" the STOP button.
            gui.WINDOW['GoStop'].click()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. There is only one model-specific gui widget.
"""
braess_left_upper = [[sg.Button('Cut string')],
                     [sg.Text("Click 'go' to allow the weight to pull on the (green) \n"
                              "springs. When the springs reach equilibrium, click \n"
                              "'Cut string' to convert the system from two springs \n"
                              'in series of two springs in parallel--each side shares \n'
                              "half the load. Click 'go' again to let the let the \n"
                              'system reach a new equilibrium.\n\n'
                              'That the series system hangs lower than the parallel\n'
                              'system is sometimes considered paradoxical.\n\n'
                              'Note that the white "strings" retain their length\n'
                              'and simply provide stability for the strings.')]
                     ]


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, 'Network test', gui_left_upper=braess_left_upper, agent_class=Braess_Node, auto_setup=True)
