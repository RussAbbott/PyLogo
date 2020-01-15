
from math import atan2, pi, sqrt

import pygame as pg
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame import Surface
from pygame.math import Vector2
import pygame.transform as pgt

# noinspection PyUnresolvedReferences
import PyLogo.core.agent as agent
import PyLogo.core.gui as gui
from PyLogo.core.gui import HALF_PATCH_SIZE, PATCH_SIZE
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils
from PyLogo.core.utils import V2
from PyLogo.core.world_patch_block import Block, Patch, World

from random import choice, randint

from typing import Tuple


def is_acceptable_color(rgb: Tuple[int, int, int]):
    """
    Require reasonably bright colors for which r, g, and b are not too close to each other.
    """
    sum_rgb = sum(rgb)
    avg_rgb = sum_rgb/3
    return 150 <= sum_rgb and sum(abs(avg_rgb-x) for x in rgb) > 100


# These are colors defined by pygame that satisfy is_acceptable_color above.
PYGAME_COLORS = [rgba for rgba in THECOLORS.values() if is_acceptable_color(rgba[:3])]

# These are NetLogo primary colors.
NETLOGO_PRIMARY_COLORS = [Color('gray'), Color('red'), Color('orange'), Color('brown'), Color('yellow'),
                          Color('green'), Color('limegreen'), Color('turquoise'), Color('cyan'),
                          Color('skyblue3'), Color('blue'), Color('violet'), Color('magenta'), Color('pink')]

# noinspection PyArgumentList
SHAPES = {'netlogo_figure': ((V2(1, 1), V2(0.5, 0), V2(0, 1), V2(0.5, 3/4)),
                             [])}


class Agent(Block):

    color_palette = choice([NETLOGO_PRIMARY_COLORS, PYGAME_COLORS])

    id = 0

    SQRT_2 = sqrt(2)

    def __init__(self, center_pixel=None, color=None, scale=1.4, shape=agent.SHAPES['netlogo_figure'][0]):
        # Can't make this a default value because utils.CENTER_PIXEL() isn't defined
        # when the default values are compiled
        if center_pixel is None:
            center_pixel = utils.CENTER_PIXEL()

        if color is None:
            # Select a color at random from the color_palette
            # Agent.color_palette is set during World.setup().
            color = choice(Agent.color_palette)

        super().__init__(center_pixel, color)

        self.scale = scale
        self.shape = shape
        self.base_image = self.create_base_image()

        Agent.id += 1
        self.id = Agent.id
        self.the_world().agents.add(self)
        self.current_patch().add_agent(self)
        self.heading = randint(0, 360)
        self.speed = 1
        # To keep PyCharm happy.
        self.velocity = None

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}-{self.id}@{(self.center_pixel.round(2))}: heading: {round(self.heading, 2)}'

    def bounce_off_screen_edge(self, dxdy):
        """
       Bounce agent off the screen edges
       """
        sc_rect = gui.simple_gui.SCREEN.get_rect()
        center_pixel = self.center_pixel
        next_center_pixel = center_pixel + dxdy
        if next_center_pixel.x <= sc_rect.left <= center_pixel.x or \
            center_pixel.x <= sc_rect.right <= next_center_pixel.x:
            dxdy = utils.Velocity(dxdy.dx*(-1), dxdy.dy)

        if next_center_pixel.y <= sc_rect.top <= center_pixel.y or \
            center_pixel.y <= sc_rect.bottom <= next_center_pixel.y:
            dxdy = utils.Velocity(dxdy.dx, dxdy.dy*(-1))

        return dxdy

    def create_base_image(self):
        base_image = self.create_blank_base_image()

        # Instead of using pgt.smoothscale to scale the image, scale the polygon instead.
        scaled_shape = [(v2 * self.scale*PATCH_SIZE).as_tuple() for v2 in self.shape]
        pg.draw.polygon(base_image, self.color, scaled_shape)
        return base_image

    def create_blank_base_image(self):
        # Give the agent a larger Surface (by sqrt(2)) to work with since it may rotate.
        blank_base_image = Surface((self.rect.w * Agent.SQRT_2, self.rect.h * Agent.SQRT_2))
        blank_base_image = blank_base_image.convert_alpha()
        blank_base_image.fill((0, 0, 0, 0))
        return blank_base_image

    def create_image_to_draw(self):
        new_points = [self.map_point(utils.V_to_PV(pt)) for pt in self.shape]
        base_image = self.create_blank_base_image()
        pg.draw.polygon(base_image, self.color, new_points)
        return base_image

    def current_patch(self) -> Patch:
        row_col: utils.RowCol = utils.center_pixel_to_row_col(self.center_pixel)
        patch = self.the_world().patches[row_col.row, row_col.col]
        return patch

    def distance_to(self, other):
        screen_width_half = gui.SCREEN_PIXEL_WIDTH()/2
        screen_height_half = gui.SCREEN_PIXEL_HEIGHT()/2
        end_pts = [(self.center_pixel + a + b, other.center_pixel + a + b)
                   for a in [utils.PixelVector(0, 0), utils.PixelVector(screen_width_half, 0)]
                   for b in [utils.PixelVector(0, 0), utils.PixelVector(0, screen_height_half)]
                   ]
        dist = min(start.distance_to(end) for (start, end) in end_pts)
        return dist


    def draw(self):

        self.image = pgt.rotate(self.base_image, -self.heading)

        # Should probably rotate and scale the shape here as in the following, but it doesn't work properly.
        # self.image = self.create_image_to_draw()

        self.rect = self.image.get_rect(center=self.center_pixel.as_tuple())
        super().draw()
        
    def face_xy(self, xy: utils.PixelVector):
        new_heading = utils.heading_from_to(self.center_pixel, xy)
        self.set_heading(new_heading)

    def forward(self, speed=None):
        if speed is None:
            speed = self.speed
        dxdy = utils.heading_to_dxdy(self.heading) * speed
        self.move_by_dxdy(dxdy)

    def heading_toward(self, target):
        """ The heading to face the target """
        from_pixel = self.center_pixel
        to_pixel = target.center_pixel
        return utils.heading_from_to(from_pixel, to_pixel)

    def map_point(self, pxl: utils.PixelVector) -> Vector2:
        abstract_center_pixel = utils.PixelVector(1/2, 1/2)
        homed_pxl = pxl - abstract_center_pixel
        rot_home_p = homed_pxl.rotate(self.heading)
        restored_pxl = rot_home_p + abstract_center_pixel
        return restored_pxl

    def move_by_dxdy(self, dxdy: utils.Velocity):
        """
        Move to self.center_pixel + (dx, dy)
        """
        if self.get_gui_value('Bounce?'):
            new_dxdy = self.bounce_off_screen_edge(dxdy)
            if dxdy is self.velocity:
                self.set_velocity(new_dxdy)
            dxdy = new_dxdy
        self.move_to_xy(self.center_pixel + dxdy)

    def move_by_velocity(self):
        self.move_by_dxdy(self.velocity)

    def move_to_patch(self, patch):
        self.move_to_xy(patch.center_pixel)

    def move_to_xy(self, xy: utils.PixelVector):
        """
        Remove this agent from the list of agents at its current patch.
        Move this agent to its new xy center_pixel.
        Add this agent to the list of agents in its new patch.
        """
        current_patch: Patch = self.current_patch()
        current_patch.remove_agent(self)
        self.set_center_pixel(xy)
        new_patch = self.current_patch( )
        new_patch.add_agent(self)

    def set_center_pixel(self, xy: utils.PixelVector):
        self.center_pixel: utils.PixelVector = xy.wrap()
        r = self.rect
        (r.x, r.y) = (self.center_pixel.x - HALF_PATCH_SIZE(), self.center_pixel.y - HALF_PATCH_SIZE())

    def set_color(self, color):
        self.color = color
        self.base_image = self.create_base_image()

    def set_heading(self, heading):
        self.heading = heading

    @staticmethod
    def heading_from_to(from_pixel, xy):
        """ The heading to face the point (x, y) """
        delta_x = xy.x - from_pixel.x
        # Subtract in reverse to compensate for the reversal of the y axis.
        delta_y = from_pixel.y - xy.y
        atn2 = atan2(delta_y, delta_x)
        angle = (atn2 / (2 * pi) ) * 360
        new_heading = utils.angle_to_heading(angle)
        return new_heading

    def turn_left(self, delta_angles):
        self.turn_right(-delta_angles)

    def turn_right(self, delta_angles):
        self.set_heading(utils.normalize_angle_360(self.heading + delta_angles))

    def set_velocity(self, velocity):
        self.velocity = velocity
        self.face_xy(self.center_pixel + velocity)


class Turtle(Agent):
    pass


def PyLogo(world_class=World, caption=None, gui_elements=None,
           agent_class=Agent, patch_class=Patch,
           patch_size=11, bounce=True):
    if gui_elements is None:
        gui_elements = []
    if caption is None:
        caption = utils.extract_class_name(world_class)
    sim_engine = SimEngine(gui_elements, caption=caption, patch_size=patch_size, bounce=bounce)
    sim_engine.start(world_class, patch_class, agent_class)



if __name__ == '__main__':
    # noinspection PyArgumentList
    v = Vector2(1, 1)
    v1 = v.rotate(45)
    print(v1)
