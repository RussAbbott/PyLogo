
from copy import copy
from math import sqrt
from random import randint, sample, uniform

from core.agent import Agent
from core.gui import HOR_SEP, KNOWN_FIGURES, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import Link, link_exists
from core.pairs import Pixel_xy
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Force_Layout_Node(Agent):

    def __init__(self, **kwargs):
        shape_name = SimEngine.gui_get('shape')
        super().__init__(shape_name=shape_name, **kwargs)
        self.forward(randint(50, 300))
        # If there are any (other) agents, create links to them with probability 0.25.
        agents = World.agents - {self}
        if agents:
            self.make_links(agents)

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

        self.move_by_dxdy(normalized_force*10)

    def delete(self):
        World.agents.remove(self)
        World.links -= {lnk for lnk in World.links if lnk.includes(self)}

    @staticmethod
    def force_as_dxdy(this, other, screen_diagonal_div_10, repulsive=True):
        direction = normalize_dxdy((this - other) if repulsive else (other - this))
        d = this.distance_to(other, wrap=False)
        if repulsive:
            dist = max(1, this.distance_to(other, wrap=False) / screen_diagonal_div_10)
            rep_exponent = SimEngine.gui_get('rep_exponent')
            return direction * dist**rep_exponent
        else:  # attraction
            dist = max(1, max(d, screen_diagonal_div_10) / screen_diagonal_div_10)
            att_exponent = SimEngine.gui_get('att_exponent')
            force = direction*dist**att_exponent
            if d < screen_diagonal_div_10:
                force = force*(-1)
            return force

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

    @staticmethod
    def disable_enable_buttons():
        # 'enabled' is a pseudo attribute. gui.gui_set replaces it with 'disabled' and negates the value.

        SimEngine.gui_set('Delete random node', enabled=bool(World.agents))

        SimEngine.gui_set('Delete random link', enabled=bool(World.links))
        SimEngine.gui_set('Create random link', enabled=len(World.links) < len(World.agents)*(len(World.agents)-1)/2)


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
        elif event == 'Delete random link':
            lnk = sample(World.links, 1)[0]
            World.links.remove(lnk)

        self.disable_enable_buttons()
        # SimEngine.gui_set('Delete random node', disabled=not bool(World.agents))

    def setup(self):
        # SimEngine.gui_set('Create node', disabled=False)
        nbr_nodes = SimEngine.gui_get('nbr_nodes')
        for _ in range(nbr_nodes):
            self.agent_class()
        self.disable_enable_buttons()

        # SimEngine.gui_set('Delete random node', disabled=not bool(World.agents))

    def step(self):
        for agent in self.agents:
            agent.adjust_distances(self.max_motion)
        self.disable_enable_buttons()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

force_upper_left = [
                    [
                     sg.Text('Node shape'),
                     sg.Combo(KNOWN_FIGURES, key='shape', default_value='node', tooltip='Node shape')],

                    HOR_SEP(pad=(None, (0, 0))),

                    [
                     sg.Button('Create node', tooltip='Create a node'),
                     sg.Button('Delete random node', tooltip='Delete one random node')
                     ],

                    HOR_SEP(pad=(None, (0, 0))),

                    [
                     sg.Button('Create random link', tooltip='Create one node'),
                     sg.Button('Delete random link', tooltip='Delete one random node')
                     ],

                    HOR_SEP(pad=(None, (0, 0))),

                    [sg.Text('Repulsion exponent', pad=((0, 10), (20, 0)),
                             tooltip='Negative means raise to the power and divide (like gravity).\n'
                                     'Larger magnitude means distince reduces repulsive force more.'),
                     sg.Slider((-5, -1), default_value=-2, orientation='horizontal', key='rep_exponent',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Negative means raise to the power and divide (like gravity).\n'
                                       'Larger magnitude means distince reduces repulsive force more.')],

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
                     sg.Slider((6, 18), default_value=10, orientation='horizontal', key='dist_unit',
                               resolution=2, pad=((0, 0), (0, 0)), size=(10, 20),
                               tooltip='The fraction of the screen diagonal used as one unit.')],

                    HOR_SEP(),

                    [sg.Text('Click "Setup and then "Go" for force computation.', pad=((0, 0), (0, 0)))],
                    [sg.Text('Nbr of nodes', pad=((0, 10), (20, 0))),
                     sg.Slider((0, 20), default_value=7, orientation='horizontal', key='nbr_nodes',
                               pad=((0, 0), (0, 0)), size=(15, 20),
                               tooltip='Nbr of agents created by setup')],

                    [sg.Checkbox('Print force values', key='Print force values', default=False,
                                 pad=((0, 0), (20, 0)))]
                    ]



if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Force_Layout_World, 'Force test', force_upper_left, agent_class=Force_Layout_Node)
