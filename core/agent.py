from math import atan2, cos, pi, sin

import pygame as pg
from pygame.color import Color
from pygame.colordict import THECOLORS
import pygame.transform as pgt

import PyLogo.core.world_patch_block as wpb
from PyLogo.core.world_patch_block import Block, Patch
import PyLogo.core.gui as gui
import PyLogo.core.utils as utils

from random import choice

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


class Agent(Block):

    color_palette = choice([NETLOGO_PRIMARY_COLORS, PYGAME_COLORS])

    id = 0

    def __init__(self, center_pixel: utils.PixelVector = None, color=None, scale=1.4):
        if color is None:
            # Select a color at random from the color_palette
            # Agent.color_palette is set during World.setup().
            color = choice(Agent.color_palette)

        # Can't make this a default value because utils.CENTER_PIXEL() isn't defined
        # when the default values are compiled
        if center_pixel is None:
            center_pixel = utils.CENTER_PIXEL()

        super().__init__(center_pixel, color)
        # self.original_image = Surface((self.rect.w, self.rect.h)).convert_alpha()
        self.original_image = self.image.convert_alpha()
        self.original_image.fill((0, 0, 0, 0))

        pg.draw.polygon(self.original_image,
                        self.color,
                        [utils.V2(gui.PATCH_SIZE, gui.PATCH_SIZE),
                         utils.V2(gui.HALF_PATCH_SIZE( ), 0),
                         utils.V2(0, gui.PATCH_SIZE),
                         utils.V2(gui.HALF_PATCH_SIZE( ), gui.PATCH_SIZE*3/4),
                         ])

        self.scale = scale

        # pixels = int(scale*gui.BLOCK_SPACING())
        # self.original_image = pgt.smoothscale(self.original_image, (pixels, pixels))
        # self.image = self.original_image


        Agent.id += 1
        self.id = Agent.id
        wpb.WORLD.agents.add(self)
        self.current_patch().add_agent(self)
        self.heading = 0
        self.speed = 1
        # To keep PyCharm happy.
        self.velocity = None
        self.set_velocity(utils.Velocity(0, 0))

    def __str__(self):
        class_name = utils.get_class_name(self)
        return f'{class_name}-{self.id}@{(self.center_pixel.x, self.center_pixel.y)}: ' \
               f'heading: {round(self.heading, 2)}'

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

    def current_patch(self) -> Patch:
        row_col: utils.RowCol = utils.center_pixel_to_row_col(self.center_pixel)
        patch = wpb.WORLD.patches[row_col.row, row_col.col]
        return patch

    def draw(self):
        # self.image = self.original_image
        # rotated_image = pgt.rotate(self.original_image, -self.heading)
        # pixels = int(self.scale*gui.BLOCK_SPACING())
        # self.image = pgt.smoothscale(rotated_image, (pixels, pixels))
        # self.image = self.original_image
        #
        pixels = int(self.scale*gui.BLOCK_SPACING())
        scaled_image = pgt.smoothscale(self.original_image, (pixels, pixels))
        self.image = pgt.rotate(scaled_image, -self.heading)

        # image_rect = self.image.get_rect()
        # (center_x, center_y) = self.center_pixel.as_tuple()
        # # cur_patch = self.current_patch()
        # self.rect = Rect(center_x - image_rect.width/2, center_y - image_rect.height/2,
        #                  image_rect.width, image_rect.height)
        self.rect = self.image.get_rect(center=self.center_pixel.as_tuple())
        # print(f'{self}, {cur_patch}-{cur_patch.center_pixel}, image: {image_rect}-{image_rect.center}, {self.rect}')
        super().draw()

    def face_xy(self, xy: utils.PixelVector):
        new_heading = self.towards_xy(xy)
        self.set_heading(new_heading)

    def forward(self, speed=None):
        if speed is None:
            speed = self.speed
        angle = pi * self.normalize_angle_360(self.heading - 90)*(-1) / 180
        dx = cos(angle) * speed
        dy = (-1)*sin(angle) * speed
        self.move_by_dxdy(utils.Velocity(dx, dy))

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
        self.center_pixel: utils.PixelVector = xy.wrap()
        r = self.rect
        (r.x, r.y) = (self.center_pixel.x-gui.HALF_PATCH_SIZE(), self.center_pixel.y-gui.HALF_PATCH_SIZE())
        new_patch = self.current_patch( )
        new_patch.add_agent(self)

    @staticmethod
    def normalize_angle_360(angle):
        return angle % 360

    def normalize_angle_180(self, angle):
        normalized_angle = self.normalize_angle_360(angle)
        return normalized_angle if normalized_angle <= 180 else normalized_angle - 360

    def set_heading(self, angle):
        self.heading = angle

    def towards_xy(self, xy):
        """ The heading to face the point (x, y) """
        delta_x = xy.x - self.center_pixel.x
        # Subtract in reverse to compensate for the reversal of the y axis.
        delta_y = self.center_pixel.y - xy.y
        atn2 = atan2(delta_y, delta_x)
        angle = (atn2 / (2 * pi) ) * 360
        new_heading = utils.angle_to_heading(angle)
        return new_heading

    def turn_left(self, delta_angles):
        self.turn_right(-delta_angles)

    def turn_right(self, delta_angles):
        self.set_heading(self.normalize_angle_360(self.heading + delta_angles))

    def set_velocity(self, velocity):
        self.velocity = velocity
        self.face_xy(self.center_pixel + velocity)


class Turtle(Agent):
    pass
