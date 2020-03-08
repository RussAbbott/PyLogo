
from copy import copy
from math import sqrt
from random import choice, randint, sample, uniform
from typing import Tuple

from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.draw import circle

from core.agent import Agent, PYGAME_COLORS
import core.gui as gui
from core.gui import BLOCK_SPACING, HOR_SEP, KNOWN_FIGURES, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import Link, link_exists
from core.pairs import Pixel_xy
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Force_Layout_Node(Agent):

    def __init__(self, **kwargs):
        shape_name = SimEngine.gui_get('shape')
        color = SimEngine.gui_get('color')
        color = Color(color) if color != 'Random' else None
        super().__init__(shape_name=shape_name, color=color, **kwargs)
        self.forward(randint(50, 300))
        # If there are any (other) agents, create links to them with probability 0.25.
        agents = World.agents - {self}
        if agents:
            self.make_links(agents)

    def __str__(self):
        return f'FLN-{self.id}'

    def adjust_distances(self, max_motion):
        dist_unit = SimEngine.gui_get(('dist_unit'))
        screen_diagonal_div_10 = sqrt(SCREEN_PIXEL_WIDTH()**2 + SCREEN_PIXEL_HEIGHT()**2)/dist_unit

        repulsive_force = Pixel_xy((0, 0))

        for agent in (World.agents - {self}):
            repulsive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_diagonal_div_10,
                                                  repulsive=True)

        # Also consider repulsive force from walls.
        repulsive_wall_force = Pixel_xy((0, 0))

        horizontal_walls = [Pixel_xy((0, 0)), Pixel_xy((SCREEN_PIXEL_WIDTH(), 0))]
        x_pixel = Pixel_xy((self.center_pixel.x, 0))
        for h_wall_pixel in horizontal_walls:
            repulsive_wall_force += self.force_as_dxdy(x_pixel, h_wall_pixel, screen_diagonal_div_10, repulsive=True)

        vertical_walls = [Pixel_xy((0, 0)), Pixel_xy((0, SCREEN_PIXEL_HEIGHT()))]
        y_pixel = Pixel_xy((0, self.center_pixel.y))
        for v_wall_pixel in vertical_walls:
            repulsive_wall_force += self.force_as_dxdy(y_pixel, v_wall_pixel, screen_diagonal_div_10, repulsive=True)

        attractive_force = Pixel_xy((0, 0))
        for agent in (World.agents - {self}):
            if link_exists(self, agent):
                attractive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_diagonal_div_10,
                                                       repulsive=False)

        net_force = repulsive_force + repulsive_wall_force + attractive_force
        normalized_force = net_force/max([net_force.x, net_force.y, max_motion])

        if SimEngine.gui_get('Print force values'):
            print(f'{self}. \n'
                  f'rep-force {tuple(repulsive_force.round(2))}; \n'
                  f'rep-wall-force {tuple(repulsive_wall_force.round(2))}; \n'
                  f'att-force {tuple(attractive_force.round(2))}; \n'
                  f'net-force {tuple(net_force.round(2))}; \n'
                  f'normalized_force {tuple(normalized_force.round(2))}; \n\n'
                  )

        self.set_velocity(normalized_force*10)
        self.forward()

    def delete(self):
        World.agents.remove(self)
        World.links -= {lnk for lnk in World.links if lnk.includes(self)}

    def draw(self, shape_name=None):
        super().draw(shape_name=shape_name)
        if self.highlight:
            radius = round((BLOCK_SPACING() / 2) * self.scale * 1.5)
            circle(gui.SCREEN, Color('red'), self.rect.center, radius, 1)

    @staticmethod
    def force_as_dxdy(this, other, screen_diagonal_div_10, repulsive=True):
        direction = normalize_dxdy((this - other) if repulsive else (other - this))
        d = this.distance_to(other, wrap=False)
        if repulsive:
            dist = max(1, this.distance_to(other, wrap=False) / screen_diagonal_div_10)
            rep_coefficient = SimEngine.gui_get('rep_coef')
            rep_exponent = SimEngine.gui_get('rep_exponent')
            return direction * (10**rep_coefficient)/10 * dist**rep_exponent
        else:  # attraction
            dist = max(1, max(d, screen_diagonal_div_10) / screen_diagonal_div_10)
            att_coef = SimEngine.gui_get('att_coef')
            att_exponent = SimEngine.gui_get('att_exponent')
            force = direction*dist**att_exponent
            if d < screen_diagonal_div_10:
                force = force*(-1)
            return int(round((10**att_coef)/10)) * force

    def lnk_nbrs(self):
        lns = [(lnk, lnk.other_side(self)) for lnk in World.links if lnk.includes(self)]
        return lns

    def make_links(self, agents):
        """
        Ceate links from self to existing nodes.
        """
        # Put agents (nodes) in random order.
        potential_partners = sample(agents, len(agents))
        # Build a generator that keeps with probability 0.25 potential partners without links to self
        gen = (agent for agent in potential_partners if uniform(0, 1) < 0.25 and not link_exists(self, agent))
        # Create a link with each of these partners.
        for partner in gen:
            Link(self, partner)


class Force_Layout_World(World):

    def __init__(self, patch_class, agent_class):
        # pixels per step
        self.max_motion = 5
        super().__init__(patch_class, agent_class)
        self.shortest_path_links = []
        self.disable_enable_buttons()

    @staticmethod
    def create_link():
        link_created = False
        agent_set_1 = sample(World.agents, len(World.agents))
        while not link_created:
            # pop selects a random element from a set and removes and returns it.
            agent_1 = agent_set_1.pop()
            agent_set_2 = sample(agent_set_1, len(agent_set_1))  
            while agent_set_2:
                agent_2 = agent_set_2.pop()
                if not link_exists(agent_1, agent_2):
                    Link(agent_1, agent_2)
                    link_created = True
                    break

    def disable_enable_buttons(self):
        # 'enabled' is a pseudo attribute. gui.gui_set replaces it with 'disabled' and negates the value.

        SimEngine.gui_set('Delete random node', enabled=bool(World.agents))

        SimEngine.gui_set('Delete random link', enabled=bool(World.links))
        SimEngine.gui_set('Create random link', enabled=len(World.links) < len(World.agents)*(len(World.agents)-1)/2)

        SimEngine.gui_set('Delete shortest-path link', enabled=self.shortest_path_links)

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and the change isn't handled by the system.
        The key of the widget that changed is in event.
        """
        # Handle color change requests.
        super().handle_event(event)

        # Handle rule nbr change events, either switches or rule_nbr slider
        if event == 'Create node':
            self.agent_class()
        elif event == 'Delete random node':
            agent = sample(self.agents, 1)[0]
            agent.delete()
        elif event == 'Create random link':
            self.create_link()
        elif event in ['Delete random link', 'Delete shortest-path link']:
            link_pool = World.links if event == 'Delete random link' else self.shortest_path_links
            lnk = sample(link_pool, 1)[0]
            World.links.remove(lnk)
            if event == 'Delete shortest-path link':
                self.shortest_path_links = []

        self.disable_enable_buttons()
        # SimEngine.gui_set('Delete random node', disabled=not bool(World.agents))

    def mouse_click(self, xy: Tuple[int, int]):
        """ Toggle clicked patch's aliveness. """
        patch = self.pixel_tuple_to_patch(xy)
        if len(patch.agents) == 1:
            node = choice(list(patch.agents))
        else:
            patches = patch.neighbors_24()
            nodes = {node for patch in patches for node in patch.agents}
            node = nodes.pop() if nodes else Pixel_xy(xy).closest_block(World.agents)
        if node:
            node.highlight = not node.highlight

    def setup(self):
        # SimEngine.gui_set('Create node', disabled=False)
        nbr_nodes = SimEngine.gui_get('nbr_nodes')
        for _ in range(nbr_nodes):
            self.agent_class()
        self.disable_enable_buttons()

    @staticmethod
    def shortest_path(node1, node2):
        visited = {node1}
        # A path is a sequence of tuples (link, node) where the link
        # attaches to the node preceding it and in its tuple.
        # The first tuple in a path starts with a None link since
        # there is no preceding node.

        # The frontier is a list of paths, shortest first.
        frontier = [[(None, node1)]]
        while frontier:
            current_path = frontier.pop(0)
            # The lnk_nbrs are tuples as in the paths. For a given node
            # they are all the nodes links along with the nodes linked to.
            # This is asking for the lnk_nbrs of the last node in the current path,
            # i.e., all the ways the current path can be continued.
            lnk_nbrs = [lnk_nbr for lnk_nbr in current_path[-1][1].lnk_nbrs() if lnk_nbr[1] not in visited]
            # Do any of these continuations reach the target, node_2? If so, we've found the shortest path.
            lnks_to_node_2 = [lnk_nbr for lnk_nbr in lnk_nbrs if lnk_nbr[1] == node2]
            # If lnks_to_node_2 is non-empty it will have one element: (lnk, node_2)
            if lnks_to_node_2:
                path = current_path + lnks_to_node_2
                # Extract the links, but drop the None at the beginning.
                lnks = [lnk_nbr[0] for lnk_nbr in path[1:]]
                for lnk in lnks:
                    lnk.color = Color('red')
                    lnk.width = 2
                return lnks
            # Not done. Add the newly reached nodes to visted.
            visited |= {lnk_nbr[1] for lnk_nbr in lnk_nbrs}
            # For each lnk_nbr construct an extended version of the current path.
            extended_paths = [current_path + [lnk_nbr] for lnk_nbr in lnk_nbrs]
            # Add all those extended paths to the frontier.
            frontier += extended_paths

        # If we get out of the loop because the frontier is empty, there is no path from node_1 to node_2.
        return None

    def step(self):
        for node in self.agents:
            node.adjust_distances(self.max_motion)

        # Put all the links back to normal.
        for lnk in World.links:
            lnk.color = lnk.default_color
            lnk.width = 1

        selected_nodes = [node for node in self.agents if node.highlight]
        # If there are two selected nodes, find the shortest path between them.
        if len(selected_nodes) == 2:
            self.shortest_path_links = self.shortest_path(*selected_nodes)

        # Update which buttons are enabled.
        self.disable_enable_buttons()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

force_left_upper = [
                    [
                     sg.Button('Create random link', tooltip='Create a random link', pad=((0, 10), (5, 0))),
                     sg.Col([[sg.Button('Delete random link', tooltip='Delete a random link',
                                        pad=((10, 10), (5, 0)))],
                             [sg.Button('Delete shortest-path link',
                                        tooltip='Delete a random link on the shortest path',
                                        pad=((0, 0), (5, 0)))]])
                     ],

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
                     sg.Slider((3, 16), default_value=10, orientation='horizontal', key='dist_unit',
                               resolution=1, pad=((0, 0), (0, 0)), size=(10, 20),
                               tooltip='The fraction of the screen diagonal used as one unit.')],

                    HOR_SEP(pad=((50, 0), (0, 0))),

                    [sg.Text('Click "Setup and then "Go" for force computation.', pad=((0, 0), (0, 0)))],
                    [sg.Text('Nbr of nodes', pad=((0, 10), (20, 0))),
                     sg.Slider((0, 20), default_value=7, orientation='horizontal', key='nbr_nodes',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Nbr of agents created by setup')],

                    [sg.Checkbox('Print force values', key='Print force values', default=False,
                                 pad=((0, 0), (20, 0)))]
                    ]


force_right_upper = [
                     [
                      sg.Col([
                              [sg.Button('Create node', tooltip='Create a node'),
                               sg.Button('Delete random node', tooltip='Delete one random node')]
                              ],
                             pad=((80, 20), None)),

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
    PyLogo(Force_Layout_World, 'Force test', gui_left_upper=force_left_upper, gui_right_upper=force_right_upper,
           agent_class=Force_Layout_Node,  bounce=True)
