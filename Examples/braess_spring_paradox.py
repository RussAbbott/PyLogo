from math import copysign, sqrt

from pygame.color import Color

# Import the string constants you will need (mainly keys but also values such as the graph types)
# as well as the classes and gui elements
from Examples.network_framework import (DIST_UNIT, Graph_Node, NODE,
                                        network_left_upper, network_right_upper)
from Examples.network_framework import Graph_World
from core.gui import SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import Link
from core.pairs import Pixel_xy
from core.sim_engine import SimEngine
from core.world_patch_block import World


class Braess_Link(Link):

    def __init__(self, node_1, node_2, length=None, stretchy=True, **kwargs):
        super().__init__(node_1, node_2, **kwargs)
        # This is the resting length
        self.length = length if length else Braess_World.dist_unit
        self.stretchy = stretchy
        self.agent_2.center_pixel = Pixel_xy((self.agent_2.center_pixel.x, self.agent_1.center_pixel.y + self.length))

    def adjust_length(self):
        actual_length = self.agent_1.distance_to(self.agent_1)
        discrepancy = self.proper_length() - actual_length
        discrepancy = copysign(min(10, abs(discrepancy)), discrepancy)
        center_pixel = self.agent_2.center_pixel
        print(f'{self}: {center_pixel} -> ', end='')
        self.agent_2.move_to_xy(center_pixel)
        print(f'{center_pixel}')
        self.agent_2.center_pixel = Pixel_xy((center_pixel.x, center_pixel.y + discrepancy))

    def draw(self):
        too_long = self.agent_1.distance_to(self.agent_2) > self.proper_length()
        self.color = Color( 'white' if not self.stretchy else 'red' if too_long else 'green' )
        self.width = 1 if not self.stretchy else 4 if too_long else 2
        super().draw()

    def proper_length(self):
        divisor = len(Braess_World.weight.lnk_nbrs())
        prpr_len = self.length + (0 if not self.stretchy else Braess_World.mass / divisor)
        return prpr_len


class Braess_Node(Graph_Node):

    def __init__(self, location, pinned=False, shape_name=NODE, **kwargs):
        kwargs['color'] = Color('black')
        super().__init__(shape_name=shape_name, **kwargs)
        self.pinned = pinned
        self.move_to_xy(location)


class Braess_World(Graph_World):

    dist_unit = None
    mass = None
    weight = None

    def __init__(self, patch_class, agent_class):
        super().__init__(patch_class, agent_class)

        dist_factor = SimEngine.gui_get(DIST_UNIT)/1
        Braess_World.dist_unit = int(sqrt(SCREEN_PIXEL_WIDTH() ** 2 + SCREEN_PIXEL_HEIGHT() ** 2) / dist_factor)
        Braess_World.mass = Braess_World.dist_unit / 2

        x_offset = 50
        x_x = int(SCREEN_PIXEL_WIDTH()/2) + x_offset

        # screen_height = SCREEN_PIXEL_HEIGHT()

        # This is what setup would normally do. But we're doing it here to avoid
        # having to declare these variables here and then define them in setup.
        self.top_spring_node_1 = Braess_Node(Pixel_xy( (x_x, 50) ), pinned=True)
        self.top_spring_node_2 = Braess_Node(Pixel_xy( (x_x, 50 + Braess_World.dist_unit) ) )
        self.top_spring = Braess_Link(self.top_spring_node_1, self.top_spring_node_2)

        self.bottom_spring_node_1 = Braess_Node(Pixel_xy( (x_x,
                                                           self.top_spring_node_2.center_pixel.y +
                                                           Braess_World.dist_unit/2) ) )
        self.bottom_spring_node_2 = Braess_Node(Pixel_xy( (x_x,
                                                           self.bottom_spring_node_1.center_pixel.y +
                                                           Braess_World.dist_unit) ) )

        Braess_World.weight = self.bottom_spring_node_2

        self.string = Braess_Link(self.top_spring_node_2, self.bottom_spring_node_1,
                                  stretchy=False, length=Braess_World.dist_unit/3)

        self.bottom_spring = Braess_Link(self.bottom_spring_node_1, self.bottom_spring_node_2)

    def setup(self):
        """ Need this to override setup in network_framework """
        ...

    def step(self):
        print()
        for lnk in World.links:
            lnk.adjust_length()


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Braess_World, 'Network test', gui_left_upper=network_left_upper,
           gui_right_upper=network_right_upper, agent_class=Braess_Node, clear=False, auto_setup=True)
