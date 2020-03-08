
from __future__ import annotations

from pygame.color import Color

from core.agent import Agent
import core.gui as gui
from core.world_patch_block import World


def hash_object(agent_1, agent_2, directed=False):
    return (agent_1, agent_2) if directed else frozenset({agent_1, agent_2})


def link_exists(agent_1, agent_2, directed=False):
    """
    Determine whether a directed/undirected link between agent_1 and agent_2 already exists in World.links.

    The strategy is to create a hash_object of the possible link and then see if any existing link has
    the same hash_object.
    """
    hash_obj = hash_object(agent_1, agent_2, directed)
    return any(hash_obj == lnk.hash_object for lnk in World.links)


class Link:

    def __init__(self, agent_1: Agent, agent_2: Agent, directed: bool = False,
                 color: Color = Color('white'), width: int = 1):
        self.agent_1: Agent = agent_1
        self.agent_2: Agent = agent_2
        self.both_sides = {agent_1, agent_2}
        self.directed = directed
        # Create a hash_object to be used by both __eq__ and __hash__.
        self.hash_object = hash_object(agent_1, agent_2, directed)
        self.default_color = color
        self.color = color
        self.width = width
        World.links.add(self)

    def __eq__(self, other: Link):
        """
        It's conceivable (although extremely unlikely) that hash(self.hash_object) == hash(other.hash_object) even
        though self.hash_object != other.hash_object.
        Python requires that if two objects compare as __eq__ their hash values must be the same.
        Python doesn't require that if two objects have the same hash values, they must compare as __eq__.
        """
        return self.hash_object == other.hash_object

    def __hash__(self):
        return hash(self.hash_object)

    def __str__(self):
        return f'{self.agent_1} {"-->" if self.directed else "<-->"} {self.agent_2}'

    def draw(self):
        gui.draw_line(self.agent_1.rect.center, self.agent_2.rect.center, line_color=self.color, width=self.width)

    def includes(self, agent):
        return agent in (self.agent_1, self.agent_2)

    def is_linked_with(self, other, directed=False):
        return link_exists(self, other, directed)

    def other_side(self, node):
        return (self.both_sides - {node}).pop()

    def set_color(self, color):
        self.color = color

    def set_width(self, width):
        self.width = width
