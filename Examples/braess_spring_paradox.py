from math import copysign

from pygame.color import Color

import core.gui as gui
from core.agent import Agent
from core.graph_framework import Graph_Node   # , Graph_World
from core.gui import CIRCLE, NODE, SCREEN_PIXEL_WIDTH
from core.link import Link
from core.pairs import Pixel_xy, Velocity
from core.sim_engine import SimEngine
from core.world_patch_block import World


class Braess_Link(Link):
    """
    A Braess_Link links two Braess_Nodes. This is used mainly for springs.
    There are special subclasses for rigid bars and cords.
    """

    # Updated during each step() call.
    # When the system reaches equilibrium, this becomes False
    some_link_changed = None

    def __init__(self, *arags, **kwargs):
        super().__init__(*arags, **kwargs)
        # This is the resting length. All springs have this as their default length.
        self.resting_length = Braess_World.dist_unit
        if not (isinstance(self, Braess_Bar) or isinstance(self, Braess_Cord)):
            self.node_2.move_to_xy(Pixel_xy((self.node_2.x, self.node_1.y + self.resting_length)))
        self.color = Color('green')
        self.width = 2

    # ########################################################################################################

    # This is a strange and sometimes convenient Python feature. The following define node_1 and node_2 to
    # be getters and setters for node_1 and node_2 respectively. When used, parentheses are not needed.
    @property
    def node_1(self) -> Agent:
        return self.agent_1

    @node_1.setter
    def node_1(self, new_agent: Agent):
        self.agent_1 = new_agent

    @property
    def node_2(self) -> Agent:
        return self.agent_2

    @node_2.setter
    def node_2(self, new_agent: Agent):
        self.agent_2 = new_agent

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
            # Note that x and y have been defined to be getters for center pixels (x, y).
            new_center_pixel = Pixel_xy((self.node_2.x, self.node_2.y + adjusted_discrepancy))
            self.node_2.move_to_xy(new_center_pixel)

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(int(self.node_1.distance_to(self.node_2)))

    def proper_length(self):
        """
        Since we are using abstract units for weight and length so that weight is equal to
        the amount a spring stretches, a spring should be as long as its resting length
        plus the weight it is supporting.
        """
        return self.resting_length + Braess_World.mass()


class Braess_Bar(Braess_Link):
    """
    A Braess_Bar is a rigid horizontal bar. It remains horizontal.
    """

    def __init__(self, *arags, **kwargs):
        super().__init__(*arags, **kwargs)
        self.color = Color('violet')

    def adjust_nodes(self):
        """ Move node_2 up or down to match node_1. """
        if self.node_1.y != self.node_2.y:
            self.node_2.move_to_xy(Pixel_xy((self.node_2.x, self.node_1.y)))

    @property
    def label(self):
        """ Attach no label to a bar. """
        return None


class Braess_Cord(Braess_Link):
    """
    A Braess_Cord is a rigid vertical link. It retains its length whenever one of its ends is moved.
    """

    def __init__(self, node_1, node_2, **kwargs):
        super().__init__(node_1, node_2, **kwargs)
        self.resting_length = self.node_1.distance_to(self.node_2)
        self.color = Color('white')
        self.width = 1

    def proper_length(self):
        """ Since cords don't stretch, their proper_length is their resting length. """
        return self.resting_length


class Braess_Node(Graph_Node):

    def __init__(self, location, pinned=False, shape_name=NODE, **kwargs):
        # Add color and shape_name to the key-word arguments.
        kwargs['color'] = Color('plum4' if shape_name == CIRCLE else 'orange')
        kwargs['shape_name'] = shape_name
        super().__init__(**kwargs)
        # A Node may be pinned, i.e., fixed in placed. The top-most nodes are pinned.
        self.pinned = pinned
        self.move_to_xy(location)

    @property
    def label(self):
        if self is not Braess_World.weight_node:
            return None
        return f'weight: 100; total dist: {str(int(Braess_World.weight_node.y - Braess_World.top))}'


class Braess_World(World):

    CUT_CORD = 'Cut cord'

    cord_slack = 25

    dist_unit = 100

    # The system is in either of two states: series (1) or parallel (2)
    state = None

    top = 20

    # the weight_node is the plum-colored weight hanging at the bottom.
    weight_node = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = int(SCREEN_PIXEL_WIDTH()/2)
        self.x_offset = 20

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        event holds the key of the widget that changed.
        """
        if event == Braess_World.CUT_CORD:
            self.setup_2()

    @staticmethod
    def mass():
        """
        This is the value by which the weight_node pulls down on the springs.
        In state 1 (series) each node is pulled by the full weight. (We define weight
        in terms of the dist_unit because springs expand linearly with the weight
        pulling on them. In state 2 each node is pulled down by half the weight.
        """
        return Braess_World.dist_unit / Braess_World.state

    # noinspection PyAttributeOutsideInit
    def setup(self):
        """
        Set up for state 1. Build the contraption piece by piece.
        """
        # Create the top spring.
        self.top_spring_node_1 = Braess_Node(Pixel_xy( (self.x, Braess_World.top) ), pinned=True)
        self.top_spring_node_2 = Braess_Node(Pixel_xy( (self.x, self.top_spring_node_1.y +
                                                           Braess_World.dist_unit) ) )
        self.top_spring = Braess_Link(self.top_spring_node_1, self.top_spring_node_2)

        # Create the cord connecting the two springs.
        # Create top node of the bottom spring.
        self.bottom_spring_node_1 = Braess_Node(Pixel_xy( (self.x,
                                                           self.top_spring_node_2.y +
                                                           Braess_World.dist_unit/2) ) )
        self.cord_1 = Braess_Cord(self.top_spring_node_2, self.bottom_spring_node_1)

        # Create the bottom spring.
        #     bar_y is the height of the bottom node of the bottom spring.
        #     It is also the height of the bar to be created latter.
        #     We use the center node of that bar as the bottom node of the bottom spring.
        bar_y = self.bottom_spring_node_1.y + Braess_World.dist_unit
        self.bar_node_center = Braess_Node(Pixel_xy( (self.x, bar_y) ))
        self.bottom_spring = Braess_Link(self.bottom_spring_node_1, self.bar_node_center)

        # Create the weight node and the cord that attaches it to the bottom spring.
        Braess_World.weight_node = Braess_Node(Pixel_xy( (self.x, bar_y + Braess_World.dist_unit/2)),
                                               shape_name=CIRCLE)
        self.weight_cord = Braess_Cord(self.bar_node_center, Braess_World.weight_node)

        # ## Done with the construction for state 1. ## #

        # These are the links whose lengths are adjusted as the weight_node pulls on them.
        # The two cords do not have their lengths change but their node positions change.
        self.adjustable_links = [self.top_spring, self.cord_1, self.bottom_spring, self.weight_cord]

        Braess_Link.some_link_changed = True
        Braess_World.state = 1
        SimEngine.gui_set(Braess_World.CUT_CORD, enabled=False)

    # noinspection PyAttributeOutsideInit
    def setup_2(self):
        """
        Set up for state 2. State 2 reuses and in some cases repurposes the elements of state 1.
        It also creates a new Node and a new String.
        """
        # Move the top spring to the right by x_offset
        self.top_spring_node_1.move_by_dxdy(Velocity((self.x_offset, 0)))
        self.top_spring_node_2.move_by_dxdy(Velocity((self.x_offset, 0)))

        # Move the center bar node and the weight down by the slack in the new cords.
        self.bar_node_center.move_by_dxdy(Velocity((0, Braess_World.cord_slack)))
        Braess_World.weight_node.move_by_dxdy(Velocity((0, Braess_World.cord_slack)))

        # Construct the full bar. By the convention built into Braess-Bar,
        # the position of node_1 determines node_2's position.
        bar_y = self.bar_node_center.y
        self.bar_node_left = Braess_Node(Pixel_xy( (self.x - self.x_offset, bar_y) ) )
        self.bar_node_right = Braess_Node(Pixel_xy( (self.x + self.x_offset, bar_y) ) )

        self.bar_right = Braess_Bar(self.bar_node_right, self.bar_node_center)
        self.bar_left = Braess_Bar( self.bar_node_left, self.bar_node_center)
        # Move the bottom of spring 2 from the center of the bar to its left end.
        self.bottom_spring.node_2 = self.bar_node_left

        # Change cord_1 to link to the node at the right of the bar rather than the center.
        self.cord_1.node_2 = self.bar_node_right
        # Redefine its (fixed) resting length as its current length.
        self.cord_1.resting_length = self.cord_1.node_1.distance_to(self.cord_1.node_2)

        # The left cord is a new element in state 2. It consists of a new Node and a new String.
        # It is offset to the left.
        self.top_left_cord_node = Braess_Node(Pixel_xy((self.x - self.x_offset, Braess_World.top)), pinned=True)
        self.bottom_spring_node_1.move_by_dxdy(Velocity((- self.x_offset, Braess_World.cord_slack)))
        self.left_cord = Braess_Cord(self.top_left_cord_node, self.bottom_spring_node_1)

        # ## Done with the adjustments for state 2. ## #

        # Add the new cord and bar nodes to the adjustable links.
        self.adjustable_links.extend([self.left_cord, self.bar_right, self.bar_left])

        Braess_Link.some_link_changed = True
        Braess_World.state = 2
        SimEngine.gui_set(Braess_World.CUT_CORD, enabled=False)

    def step(self):
        # If there was a change during the previous step, see if additional changes are needed.
        if Braess_Link.some_link_changed:
            # When a link changes length, Braess_Link.some_link_changed is set to True.
            Braess_Link.some_link_changed = False
            for lnk in self.adjustable_links:
                lnk.adjust_nodes()
        else:
            # If no adjustable link changed on the previous step, we're done. "Click" the STOP button.
            gui.WINDOW['GoStop'].click()
            # Enable/disable the Cut-cord button depending on whether we just finished state 1 or state 2.
            SimEngine.gui_set(Braess_World.CUT_CORD, enabled=(self.state == 1))


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. There is only one model-specific gui widget.
"""
braess_left_upper = [
                     [sg.Text('Two green springs (unstretched length 100 units) are connected by\n'
                              'two white fixed-length 50 unit cords to a plum-colored weight.\n\n'
                              
                              "Click 'go' to allow the weight to pull on the springs.\n\n"
                              
                              "When a weight pulls on a spring, the spring extends in proportion to the\n"
                              'weight. In this case the weight is 100 units. Each spring will stretch to 200\n'
                              'units. See "total dist" on the weight label for the top to bottom distance.\n\n'
                              
                              "Now click 'Cut cord.' The weight drops by 25 units before being caught by\n"
                              'two new cords (of length 275). (The cut cord is not shown.) Cutting the cord\n'
                              'converts the system from a single support line to two lines, each of which\n'
                              'uses a single spring. (There are still two springs holding up the weight.)\n\n'
                              
                              "Click 'go' to let the system reach a new equilibrium. The weight rises! Why?\n\n"
                              
                              'In series, each spring bears 100 units (Why?) and stretches to 200 units.\n'
                              'In parallel, each spring bears (50 units) (Why?) and stretches to 150 units.\n\n'
                                                            
                              'Cutting the cord is equivalent to removing(!) the extra road in the Braess road \n'
                              'paradox. It forces the weight (the "traffic") to be split between the two sides.\n\n'
                              
                              'For a physical demo, see https://youtu.be/ekd2MeDBV8s.'
                              
                              ,
                              pad=(None, (0, 10)))],
    
                     [sg.Button(Braess_World.CUT_CORD)]
                     ]


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, "Braess' spring paradox", gui_left_upper=braess_left_upper, agent_class=Braess_Node)
