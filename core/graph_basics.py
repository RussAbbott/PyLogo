from pygame.color import Color
from pygame.draw import circle

import core.gui as gui
from core.agent import Agent
from core.gui import BLOCK_SPACING, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import link_exists
# noinspection PyUnresolvedReferences
from core.pairs import Pixel_xy, Velocity, center_pixel
from core.sim_engine import SimEngine
from core.utils import normalize_dxdy
from core.world_patch_block import World


class Basic_Graph_Node(Agent):

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
        d = max(1, pixel_a.distance_to(pixel_b, wrap=False))
        if repulsive:
            dist = max(1, pixel_a.distance_to(pixel_b, wrap=False) / screen_distance_unit)
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

    def lnk_nbrs(self):
        lns = [(lnk, lnk.other_side(self)) for lnk in World.links if lnk.includes(self)]
        return lns


class Basic_Graph_World(World):

    ...



if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_World, 'Force test', agent_class=Graph_Node, clear=True, bounce=True, auto_setup=True)
