
from typing import Tuple

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
        if abs(discrepancy) > 0:
            self.node_2.move_node(Velocity((0, discrepancy)))

    def extend_linked_nodes(self, LinkType):
        node_1 = self.node_2
        length = Braess_World.dist_unit
        if LinkType == Braess_Cord:
            length /= 2
        node_2 = Braess_Node(Pixel_xy((node_1.x, node_1.y + length)))
        link_construct = LinkType(node_1, node_2)
        return link_construct

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(int(self.node_1.distance_to(self.node_2)))

    def move_by_dxdy(self, dxdy: Tuple):
        self.node_1.move_by_dxdy(Velocity(dxdy))
        self.node_2.move_by_dxdy(Velocity(dxdy))

    def proper_length(self):
        """
        Since we are using abstract units for weight and length so that weight is equal to
        the amount a spring stretches, a spring should be as long as its resting length
        plus the weight it is supporting.
        """
        return self.resting_length + Braess_World.mass()

    def set_target_by_dxdy(self, dxdy: Tuple):
        for node in [self.node_1, self.node_2]:
            node.set_target_by_dxdy(Velocity(dxdy))

    @staticmethod
    def vertical_linked_nodes(LinkType, x, y_top, length=None):
        node_1 = Braess_Node(Pixel_xy((x, y_top)))
        if length is None:
            length = Braess_World.dist_unit
            if LinkType == Braess_Cord:
                length /= 2
        node_2 = Braess_Node(Pixel_xy((x, y_top + length)))
        link_construct = LinkType(node_1, node_2)
        return link_construct


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

    def reset_length(self):
        self.resting_length = self.node_1.distance_to(self.node_2)



class Braess_Node(Graph_Node):

    def __init__(self, location, shape_name=NODE, **kwargs):
        # Add color and shape_name to the key-word arguments.
        kwargs['color'] = Color('plum4' if shape_name == CIRCLE else 'orange')
        kwargs['shape_name'] = shape_name
        super().__init__(**kwargs)
        self.move_to_xy(location)

    @property
    def label(self):
        if self is not Braess_World.weight_node:
            return None
        return f'weight: 100; total dist: {str(int(Braess_World.weight_node.y - Braess_World.top))}'

    # noinspection PyTypeChecker
    def take_animation_step(self):
        if not self.animation_target:
            return

        Agent.some_agent_changed = True
        delta = self.animation_target - self.center_pixel
        self.move_node(delta)

        if abs(self.distance_to_pixel(self.animation_target)) < 0.5:
            self.move_to_xy(self.animation_target)
            self.animation_target = None


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
        self.state_transitions = {1: 'a', 'a': 2, 2: 2}

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        event holds the key of the widget that changed.
        """
        if event == Braess_World.CUT_CORD:
            self.setup_a()

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
        self.top_spring = Braess_Link.vertical_linked_nodes(Braess_Link, self.x, Braess_World.top)

        self.top_cord = self.top_spring.extend_linked_nodes(Braess_Cord)

        self.bottom_spring = self.top_cord.extend_linked_nodes(Braess_Link)

        self.weight_cord = self.bottom_spring.extend_linked_nodes(Braess_Cord)

        # Make the node_2 of the weight_cord the weight.
        Braess_World.weight_node = self.weight_cord.node_2
        Braess_World.weight_node.shape_name = CIRCLE
        Braess_World.weight_node.color = Color('plum4')

        #                            ## Done with building state 1. ##                            #

        self.adjustable_links = [self.top_spring, self.top_cord, self.bottom_spring, self.weight_cord]

        Agent.some_agent_changed = True
        Braess_World.state = 1
        SimEngine.gui_set(Braess_World.CUT_CORD, enabled=False)

    # noinspection PyAttributeOutsideInit
    def setup_a(self):
        """
        Set up for state 2. State 2 reuses and in some cases repurposes the elements of state 1.
        It also creates a new Node and a new String.
        """


        self.top_spring.move_by_dxdy((self.x_offset, 0))
        # self.top_spring.set_target_by_dxdy((self.x_offset, 0))

        self.weight_cord.set_target_by_dxdy((0, Braess_World.cord_slack))

        center_bar_node = self.bottom_spring.node_2

        # Construct the full bar.
        bar_y = center_bar_node.y
        left_bar_node = Braess_Node(Pixel_xy( (self.x, bar_y) ) )
        right_bar_node = Braess_Node(Pixel_xy( (self.x, bar_y) ) )

        # By convention, the position of node_1 determines node_2's position.
        self.bar_right = Braess_Bar(center_bar_node, right_bar_node)
        self.bar_left = Braess_Bar(center_bar_node, left_bar_node)

        # Attach the bottom spring to the left end of the bar.
        self.bottom_spring.node_2 = left_bar_node

        left_bar_node.set_target_by_dxdy(Velocity((-self.x_offset, Braess_World.cord_slack)))
        right_bar_node.set_target_by_dxdy(Velocity((self.x_offset, Braess_World.cord_slack)))

        # Attach the top cord to the right end of the bar rather than the center.
        self.top_cord.node_2 = right_bar_node

        # # Redefine its (fixed) resting length as its current length.
        # self.top_cord.reset_length()
        #
        # The left cord is a new element in state 2. It is offset to the left.
        x_coord = self.x   # - self.x_offset
        cord_length = self.bottom_spring.node_1.y + Braess_World.cord_slack - Braess_World.top
        self.left_cord = Braess_Link.vertical_linked_nodes(Braess_Cord,
                                                           x_coord, Braess_World.top,
                                                           length=cord_length)
        self.left_cord.move_by_dxdy((-self.x_offset, 0))
        # self.left_cord.set_target_by_dxdy(Velocity((-self.x_offset, 0)))
        # Make its bottom node the top node of the bottom spring.
        World.agents.remove(self.bottom_spring.node_1)
        self.bottom_spring.node_1 = self.left_cord.node_2
        # # Redefine its (fixed) resting length as its current length.
        # self.left_cord.reset_length()


        #                            ## Done with the adjustments for state 2. ##                            #

        # Add the new cord and bar nodes to the adjustable links.
        self.adjustable_links.extend([self.left_cord, self.bar_right, self.bar_left])

        Agent.some_agent_changed = True
        Braess_World.state = 'a'
        SimEngine.gui_set(Braess_World.CUT_CORD, enabled=False)
        # gui.WINDOW['GoStop'].click()

    def step(self):
        # If there was a change during the previous step, see if additional changes are needed.
        if Agent.some_agent_changed:
            # When a link changes length, Agent.some_agent_changed is set to True.
            Agent.some_agent_changed = False
            if Braess_World.state == 'a':
                visited_nodes = set()
                for node in World.agents:
                    if node.animation_target and node not in visited_nodes:
                        visited_nodes.add(node)
                        node.take_animation_step()
            else:
                for lnk in self.adjustable_links:
                    lnk.adjust_nodes()
        else:
            # If no adjustable link changed on the previous step, we're done. "Click" the STOP button.
            gui.WINDOW['GoStop'].click()

            if Braess_World.state == 'a':
                # Redefine the resting length of the two main cords.
                self.top_cord.reset_length()
                self.left_cord.reset_length()
                (self.bar_right.node_1, self.bar_right.node_2) = (self.bar_right.node_2, self.bar_right.node_1)
                (self.bar_left.node_1, self.bar_left.node_2) = (self.bar_left.node_2, self.bar_left.node_1)

            # Enable/disable the Cut-cord button depending on whether we just finished state 1 or state 2.
            SimEngine.gui_set(Braess_World.CUT_CORD, enabled=(Braess_World.state == 1))
            Braess_World.state = self.state_transitions[Braess_World.state]
            Agent.some_agent_changed = True


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
                              
                              'For a physical demo, see https://youtu.be/ekd2MeDBV8s.',
                              
                              pad=(None, (0, 10)))],
    
                     [sg.Button(Braess_World.CUT_CORD)]
                     ]


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, "Braess' spring paradox", gui_left_upper=braess_left_upper, agent_class=Braess_Node)
