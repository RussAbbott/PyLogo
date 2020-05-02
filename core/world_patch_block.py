
from __future__ import annotations

from math import sqrt
from typing import Tuple

import numpy as np
from pygame.color import Color
from pygame.rect import Rect
from pygame.surface import Surface

import core.gui as gui
# Importing the file itself eliminates the need for a globals declaration
# noinspection PyUnresolvedReferences
import core.world_patch_block as world
from core.gui import SHAPES
from core.pairs import Pixel_xy, RowCol, center_pixel
from core.utils import get_class_name


class Block:
    """
    A generic patch/agent. Has a Pixel_xy but not necessarily a RowCol. Has a Color.
    """

    agent_text_offset = int(1.5*gui.PATCH_SIZE)
    patch_text_offset = -int(1.0*gui.PATCH_SIZE)

    def __init__(self, center_pixel: Pixel_xy, color=Color('black')):
        self.center_pixel: Pixel_xy = center_pixel
        self.rect = Rect((0, 0), (gui.PATCH_SIZE, gui.PATCH_SIZE))
        # noinspection PyTypeChecker
        sum_pixel: Pixel_xy = center_pixel + Pixel_xy((1, 1))
        self.rect.center = sum_pixel
        self.image = Surface((self.rect.w, self.rect.h))
        self.color = self.base_color = color
        self._label = None
        self.highlight = None

    def distance_to_xy(self, xy: Pixel_xy):
        x_dist = self.center_pixel.x - xy.x
        y_dist = self.center_pixel.y - xy.y
        dist = sqrt(x_dist * x_dist + y_dist*y_dist)
        return dist

    # The actual drawing (blit and draw_line) takes place in core.gui.
    def draw(self, shape_name=None):
        if self.label:
            self.draw_label()
        if isinstance(self, Patch) or shape_name in SHAPES:
            self.rect.center = self.center_pixel
            # self.rect = Rect(center=self.rect.center)
            gui.blit(self.image, self.rect)
        else:
            gui.draw(self, shape_name=shape_name)

    def draw_label(self):
        offset = Block.patch_text_offset if isinstance(self, Patch) else Block.agent_text_offset
        text_center = Pixel_xy((self.rect.x + offset, self.rect.y + offset))
        line_color = None if offset == 0 else \
                     Color('white') if isinstance(self, Patch) and self.color == Color('black') else self.color
        obj_center = self.rect.center
        gui.draw_label(self.label, text_center, obj_center, line_color)

    @property
    def label(self):
        return self._label if self._label else None

    @label.setter
    def label(self, value):
        self._label = value

    def set_color(self, color):
        self.color = color
        self.image.fill(color)


class Patch(Block):
    def __init__(self, row_col: RowCol, color=Color('black')):
        super().__init__(row_col.patch_to_center_pixel(), color)
        self.row_col = row_col
        self.agents = None
        self._neighbors_4 = None
        self._neighbors_8 = None
        self._neighbors_24 = None

    def __str__(self):
        class_name = get_class_name(self)
        return f'{class_name}{(self.row_col.row, self.row_col.col)}'

    def add_agent(self, agent):
        self.agents.add(agent)

    @property
    def col(self):
        return self.row_col.col

    @property
    def row(self):
        return self.row_col.row

    def clear(self):
        self.agents = set()
        self.label = None
        self.set_color(self.base_color)

    def neighbors_4(self):
        if self._neighbors_4 is None:
            cardinal_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1))
            self._neighbors_4 = self.neighbors(cardinal_deltas)
        return self._neighbors_4

    def neighbors_8(self):
        if self._neighbors_8 is None:
            eight_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
            self._neighbors_8 = self.neighbors(eight_deltas)
        return self._neighbors_8

    def neighbors_24(self):
        if self._neighbors_24 is None:
            twenty_four_deltas = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1),
                                  (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
                                  (-2, -1), (2, -1),
                                  (-2, 0), (2, 0),
                                  (-2, 1), (2, 1),
                                  (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
                                  )
            self._neighbors_24 = self.neighbors(twenty_four_deltas)
        return self._neighbors_24

    def neighbors(self, deltas):
        """
        The neighbors of this patch determined by the deltas.
        Note the addition of two RowCol objects to produce a new RowCol object: self.row_col + utils.RowCol(r, c).
        Wrap around is handled by RowCol. We then use the RowCol object as a tuple to access the np.ndarray
        """
        # noinspection PyUnresolvedReferences
        neighbors = [World.patches_array[(self.row_col + RowCol((r, c))).wrap().as_int()]
                     for (r, c) in deltas]
        return neighbors

    def remove_agent(self, agent):
        self.agents.remove(agent)


class World:

    agents = None
    links = None

    patches = None
    patches_array: np.ndarray = None

    ticks = None

    world = None

    def __init__(self, patch_class, agent_class):

        World.ticks = 0
        World.world = self

        self.patch_class = patch_class
        self.create_patches_array()

        self.agent_class = agent_class
        self.done = False
        self.reset_all()

    @staticmethod
    def clear_all():
        World.agents = set()
        World.links = set()
        for patch in World.patches:
            patch.clear()

    def create_agents(self, nbr_agents):
        for _ in range(nbr_agents):
            self.agent_class()

    def create_ordered_agents(self, n, shape_name='netlogo_figure', scale=1.4, color=None, radius=140):
        """
        Create n Agents with headings evenly spaced from 0 to 360
        Return a list of the Agents in the order created.
        """
        agent_list = [self.agent_class(shape_name=shape_name, scale=scale, color=color) for _ in range(n)]
        for (i, agent) in enumerate(agent_list):
            heading = i * 360 / n
            agent.set_heading(heading)
            if radius:
                agent.forward(radius)
        return agent_list

    def create_patches_array(self):
        patch_pseudo_array = [[self.patch_class(RowCol((r, c))) for c in range(gui.PATCH_COLS)]
                              for r in range(gui.PATCH_ROWS)]
        World.patches_array = np.array(patch_pseudo_array)
        # .flat is an iterator. Can't use it more than once.
        World.patches = list(World.patches_array.flat)

    def create_random_agent(self, color=None, shape_name='netlogo_figure', scale=1.4):
        """
        Create an Agent placed randomly on the screen.
        Set it to face the screen's center pixel.
        """
        agent = self.agent_class(color=color, shape_name=shape_name, scale=scale)
        agent.move_to_xy(Pixel_xy.random_pixel())
        agent.face_xy(center_pixel())
        return agent

    def create_random_agents(self, nbr_agents, color=None, shape_name='netlogo_figure', scale=1.4):
        """
        Create nbr_agents Agents placed randomly on the screen.
        They are all facing the screen's center pixel.
        """
        for _ in range(nbr_agents):
            self.create_random_agent(color=color, shape_name=shape_name, scale=scale)
            # agent = self.agent_class(color=color, shape_name=shape_name, scale=scale)
            # agent.move_to_xy(Pixel_xy.random_pixel())
            # agent.face_xy(center_pixel())

    def draw(self):
        """ 
        Draw the world by drawing the patches and agents. 
        Should check to see which really need to be re-drawn.
        """
        for patch in World.patches:
            patch.draw()

        for link in World.links:
            link.draw()

        for agent in World.agents:
            agent.draw()

    def final_thoughts(self):
        """ Add any final tests, data gathering, summarization, etc. here. """
        pass
        # Uncomment this code to see how well the (@lru) caches work.
        # print()
        # for fn in [utils._heading_to_dxdy_int, utils._dx_int, utils._dy_int,
        #            utils.atan2_normalized, utils._cos_int, utils._sin_int]:
        #     if fn == utils.atan2:
        #         print()
        #     print(f'{str(fn.__wrapped__).split(" ")[1]}: {fn.cache_info()}')

    def handle_event(self, _event):
        pass

    @staticmethod
    def increment_ticks():
        World.ticks += 1

    def mouse_click(self, xy):
        pass

    def pixel_tuple_to_patch(self, xy: Tuple[int, int]):
        """
        Get the patch RowCol for this pixel
       """
        return self.pixel_xy_to_patch(Pixel_xy(xy))

    @staticmethod
    def pixel_xy_to_patch(pixel_xy: Pixel_xy) -> Patch:
        """
        Get the patch RowCol for this pixel
       """
        row_col: RowCol = pixel_xy.pixel_to_row_col()
        patch = World.patches_array[row_col.row, row_col.col]
        return patch

    def reset_all(self):
        self.done = False
        self.clear_all()
        self.reset_ticks()

    @staticmethod
    def reset_ticks():
        World.ticks = 0

    def setup(self):
        """
        Set up the world. Override for each world
        """
        pass

    def step(self):
        """
        Update the world. Override for each world
        """
        pass
