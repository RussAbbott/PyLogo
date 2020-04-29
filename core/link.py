
from __future__ import annotations

from pygame.color import Color

import core.gui as gui
from core.agent import Agent
from core.pairs import XY
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
    links = [lnk for lnk in World.links if lnk.hash_object == hash_obj]
    return links[0] if links else None


def is_reachable_via(agent_1, link_list, agent_2) -> bool:
    seen = {agent_1}
    frontier = [agent_1]
    while frontier:
        agent = frontier.pop(0)
        seen.add(agent)
        new_nghbrs = [lnk.other_side(agent) for lnk in link_list
                      if lnk.includes(agent) and lnk.other_side(agent) not in seen]
        if agent_2 in new_nghbrs:
            return True
        frontier.extend(new_nghbrs)
    return False


def minimum_spanning_tree(agent_list):
    len_agent_list = len(agent_list)
    all_links = [Link(agent_list[i], agent_list[j], add_to_world_links=False, color=Color('green'), width=2)
                 for i in range(len_agent_list - 1)
                 for j in range(i + 1, len_agent_list)]
    sorted_links = sorted(all_links, key=lambda lnk: lnk.length)
    reachable_points = set()
    link_list = []
    for lnk in sorted_links:
        if not is_reachable_via(lnk.agent_1, link_list, lnk.agent_2):
            link_list.append(lnk)
            reachable_points |= {lnk.agent_1, lnk.agent_2}
    return link_list


class Link:

    def __init__(self, agent_1: Agent, agent_2: Agent, directed: bool = False, add_to_world_links: bool = True,
                 color: Color = Color('white'), width: int = 1):
        if None in {agent_1, agent_2}:
            raise Exception(f"Can't link to None: agent_1: {agent_1}, agent_2: {agent_2}.")
        (self.agent_1, self.agent_2) = (agent_1, agent_2) if directed or agent_1 < agent_2 else (agent_2, agent_1)
        self.both_sides = {agent_1, agent_2}
        if len(self.both_sides) != 2:
            raise Exception(f"Can't have a link from a node to itself: {agent_1} == {agent_2}.")
        self.directed = directed
        # Create a hash_object to be used by both __eq__ and __hash__.
        self.hash_object = hash_object(agent_1, agent_2, directed)
        self.default_color = color
        self.color = color
        self.width = width
        if add_to_world_links:
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
        # gui.draw_line(self.agent_1.rect.center, self.agent_2.rect.center, line_color=self.color, width=self.width)
        gui.draw_line(self.agent_1.center_pixel, self.agent_2.center_pixel, line_color=self.color, width=self.width)
        if (my_label := self.label) is not None:
            # Pass the label to avoid computing it twice.
            self.draw_label(my_label)

    def draw_label(self, my_label):
        offset = int(0.5*gui.PATCH_SIZE)
        obj_center = XY(((3*self.agent_1.x + self.agent_2.x)/4, (3*self.agent_1.y + self.agent_2.y)/4))
        text_center = (obj_center.x + offset, obj_center.y + offset)
        line_color = self.color
        gui.draw_label(my_label, text_center, obj_center, line_color, background='yellow')

    def includes(self, agent):
        return agent in (self.agent_1, self.agent_2)

    def is_linked_with(self, other, directed=False):
        return link_exists(self, other, directed)

    @property
    def label(self):
        return None

    @property
    def length(self) -> float:
        return round(self.agent_1.distance_to(self.agent_2), 1)

    def other_side(self, node):
        return (self.both_sides - {node}).pop()

    def set_color(self, color):
        self.color = color

    def set_width(self, width):
        self.width = width

    def siblings(self):
        """
        Return: A tuple with the lnk_nbrs on each side, smaller side first
        """
        sibs = (self.agent_1.lnk_nbrs(), self.agent_2.lnk_nbrs())
        return sibs if len(sibs[0]) < len(sibs[1]) else (sibs[1], sibs[0])


def seq_to_links(agents, link_class=Link):
    """
    Agents is a sequence (list or tuple) of Agents.
    Returns the links that join them, include one from the end to the start.
    """
    links = []
    if len(agents) > 1:
        for i in range(len(agents)):
            lnk = link_class(agents[i], agents[(i + 1) % len(agents)])
            links.append(lnk)
    return links


