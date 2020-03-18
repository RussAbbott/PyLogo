
from random import randint, random, uniform

from pygame.color import Color
from pygame.sprite import collide_rect

from core.pairs import RowCol, Velocity
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World


class CollisionTest_Patch(Patch):

    def __init__(self, row_col: RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('white')

    def update_collision_color(self, agents):
        collides = any([collide_rect(self, agent) for agent in agents])
        fill_color = self.hit_color if collides else self.base_color
        self.set_color(fill_color)


class CollisionTest_World(World):
    """
    A world in which the patches change to green when intersecting with a agent.
    """

    def setup(self):
        nbr_agents = int(SimEngine.gui_get('nbr_agents'))
        for i in range(nbr_agents):
            # Adds itself to self.agents and to its patch's list of Agents.
            agent = self.agent_class(color=Color('red'))
            agent.set_velocity(Velocity((uniform(-2, 2), uniform(-2, 2))))

        for patch in self.patches:
            patch.update_collision_color(World.agents)

    def step(self):
        """
        Update the world by moving the agent and indicating the patches that intersect the agent
        """
        for agent in World.agents:
            agent.move_by_velocity()
            if random() < 0.01:
                agent.set_velocity(Velocity((randint(-2, 2), randint(-2, 2))))

        for patch in self.patches:
            patch.update_collision_color(World.agents)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [[sg.Text('nbr agents', pad=((0, 5), (20, 0))),
                   sg.Slider(key='nbr_agents', range=(1, 10), default_value=3, orientation='horizontal',
                             size=(10, 20))],
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(CollisionTest_World, 'Collision test', gui_left_upper, patch_class=CollisionTest_Patch, bounce=False)
