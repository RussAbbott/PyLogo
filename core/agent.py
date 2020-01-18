
from math import sqrt

import pygame as pg
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame import Surface
import pygame.transform as pgt

# noinspection PyUnresolvedReferences
import PyLogo.core.agent as agent
import PyLogo.core.gui as gui
from PyLogo.core.gui import HALF_PATCH_SIZE, PATCH_SIZE
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils
from PyLogo.core.world_patch_block import Block, Patch, World

from random import choice, randint
from statistics import mean


def is_acceptable_color(rgb):
    """
    Require reasonably bright colors (sum_rgb >= 150) for which r, g, and b are not too close to each other,
    i.e., not too close to gray.
    """
    sum_rgb = sum(rgb)
    avg_rgb = sum_rgb/3
    return sum_rgb >= 150 and sum(abs(avg_rgb-x) for x in rgb) > 100


# These are colors defined by pygame that satisfy is_acceptable_color() above.
PYGAME_COLORS = [(name, rgba[:3]) for (name, rgba) in THECOLORS.items() if is_acceptable_color(rgba[:3])]

# These are NetLogo primary colors -- more or less.
NETLOGO_PRIMARY_COLORS = [(color_name, Color(color_name))
                          for color_name in ['gray', 'red', 'orange', 'brown', 'yellow', 'green', 'limegreen',
                                             'turquoise', 'cyan', 'skyblue3', 'blue', 'violet', 'magenta', 'pink']]

# Since it's used as a default value, can't be a list. A tuple works just as well.
SHAPES = {'netlogo_figure': ((1, 1), (0.5, 0), (0, 1), (0.5, 3/4))}


class Agent(Block):

    color_palette = choice([NETLOGO_PRIMARY_COLORS, PYGAME_COLORS])

    id = 0

    SQRT_2 = sqrt(2)

    def __init__(self, center_pixel=None, color=None, scale=1.4, shape=agent.SHAPES['netlogo_figure']):
        # Can't make this a default value because utils.CENTER_PIXEL() isn't defined
        # when the default values are compiled
        if center_pixel is None:
            center_pixel = utils.center_pixel()

        if color is None:
            # Select a color at random from the color_palette
            # Agent.color_palette is set during World.setup().
            color = choice(Agent.color_palette)[1]

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

    def agents(self):
        return self.the_world().agents

    def agents_in_radius(self, distance):
        qualifying_agents = [agent for agent in self.agents()
                             if agent is not self and self.distance_to(agent) < distance]
        return qualifying_agents

    def average_of_headings(self, agent_set, fn):
        """
        fn extracts a heading from an agent. This function returns the average of those headings.
        Cannot be static because fn may refer to self.
        agent_set may not be all the agents. So it must be passed as an argument.
        """
        # dx and dy are the x and y components of traveling one unit in the heading direction.
        dx = mean([utils.dx(fn(agent)) for agent in agent_set])
        dy = mean([utils.dy(fn(agent)) for agent in agent_set])
        return utils.dxdy_to_heading(dx, dy, default_heading=self.heading)

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
        factor = self.scale*PATCH_SIZE
        scaled_shape = [(v[0]*factor,  v[1]*factor) for v in self.shape]
        pg.draw.polygon(base_image, self.color, scaled_shape)
        return base_image

    def create_blank_base_image(self):
        # Give the agent a larger Surface (by sqrt(2)) to work with since it may rotate.
        blank_base_image = Surface((self.rect.w * Agent.SQRT_2, self.rect.h * Agent.SQRT_2))
        blank_base_image = blank_base_image.convert_alpha()
        blank_base_image.fill((0, 0, 0, 0))
        return blank_base_image

    def current_patch(self) -> Patch:
        row_col: utils.RowCol = (self.center_pixel).pixel_to_patch()
        patch = self.the_world().patches[row_col.row, row_col.col]
        return patch

    def distance_to(self, other):
        wrap = not self.get_gui_value('Bounce?')
        dist = (self.center_pixel).distance_to(other.center_pixel, wrap)
        return dist

    def draw(self):
        self.image = pgt.rotate(self.base_image, -self.heading)
        self.rect = self.image.get_rect(center=self.center_pixel.as_tuple())
        super().draw()
        
    def face_xy(self, xy: utils.Pixel_xy):
        new_heading = (self.center_pixel).heading_toward(xy)
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
        return from_pixel.heading_toward(to_pixel)

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

    def move_to_xy(self, xy: utils.Pixel_xy):
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

    def set_center_pixel(self, xy: utils.Pixel_xy):
        self.center_pixel: utils.Pixel_xy = xy.wrap()
        r = self.rect
        (r.x, r.y) = (self.center_pixel.x - HALF_PATCH_SIZE(), self.center_pixel.y - HALF_PATCH_SIZE())

    def set_color(self, color):
        self.color = color
        self.base_image = self.create_base_image()

    def set_heading(self, heading):
        # Keep heading an int in range(360)
        self.heading = 0 if heading is None else int(round(heading))

    def turn_left(self, delta_angles):
        self.turn_right(-delta_angles)

    def turn_right(self, delta_angles):
        self.set_heading(utils.normalize_360(self.heading + delta_angles))

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
