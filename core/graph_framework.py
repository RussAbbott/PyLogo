
from math import sqrt
from random import choice, sample
from typing import List, Optional, Tuple

from pygame.color import Color
from pygame.draw import circle

import core.gui as gui
from core.agent import Agent, PYGAME_COLORS
from core.gui import (BLOCK_SPACING, CIRCLE, HOR_SEP, KNOWN_FIGURES, NETLOGO_FIGURE, SCREEN_PIXEL_HEIGHT,
                      SCREEN_PIXEL_WIDTH, STAR)
from core.link import Link, link_exists
from core.pairs import Pixel_xy, Velocity
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Graph_Node(Agent):

    def __init__(self, **kwargs):
        if 'color' not in kwargs:
            color = SimEngine.gui_get(COLOR)
            kwargs['color'] = Color(color) if color != RANDOM else None
        if 'shape_name' not in kwargs:
            shape_name = SimEngine.gui_get(SHAPE)
            kwargs['shape_name'] = shape_name
        super().__init__(**kwargs)

        # Is the  node selected?
        self.selected = False

    def __str__(self):
        return f'FLN-{self.id}'

    def adjust_distances(self, screen_distance_unit, velocity_adjustment=1):

        normalized_force = self.compute_velocity(screen_distance_unit, velocity_adjustment)
        self.set_velocity(normalized_force)
        self.forward()

    def compute_velocity(self, screen_distance_unit, velocity_adjustment):
        repulsive_force: Velocity = Velocity((0, 0))

        for node in (World.agents - {self}):
            repulsive_force += self.force_as_dxdy(self.center_pixel, node.center_pixel, screen_distance_unit,
                                                  repulsive=True)

        # Also consider repulsive force from walls.
        repulsive_wall_force: Velocity = Velocity((0, 0))

        horizontal_walls = [Pixel_xy((0, 0)), Pixel_xy((SCREEN_PIXEL_WIDTH(), 0))]
        x_pixel = Pixel_xy((self.center_pixel.x, 0))
        for h_wall_pixel in horizontal_walls:
            repulsive_wall_force += self.force_as_dxdy(x_pixel, h_wall_pixel, screen_distance_unit, repulsive=True)

        vertical_walls = [Pixel_xy((0, 0)), Pixel_xy((0, SCREEN_PIXEL_HEIGHT()))]
        y_pixel = Pixel_xy((0, self.center_pixel.y))
        for v_wall_pixel in vertical_walls:
            repulsive_wall_force += self.force_as_dxdy(y_pixel, v_wall_pixel, screen_distance_unit, repulsive=True)

        attractive_force: Velocity = Velocity((0, 0))
        for node in (World.agents - {self}):
            if link_exists(self, node):
                attractive_force += self.force_as_dxdy(self.center_pixel, node.center_pixel, screen_distance_unit,
                                                       repulsive=False)

        # noinspection PyTypeChecker
        net_force: Velocity = repulsive_force + repulsive_wall_force + attractive_force
        normalized_force: Velocity = net_force / max([net_force.x, net_force.y, velocity_adjustment])
        normalized_force *= 10

        if SimEngine.gui_get(PRINT_FORCE_VALUES):
            print(f'{self}. \n'
                  f'rep-force {tuple(repulsive_force.round(2))}; \n'
                  f'rep-wall-force {tuple(repulsive_wall_force.round(2))}; \n'
                  f'att-force {tuple(attractive_force.round(2))}; \n'
                  f'net-force {tuple(net_force.round(2))}; \n'
                  f'normalized_force {tuple(normalized_force.round(2))}; \n\n'
                  )
        return normalized_force

    def delete(self):
        World.agents.remove(self)
        World.links -= {lnk for lnk in World.links if lnk.includes(self)}

    def draw(self, shape_name=None):
        super().draw(shape_name=shape_name)
        if self.selected:
            radius = round((BLOCK_SPACING() / 2) * self.scale * 1.5)
            circle(gui.SCREEN, Color('red'), self.rect.center, radius, 1)

    @staticmethod
    def force_as_dxdy(pixel_a: Pixel_xy, pixel_b: Pixel_xy, screen_distance_unit, repulsive):
        """
        Compute the force between pixel_a pixel and pixel_b and return it as a velocity: direction * force.
        """
        direction: Velocity = normalize_dxdy( (pixel_a - pixel_b) if repulsive else (pixel_b - pixel_a) )
        d = max(1, pixel_a.distance_to(pixel_b))  #, wrap=False))
        if repulsive:
            dist = max(1, pixel_a.distance_to(pixel_b) / screen_distance_unit)  #, wrap=False)
            rep_coefficient = SimEngine.gui_get(REP_COEFF)
            rep_exponent = SimEngine.gui_get(REP_EXPONENT)
            force = direction * ((10**rep_coefficient)/10) * dist**rep_exponent
            return force
        else:  # attraction
            dist = max(1, max(d, screen_distance_unit) / screen_distance_unit)
            att_exponent = SimEngine.gui_get(ATT_EXPONENT)
            force = direction*dist**att_exponent
            # If the link is too short, push away instead of attracting.
            if d < screen_distance_unit:
                force = force*(-1)
            att_coefficient = SimEngine.gui_get(ATT_COEFF)
            final_force = force * 10**(att_coefficient-1)
            return final_force


class Graph_World(World):

    def __init__(self, patch_class, agent_class):
        self.velocity_adjustment = 1
        super().__init__(patch_class, agent_class)
        self.shortest_path_links = None
        self.selected_nodes = set()

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

    def build_graph(self):
        """
        Arrange all the nodes (or all but one) as a ring.
        Then link them depending on the kind of network desired.
        """
        nbr_nodes = SimEngine.gui_get(NBR_NODES)
        graph_type = SimEngine.gui_get(GRAPH_TYPE)

        # If we are generating a star or a wheel network, arrange nbr_nodes-1 as
        # a ring and use the other node as the center node.

        # If we are generating another type of graph, arrange all the nodes as a ring.

        nbr_ring_nodes = (nbr_nodes - 1) if graph_type in ['star', 'wheel'] else nbr_nodes

        # create_ordered_agents() creates the indicated number of nodes and arranges
        # them in a ring. It returns a list of the nodes in ring-order.
        ring_node_list = self.create_ordered_agents(nbr_ring_nodes, shape_name=SimEngine.gui_get(SHAPE))

        # Link the nodes to complete the desired graph.
        if nbr_nodes:
            self.link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list)

    def build_shortest_path(self):
        Graph_World.reset_links()
        self.selected_nodes = [node for node in World.agents if node.selected]
        # If there are exactly two selected nodes, find the shortest path between them.
        if len(self.selected_nodes) == 2:
            self.shortest_path_links = self.shortest_path()
            # self.shortest_path_links will be either a list of links or None
            # If there is a path, highlight it.
            if self.shortest_path_links:
                for lnk in self.shortest_path_links:
                    lnk.color = Color('red')
                    lnk.width = 2

    def compute_metrics(self):
        clust_coefficient = self.clustering_coefficient()
        SimEngine.gui_set(CLUSTER_COEFF, value=clust_coefficient)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set(PATH_LENGTH, value=avg_path_length)

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        return TBD

    @staticmethod
    def create_random_link():
        """
        Create a new link between two random nodes, if possible.
        The approach is to pick a random node and then pick another random node
        with no link to the first one. If there are no nodes that are not already
        linked to the first node, select a different first node. Repeat until
        a pair of nodes is found that can be linked. If all pairs of nodes
        are already linked, do nothing.
        """
        link_created = False
        # sample() both copies and shuffles elements from its first argument.
        # Can't use choice with World.agents because world.agents is a set and 
        # can't be accessed through an index, which is what choice uses.
        node_set_1 = sample(World.agents, len(World.agents))
        while not link_created:
            node_1 = node_set_1.pop()
            # Since node_1 has been popped from node_set_1,
            # node_set_2 does not contain node_1.
            # Can't use choice with a set.
            node_set_2 = sample(node_set_1, len(node_set_1))
            while node_set_2:
                node_2 = node_set_2.pop()
                if not link_exists(node_1, node_2):
                    Link(node_1, node_2)
                    link_created = True
                    break

    def delete_a_shortest_path_link(self):
        """
        Look for a link to delete so that there is still some shortest path.
        Pick the one with the longest shortest path.
        """
        (longest_path_len, lnk) = (0, None)
        for lnk_x in self.shortest_path_links:
            World.links.remove(lnk_x)
            path = self.shortest_path()
            if path and len(path) > longest_path_len:
                (longest_path_len, lnk) = (len(path), lnk_x)
            World.links.add(lnk_x)

        if not lnk:
            lnk = choice(self.shortest_path_links)
        World.links.remove(lnk)

    def disable_enable_buttons(self):
        # 'enabled' is a pseudo attribute. SimEngine.gui_set replaces it with 'disabled' and negates the value.

        SimEngine.gui_set(DELETE_RANDOM_NODE, enabled=bool(World.agents))

        SimEngine.gui_set(DELETE_RANDOM_LINK, enabled=bool(World.links))
        SimEngine.gui_set(CREATE_RANDOM_LINK, enabled=len(World.links) < len(World.agents)*(len(World.agents)-1)/2)

        SimEngine.gui_set(DELETE_SHORTEST_PATH_LINK, enabled=self.shortest_path_links and len(self.selected_nodes) == 2)

        # Show node id's or not as requested.
        show_labels = SimEngine.gui_get(SHOW_NODE_IDS)
        for node in World.agents:
            node.label = str(node.id) if show_labels else None

    def draw(self):
        self.build_shortest_path()
        # Update which buttons are enabled.
        self.disable_enable_buttons()
        super().draw()

    @staticmethod
    def link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        To be overridden in subclasses.
        """
        pass

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle color change requests.
        super().handle_event(event)

        # Handle link/node creation/deletion request events.
        if event == CREATE_NODE:
            self.agent_class()
        elif event == DELETE_RANDOM_NODE:
            # Can't use choice with a set.
            node = sample(World.agents, 1)[0]
            node.delete()
        elif event == CREATE_RANDOM_LINK:
            self.create_random_link()
        elif event == DELETE_RANDOM_LINK:
            World.links.pop()
        elif event == DELETE_SHORTEST_PATH_LINK:
            self.delete_a_shortest_path_link()

    def mouse_click(self, xy: Tuple[int, int]):
        """ Select closest node. """
        patch = self.pixel_tuple_to_patch(xy)
        if len(patch.agents) == 1:
            node = sample(patch.agents, 1)[0]
        else:
            patches = patch.neighbors_24()
            nodes = {node for patch in patches for node in patch.agents}
            node = nodes.pop() if nodes else Pixel_xy(xy).closest_block(World.agents)
        if node:
            node.selected = not node.selected

    @staticmethod
    def reset_links():
        # Set all the links back to normal.
        for lnk in World.links:
            lnk.color = lnk.default_color
            lnk.width = 1

    @staticmethod
    def screen_distance_unit():
        dist_unit = SimEngine.gui_get(DIST_UNIT)
        screen_distance_unit = sqrt(SCREEN_PIXEL_WIDTH() ** 2 + SCREEN_PIXEL_HEIGHT() ** 2) / dist_unit
        return screen_distance_unit

    def setup(self):
        self.disable_enable_buttons()
        self.build_graph()
        self.compute_metrics()

    def shortest_path(self) -> Optional[List[Link]]:
        (node1, node2) = self.selected_nodes
        # Start with the node with the smaller number of neighbors.
        if len(node1.lnk_nbrs()) > len(node2.lnk_nbrs()):
            (node1, node2) = (node2, node1)
        visited = {node1}

        # A path is a sequence of tuples (link, node) where
        # the link attaches to the node in the preceding
        # tuple. The first tuple in a path starts with a
        # None link since there is no preceding node.

        # The frontier is a list of paths, shortest first.
        frontier = [[(None, node1)]]
        while frontier:
            current_path = frontier.pop(0)
            # The lnk_nbrs are tuples as in the paths. For a given node
            # they are all the node's links along with the nodes linked to.

            # This gets the last node in the current path,
            (_last_link, last_node) = current_path[-1]

            # This gets all the non-visited lnk_nbrs of the last node.
            # Each neighbor is a (link, node) pair. 
            lnk_nbrs = [(lnk, nbr) for (lnk, nbr) in last_node.lnk_nbrs() if nbr not in visited]

            # Do any of these continuations reach the target, node_2? If so, we've found the shortest path.
            lnks_to_node_2 = [(lnk, nbr) for (lnk, nbr) in lnk_nbrs if nbr == node2]

            # If lnks_to_node_2 is non-empty it will have one element: (lnk, node_2)
            if lnks_to_node_2:
                path = current_path + lnks_to_node_2
                # Extract the links, but drop the None at the beginning.
                lnks = [lnk for (lnk, _nbr) in path[1:]]
                return lnks

            # Not done. Add the newly reached nodes to visted.
            visited |= {nbr for (_lnk, nbr) in lnk_nbrs}

            # For each neighbor construct an extended version of the current path.
            extended_paths = [current_path + [lnk_nbr] for lnk_nbr in lnk_nbrs]

            # Add all those extended paths to the frontier.
            frontier += extended_paths

        # If we get out of the loop because the frontier is empty, there is no path from node_1 to node_2.
        return None

    def step(self):
        dist_unit = Graph_World.screen_distance_unit()
        if SimEngine.gui_get(LAYOUT) == FORCE_DIRECTED:
            for node in World.agents:
                node.adjust_distances(dist_unit, self.velocity_adjustment)

        self.compute_metrics()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

# Keys and other GUI strings. Grouped together more or less as they appear in the GUI.

CREATE_NODE = 'Create node'
DELETE_RANDOM_NODE = 'Delete random node'

DELETE_RANDOM_LINK = 'Delete random link'
CREATE_RANDOM_LINK = 'Create random link'
DELETE_SHORTEST_PATH_LINK = 'Delete a shortest-path link'

LAYOUT = 'layout'
FORCE_DIRECTED = 'force-directed'
CLEAR = 'clear'

GRAPH_TYPE = 'graph type'

PREF_ATTACHMENT = 'pref attachment'
RANDOM = 'random'
RING = 'ring'
SMALL_WORLD = 'small world'
WHEEL = 'wheel'

LINK_PROB = 'link_prob'
CLUSTER_COEFF = 'cluster_coeff'
PATH_LENGTH = 'path_length'
TBD = 'TBD'

REP_COEFF = 'rep_coeff'
REP_EXPONENT = 'rep_exponent'
ATT_COEFF = 'att_coeff'
ATT_EXPONENT = 'att_exponent'
DIST_UNIT = 'dist_unit'
SHOW_NODE_IDS = "Show node id's"
PRINT_FORCE_VALUES = 'Print force values'

NBR_NODES = 'nbr_nodes'
SHAPE = 'shape'
COLOR = 'color'

tt = 'Probability that two nodes in a random graph will be linked\n' \
     'or that a link in a small world graph will be rewired'


graph_left_upper = [
                    [
                     sg.Button(CREATE_RANDOM_LINK, tooltip='Create a random link', pad=((0, 10), (5, 0))),
                     sg.Col([[sg.Button(DELETE_RANDOM_LINK, tooltip='Delete a random link',
                                        pad=((10, 10), (5, 0)))],
                             [sg.Button(DELETE_SHORTEST_PATH_LINK,
                                        tooltip='Delete a random link on the shortest path',
                                        pad=((0, 0), (5, 0)))]])
                     ],

                    HOR_SEP(pad=((50, 0), (0, 0))),

                    [sg.Text(LAYOUT, pad=((0, 0), (20, 0))),
                     sg.Combo([CIRCLE, FORCE_DIRECTED], key=LAYOUT, size=(11, 20),
                               pad=((5, 0), (20, 0)), default_value=FORCE_DIRECTED, tooltip='Select a layout'),

                     sg.Text('Graph type', pad=((10, 0), (20, 0))),
                     sg.Combo([PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, STAR, WHEEL], size=(11, 20),
                              key=GRAPH_TYPE, pad=((5, 0), (20, 0)), default_value=WHEEL, tooltip='graph type')],

                    [sg.Text('Random graph link prob\nSmall world rewire prob', pad=((0, 10), (20, 0)),
                             tooltip=tt),
                     sg.Slider((0, 100), default_value=10, orientation='horizontal', key=LINK_PROB,
                               size=(10, 20), pad=((0, 0), (10, 0)),
                               tooltip=tt)],

                    [sg.Text('Clustering coeff', pad=(None, (20, 0))),
                     sg.Text('None', background_color='white', text_color='black', key=CLUSTER_COEFF,
                             pad=((5, 0), (20, 0))),
                     sg.Text('Avg path length', pad=((20, 0), (20, 0))),
                     sg.Text('None', background_color='white', text_color='black', key=PATH_LENGTH,
                             pad=((5, 0), (20, 0)))],

                    HOR_SEP(pad=((50, 0), (0, 0))),

                    [sg.Text('Repulsion coefficient', pad=((0, 10), (20, 0)),
                             tooltip='Larger is stronger.'),
                     sg.Slider((1, 5), default_value=1, orientation='horizontal', key=REP_COEFF,
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Negative means raise to the power and divide (like gravity).\n'
                                       'Larger magnitude means distince reduces repulsive force more.')],

                    [sg.Text('Repulsion exponent', pad=((0, 10), (20, 0)),
                             tooltip='Negative means raise to the power and divide (like gravity).\n'
                                     'Larger magnitude means distince reduces repulsive force more.'),
                     sg.Slider((-5, -1), default_value=-2, orientation='horizontal', key=REP_EXPONENT,
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Negative means raise to the power and divide (like gravity).\n'
                                       'Larger magnitude means distince reduces repulsive force more.')],

                    [sg.Text('Attraction coefficient', pad=((0, 10), (20, 0)),
                             tooltip='If > distance unit, larger magnitude means \n'
                                     'increase force more with distance (like a spring)\n'
                                     'If < distance unit, force becomes repulsive (also like a spring)'),
                     sg.Slider((1, 6), default_value=1, orientation='horizontal', key=ATT_COEFF,
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='If distance > distance unit, larger magnitude means \n'
                                       'increase force more with distance (like a spring)\n'
                                       'If distance < distance unit, force becomes repulsive (also like a spring)')],

                    [sg.Text('Attraction exponent', pad=((0, 10), (20, 0)),
                             tooltip='If > distance unit, larger magnitude means \n'
                                     'increased force more with distance (like a stretched spring)\n'
                                     'If < distance unit, force becomes repulsive\n'
                                     '(like a compressed spring)'),
                     sg.Slider((0, 10), default_value=2, orientation='horizontal', key=ATT_EXPONENT,
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='If distance > distance unit, larger magnitude means \n'
                                       'increased force more with distance (like a spring)\n'
                                       'If distance < distance unit, force becomes repulsive\n'
                                       '(like a compressed spring)')],

                    [sg.Text('Distance unit/ideal link length', pad=((0, 10), (20, 0)),
                             tooltip='The fraction of the screen diagonal used as one unit.'),
                     sg.Slider((3, 16), default_value=8, orientation='horizontal', key=DIST_UNIT,
                               resolution=1, pad=((0, 0), (0, 0)), size=(10, 20),
                               tooltip='The fraction of the screen diagonal used as one unit.')],

                    [
                     sg.Checkbox("Show node id's", key=SHOW_NODE_IDS, default=False, pad=((20, 0), (20, 0))),
                     sg.Checkbox('Print force values', key=PRINT_FORCE_VALUES, default=False, pad=((20, 0), (20, 0)))
                     ],

                   ]


graph_right_upper = [
                     [
                      sg.Col([
                              [sg.Button(CREATE_NODE, tooltip='Create a node'),
                               sg.Button(DELETE_RANDOM_NODE, tooltip='Delete one random node')],

                              [sg.Text('Click two nodes for shortest path')]],
                              pad=((0, 0), None)),

                      sg.Col([
                              [sg.Text('Nodes', pad=((0, 0), (15, 0))),
                               sg.Slider((0, 20), default_value=9, orientation='horizontal', key=NBR_NODES,
                                         size=(10, 20), tooltip='Nbr of nodes created by setup')
                               ],
                              # The "pad" on the next line is for the Col widget.
                              ], pad=((0, 0), (5, 0))),

                      sg.Col([
                              [sg.Text('Node shape'),
                               sg.Combo(KNOWN_FIGURES, key=SHAPE, default_value=NETLOGO_FIGURE,
                                        tooltip='Node shape')],


                              [sg.Text('Node color'),
                               sg.Combo([RANDOM] + [color[0] for color in PYGAME_COLORS], key=COLOR,
                                        default_value=RANDOM,  tooltip='Node color')]])

                      ]

                    ]


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_World, 'Force test', gui_left_upper=graph_left_upper, gui_right_upper=graph_right_upper,
           agent_class=Graph_Node, clear=True, bounce=True, auto_setup=True)
