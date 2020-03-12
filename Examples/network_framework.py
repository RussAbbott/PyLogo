
from math import sqrt
from random import choice, sample, uniform
from typing import Tuple

from pygame.color import Color
from pygame.draw import circle

from core.agent import Agent, PYGAME_COLORS
import core.gui as gui
from core.gui import BLOCK_SPACING, HOR_SEP, KNOWN_FIGURES, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import Link, link_exists
from core.pairs import center_pixel, Pixel_xy, Velocity
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Network_Node(Agent):

    def __init__(self, **kwargs):
        color = SimEngine.gui_get('color')
        color = Color(color) if color != 'Random' else None
        shape_name = SimEngine.gui_get('shape')
        kwargs['shape_name'] = shape_name
        super().__init__(color=color, **kwargs)
        # Is the  node selected?
        self.selected = False

    def __str__(self):
        return f'FLN-{self.id}'

    def adjust_distances(self, velocity_adjustment):
        dist_unit = SimEngine.gui_get(('dist_unit'))
        screen_distance_unit = sqrt(SCREEN_PIXEL_WIDTH()**2 + SCREEN_PIXEL_HEIGHT()**2)/dist_unit

        repulsive_force: Velocity = Velocity((0, 0))

        for agent in (World.agents - {self}):
            repulsive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
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
        for agent in (World.agents - {self}):
            if link_exists(self, agent):
                attractive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
                                                         repulsive=False)

        net_force = repulsive_force + repulsive_wall_force + attractive_force
        normalized_force: Velocity = net_force/max([net_force.x, net_force.y, velocity_adjustment])
        normalized_force *= 10

        if SimEngine.gui_get('Print force values'):
            print(f'{self}. \n'
                  f'rep-force {tuple(repulsive_force.round(2))}; \n'
                  f'rep-wall-force {tuple(repulsive_wall_force.round(2))}; \n'
                  f'att-force {tuple(attractive_force.round(2))}; \n'
                  f'net-force {tuple(net_force.round(2))}; \n'
                  f'normalized_force {tuple(normalized_force.round(2))}; \n\n'
                  )

        self.set_velocity(normalized_force)
        self.forward()

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
        d = pixel_a.distance_to(pixel_b, wrap=False)
        if repulsive:
            dist = max(1, pixel_a.distance_to(pixel_b, wrap=False) / screen_distance_unit)
            rep_coefficient = SimEngine.gui_get('rep_coef')
            rep_exponent = SimEngine.gui_get('rep_exponent')
            force = direction * (10**rep_coefficient)/10 * dist**rep_exponent
            return force
        else:  # attraction
            dist = max(1, max(d, screen_distance_unit) / screen_distance_unit)
            att_exponent = SimEngine.gui_get('att_exponent')
            force = direction*dist**att_exponent
            # If the link is too short, push away instead of attracting.
            if d < screen_distance_unit:
                force = force*(-1)
            att_coefficient = SimEngine.gui_get('att_coef')
            return 10**(att_coefficient-1) * force

    def neighbors(self):
        lns = [(lnk, lnk.other_side(self)) for lnk in World.links if lnk.includes(self)]
        return lns


class Network_World(World):

    def __init__(self, patch_class, agent_class):
        self.velocity_adjustment = 1
        super().__init__(patch_class, agent_class)
        self.shortest_path_links = None
        self.selected_nodes = set()
        self.disable_enable_buttons()

    def build_graph(self):
        """
        Arrange all the nodes (or all but one) as a ring.
        Then link them depending on the kind of network desired.
        """
        nbr_nodes = SimEngine.gui_get('nbr_nodes')
        graph_type = SimEngine.gui_get('graph type')

        # If we are generating a star or a wheel network, arrange nbr_nodes-1 as
        # a ring and use the other node as the center node.

        # If we are generating a ring or a random network, arrange all the nodes as a ring.

        ring_nodes = (nbr_nodes - 1) if graph_type in ['star', 'wheel'] else nbr_nodes

        # create_ordered_agents() creates the indicated number of nodes and arranges them in a ring.
        # It also returns a list of the nodes in ring-order.
        ring_node_list = self.create_ordered_agents(ring_nodes)

        # Now link the nodes according to the desired graph.
        self.generate_graph(graph_type, ring_node_list)

    def compute_metrics(self):
        clust_coefficient = self.clustering_coefficient()
        SimEngine.gui_set('cluster_coeff', value=clust_coefficient)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set('path_length', value=avg_path_length)

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        return 'TBD'

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return 'TBD'

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
        node_set_1 = sample(World.agents, len(World.agents))
        while not link_created:
            node_1 = node_set_1.pop()
            # Since node_1 has been popped from node_set_1,
            # node_set_2 does not contain node_1.
            node_set_2 = sample(node_set_1, len(node_set_1))
            while node_set_2:
                node_2 = node_set_2.pop()
                if not link_exists(node_1, node_2):
                    Link(node_1, node_2)
                    link_created = True
                    break

    def delete_a_shortest_path_link(self):
        # Look for a link to delete so that there is still some path.
        link_deleted = False
        for lnk in self.shortest_path_links:
            World.links.remove(lnk)
            # self.shortest_path() will return either a shortest path or None.
            # If it returns a shortest path, the link we deleted is ok to delete.
            if self.shortest_path():
                link_deleted = True
                break
            else:
                # Deleting lnk prevents any path. Put it back and try another one.
                World.links.add(lnk)
        # At this point we have either found and deleted a link or not.
        # If we have found a link to delete, i.e., link_deleted is True, we're done.
        # Otherwise delete a random link in the shortest path.
        if not link_deleted:
            # Select a random link and delete it.
            lnk = choice(self.shortest_path_links)
            World.links.remove(lnk)

    def disable_enable_buttons(self):
        # 'enabled' is a pseudo attribute. gui.gui_set replaces it with 'disabled' and negates the value.

        SimEngine.gui_set('Delete random node', enabled=bool(World.agents))

        SimEngine.gui_set('Delete random link', enabled=bool(World.links))
        SimEngine.gui_set('Create random link', enabled=len(World.links) < len(World.agents)*(len(World.agents)-1)/2)

        SimEngine.gui_set('Delete shortest-path link', enabled=self.shortest_path_links)

        # Show node id's if requested.
        show_labels = SimEngine.gui_get("Show node id's")
        for node in World.agents:
            node.label = str(node.id) if show_labels else None

    @staticmethod
    def generate_graph(graph_type, ring_node_list):
        pass

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle color change requests.
        super().handle_event(event)

        # Handle link/node creation/deletion request events.
        if event == 'Create node':
            self.agent_class()
        elif event == 'Delete random node':
            agent = sample(self.agents, 1)[0]
            agent.delete()
        elif event == 'Create random link':
            self.create_random_link()
        elif event == 'Delete random link':
            World.links.pop()
        elif event == 'Delete shortest-path link':
            self.delete_a_shortest_path_link()

        self.disable_enable_buttons()

    def mouse_click(self, xy: Tuple[int, int]):
        """ Select closest node. """
        patch = self.pixel_tuple_to_patch(xy)
        if len(patch.agents) == 1:
            node = choice(list(patch.agents))
        else:
            patches = patch.neighbors_24()
            nodes = {node for patch in patches for node in patch.agents}
            node = nodes.pop() if nodes else Pixel_xy(xy).closest_block(World.agents)
        if node:
            node.selected = not node.selected

    def setup(self):
        self.build_graph()
        self.compute_metrics()
        self.disable_enable_buttons()

    def shortest_path(self):
        (node1, node2) = self.selected_nodes
        # Start with the node with the smaller number of neighbors.
        if len(node1.neighbors()) > len(node2.neighbors()):
            (node1, node2) = (node2, node1)
        visited = {node1}
        # A path is a sequence of tuples (link, node) where the link
        # attaches to the node preceding it and in its tuple.
        # The first tuple in a path starts with a None link since
        # there is no preceding node.

        # The frontier is a list of paths, shortest first.
        frontier = [[(None, node1)]]
        while frontier:
            current_path = frontier.pop(0)
            # The neighbors are tuples as in the paths. For a given node
            # they are all the nodes links along with the nodes linked to.
            # This is asking for the last node in the current path,
            last_node = current_path[-1][1]
            # This gets all the non-visited neighbors of the last node.
            # Each neighbor is a (link, node) pair.
            neighbors = [neighbor for neighbor in last_node.neighbors() if neighbor[1] not in visited]
            # Do any of these continuations reach the target, node_2? If so, we've found the shortest path.
            lnks_to_node_2 = [neighbor for neighbor in neighbors if neighbor[1] == node2]
            # If lnks_to_node_2 is non-empty it will have one element: (lnk, node_2)
            if lnks_to_node_2:
                path = current_path + lnks_to_node_2
                # Extract the links, but drop the None at the beginning.
                lnks = [neighbor[0] for neighbor in path[1:]]
                return lnks
            # Not done. Add the newly reached nodes to visted.
            visited |= {neighbor[1] for neighbor in neighbors}
            # For each neighbor construct an extended version of the current path.
            extended_paths = [current_path + [neighbor] for neighbor in neighbors]
            # Add all those extended paths to the frontier.
            frontier += extended_paths

        # If we get out of the loop because the frontier is empty, there is no path from node_1 to node_2.
        return None

    def step(self):
        for node in self.agents:
            node.adjust_distances(self.velocity_adjustment)

        # Set all the links back to normal.
        for lnk in World.links:
            lnk.color = lnk.default_color
            lnk.width = 1

        self.selected_nodes = [node for node in self.agents if node.selected]
        # If there are exactly two selected nodes, find the shortest path between them.
        if len(self.selected_nodes) == 2:
            self.shortest_path_links = self.shortest_path()
            # self.shortest_path_links will be either a list of links or None
            # If there is a path, highlight it.
            if self.shortest_path_links:
                for lnk in self.shortest_path_links:
                    lnk.color = Color('red')
                    lnk.width = 2

        # Update which buttons are enabled.
        self.disable_enable_buttons()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

tt = 'Probability that two nodes in a random graph will be linked\n' \
     'or that a link in a small world graph will be rewired'

network_left_upper = [
                    [
                     sg.Button('Create random link', tooltip='Create a random link', pad=((0, 10), (5, 0))),
                     sg.Col([[sg.Button('Delete random link', tooltip='Delete a random link',
                                        pad=((10, 10), (5, 0)))],
                             [sg.Button('Delete shortest-path link',
                                        tooltip='Delete a random link on the shortest path',
                                        pad=((0, 0), (5, 0)))]])
                     ],

                    HOR_SEP(pad=((50, 0), (0, 0))),

                     [sg.Text('Graph type', pad=((0, 10), (20, 0))),
                      sg.Combo(['lattice', 'pref attachment', 'random', 'ring', 'small world', 'star', 'wheel'],
                               key='graph type', pad=((10, 0), (20, 0)), default_value='ring', tooltip='graph type')],

                    [sg.Text('Random graph link prob\nSmall world rewire prob', pad=((0, 10), (20, 0)),
                             tooltip=tt),
                     sg.Slider((0, 100), default_value=10, orientation='horizontal', key='link_prob',
                               size=(10, 20), pad=((0, 0), (10, 0)),
                               tooltip=tt)],

                    [sg.Text('Clustering coeff', pad=(None, (20, 0))),
                     sg.Text('None', background_color='white', text_color='black', key='cluster_coeff',
                             pad=((5, 0), (20, 0))),
                     sg.Text('Avg path length', pad=((20, 0), (20, 0))),
                     sg.Text('None', background_color='white', text_color='black', key='path_length',
                             pad=((5, 0), (20, 0)))],

                    HOR_SEP(pad=((50, 0), (0, 0))),

                    [sg.Text('Repulsion coefficient', pad=((0, 10), (20, 0)),
                             tooltip='Negative means raise to the power and divide (like gravity).\n'
                                     'Larger magnitude means distince reduces repulsive force more.'),
                     sg.Slider((1, 5), default_value=1, orientation='horizontal', key='rep_coef',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Larger is stronger.')],

                    [sg.Text('Repulsion exponent', pad=((0, 10), (20, 0)),
                             tooltip='Negative means raise to the power and divide (like gravity).\n'
                                     'Larger magnitude means distince reduces repulsive force more.'),
                     sg.Slider((-5, -1), default_value=-2, orientation='horizontal', key='rep_exponent',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Negative means raise to the power and divide (like gravity).\n'
                                       'Larger magnitude means distince reduces repulsive force more.')],

                    [sg.Text('Attraction coefficient', pad=((0, 10), (20, 0)),
                             tooltip='If > distance unit, larger magnitude means \n'
                                     'increase force more with distance (like a spring)\n'
                                     'If < distance unit, force becomes repulsive (also like a spring)'),
                     sg.Slider((1, 6), default_value=1, orientation='horizontal', key='att_coef',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='If distance > distance unit, larger magnitude means \n'
                                       'increase force more with distance (like a spring)\n'
                                       'If distance < distance unit, force becomes repulsive (also like a spring)')],

                    [sg.Text('Attraction exponent', pad=((0, 10), (20, 0)),
                             tooltip='If > distance unit, larger magnitude means \n'
                                     'increase force more with distance (like a spring)\n'
                                     'If < distance unit, force becomes repulsive (also like a spring)'),
                     sg.Slider((0, 10), default_value=2, orientation='horizontal', key='att_exponent',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='If distance > distance unit, larger magnitude means \n'
                                       'increase force more with distance (like a spring)\n'
                                       'If distance < distance unit, force becomes repulsive (also like a spring)')],

                    [sg.Text('Distance unit/ideal link length', pad=((0, 10), (20, 0)),
                             tooltip='The fraction of the screen diagonal used as one unit.'),
                     sg.Slider((3, 16), default_value=8, orientation='horizontal', key='dist_unit',
                               resolution=1, pad=((0, 0), (0, 0)), size=(10, 20),
                               tooltip='The fraction of the screen diagonal used as one unit.')],

                    [
                     sg.Checkbox("Show node id's", key="Show node id's", default=False, pad=((20, 0), (20, 0))),
                     sg.Checkbox('Print force values', key='Print force values', default=False, pad=((20, 0), (20, 0)))
                     ],

                   ]
network_right_upper = [
                     [
                      sg.Col([
                              [sg.Button('Create node', tooltip='Create a node'),
                               sg.Button('Delete random node', tooltip='Delete one random node')],

                              [sg.Text('Click two nodes for shortest path')]],
                              pad=((0, 0), None)),

                      sg.Col([
                              [sg.Text('Nodes', pad=((0, 0), (15, 0))),
                               sg.Slider((0, 20), default_value=9, orientation='horizontal', key='nbr_nodes',
                                         size=(10, 20), tooltip='Nbr of agents created by setup')],
                              # [sg.Text('Nbr of nodes', pad=((0, 0), (20, 0))),
                              #  sg.Slider((0, 20), default_value=9, orientation='horizontal', key='nbr_nodes',
                              #            size=(10, 20), tooltip='Nbr of agents created by setup')]
                              ], pad=((0, 0), (5, 0))),

                      sg.Col([
                              [sg.Text('Node shape'),
                               sg.Combo(KNOWN_FIGURES, key='shape', default_value='netlogo_figure',
                                        tooltip='Node shape')],


                              [sg.Text('Node color'),
                               sg.Combo(['Random'] + [color[0] for color in PYGAME_COLORS], key='color',
                                        default_value='Random',  tooltip='Node color')]])

                      ]

                    ]


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Network_World, 'Force test', gui_left_upper=network_left_upper, gui_right_upper=network_right_upper,
           agent_class=Network_Node,  bounce=True)
