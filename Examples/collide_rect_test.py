
import PyLogo.core.world_patch_block as wpb
import PyLogo.core.utils as utils

from pygame.color import Color
from pygame.sprite import collide_rect

from random import randint, random, uniform


class CollisionTest_Patch(wpb.Patch):

    def __init__(self, row_col: utils.RowCol):
        super().__init__(row_col)
        # Each patch gets a hit_color
        self.hit_color = Color('white')

    def update_collision_color(self, agents):
        collides = any([collide_rect(self, agent) for agent in agents])
        fill_color = self.hit_color if collides else self.color
        self.image.fill(fill_color)


class CollisionTest_World(wpb.World):
    """
    A world in which the patches change to green when intersecting with a agent.
    """

    def setup(self):
        nbr_agents = int(wpb.WORLD.values['nbr_agents'])
        for i in range(nbr_agents):
            # Adds itself to self.agents and to its patch's list of Agents.
            agent = self.agent_class(color=Color('red'))
            agent.set_velocity(utils.Velocity(uniform(-2, 2), uniform(-2, 2)))

        for patch in self.patches.flat:
            patch.update_collision_color(self.agents)

    def step(self):
        """
        Update the world by moving the agent and indicating the patches that intersect the agent
        """
        for agent in self.agents:
            agent.move_by_velocity()
            if random() < 0.01:
                agent.set_velocity(utils.Velocity(randint(-2, 2), randint(-2, 2)))

        for patch in self.patches.flat:
            patch.update_collision_color(self.agents)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('nbr agents', pad=((0, 5), (20, 0))),
                 sg.Slider(key='nbr_agents', range=(1, 10), default_value=3, orientation='horizontal', size=(10, 20))],
                ]

if __name__ == "__main__":
    from PyLogo.Examples.main import PyLogo
    PyLogo(CollisionTest_World, 'Collision test', gui_elements, patch_class=CollisionTest_Patch, bounce=False)
