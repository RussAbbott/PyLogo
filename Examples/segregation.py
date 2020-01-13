
from PyLogo.core.agent import Agent
import PyLogo.core.world_patch_block as wpb
from PyLogo.core.world_patch_block import Patch, World

from pygame import Color

from random import choice, randint, sample


class SegregationAgent(Agent):

    def __init__(self):
        super().__init__()
        self.is_happy = None
        self.pct_similar = None
        self.pct_similar_wanted = None

    def find_new_spot_if_unhappy(self, empty_patches):
        """
        If this agent is happy, do nothing.
        If it's unhappy move it to an empty patch where it is happy if one can be found.
        Otherwise, move it to any empty patch.

        Keep track of the empty patches instead of wandering around looking for one.
        The original NetLogo code doesn't check to see if the agent would be happy in its new spot.
        (Doing so doesn't guarantee that the formerly happy new neighbors in the new spot remain happy!)
        """
        if not self.is_happy:
            # Keep track of current patch. Will add to empty patches after this Agent moves.
            current_patch = self.current_patch()
            # Find one of the best available patches. The sample size of 25 is arbitrary.
            # It seems like a reasonable compromize between speed and number of steps.
            nbr_of_patches_to_sample = min(25, len(empty_patches))
            best_patch = max(sample(empty_patches, nbr_of_patches_to_sample),
                             key=lambda patch: self.pct_similarity_satisfied_here(patch))
            empty_patches.remove(best_patch)
            empty_patches.add(current_patch)
            self.move_to_patch(best_patch)

    def pct_similar_here(self, patch) -> int:
        """
        Returns an integer between 0 and 100 for the percent similar to neighbors.
        Returns 100 if no neighbors,
        """
        self.move_to_patch(patch)
        agents_nearby_list = [tur for patch in self.current_patch().neighbors_8() for tur in patch.agents]
        total_nearby_count = len(agents_nearby_list)
        similar_nearby_count = len([tur for tur in agents_nearby_list if tur.color == self.color])
        # Isolated agents, i.e., with no nearby neighbors, are considered to have 0% similar neighbors.
        similarity = 0 if total_nearby_count == 0 else round(100 * similar_nearby_count / total_nearby_count)
        return similarity

    def pct_similarity_satisfied_here(self, patch) -> float:
        """
        Returns the degree to which the similarity here satisfies pct_similar_wanted.
        Returns a fraction between 0 and 1.
        Never more than 1. Doesn't favor more similar patches over sufficiently similar patches.
        """
        return min(1.0, self.pct_similar_here(patch)/self.pct_similar_wanted)


    def update(self):
        """
        Determine pct_similar and whether this agent is happy.
        """
        self.pct_similar = self.pct_similar_here(self.current_patch())
        self.is_happy = self.pct_similar >= self.pct_similar_wanted


class SegregationWorld(World):
    """
      percent-similar: on the average, what percent of a agent's neighbors are the same color as that agent?
      percent-unhappy: what percent of the agents are unhappy?
    """
    def __init__(self, patch_class=Patch, agent_class=SegregationAgent):
        super().__init__(patch_class=patch_class, agent_class=agent_class)

        self.empty_patches = None
        self.percent_similar = None
        self.percent_unhappy = None
        self.unhappy_agents = None
        # This is an experimental number.
        self.max_agents_per_step = 60
        self.patch_color = Color('white')

    def done(self):
        return all(tur.is_happy for tur in self.agents)

    def draw(self):
        for patch in self.patches.flat:
            if not patch.agents:
                patch.draw()
        for agent in self.agents:
            current_patch = agent.current_patch()
            current_patch.set_color(agent.color)
            current_patch.draw()
            current_patch.set_color(self.patch_color)
            # agent.draw()

    @staticmethod
    def select_the_colors():
        """
        Require reasonably intense colors for which r, g, and b are not too close to each other
        and which are reasonably different.
        """
        while True:
            # Each color_4 element is (r, g, b, a)
            colors_4 = sample(Agent.color_palette, 2)
            # Discard the 'a' value
            colors = [color[:3] for color in colors_4]
            # Reject any color that's too close to gray (gray_measure).
            too_gray = False
            for color in colors:
                rgb_avg = sum(color)/3
                gray_measure = sum(abs(rgb_avg-ci) for ci in color)
                too_gray = too_gray or gray_measure < 75
            if too_gray:
                continue
            # Reject any pair of colors that are too close to each other.
            rgb_pairs = zip(colors[0], colors[1])
            colors_diff = sum(abs(c1 - c2) for (c1, c2) in rgb_pairs)
            if colors_diff > 400:
                return colors

    def setup(self):
        density = self.get_gui_value('density')
        pct_similar_wanted = self.get_gui_value('% similar wanted')

        (color_a, color_b) = self.select_the_colors()

        self.empty_patches = set()
        for patch in self.patches.flat:
            patch.set_color(self.patch_color)
            patch.neighbors_8()  # Calling neighbors_8 stores it as a cached value

            # Create the Agents. The density is approximate.
            if randint(0, 100) <= density:
                agent = SegregationAgent()
                agent.pct_similar_wanted = pct_similar_wanted
                agent.set_color(choice([color_a, color_b]))
                agent.move_to_patch(patch)
            else:
                self.empty_patches.add(patch)

        self.update_all()

    def step(self):
        nbr_unhappy_agents = len(self.unhappy_agents)
        # If there are small number of unhappy agents, move them carefully.
        # Otherwise move the smaller of self.max_agents_per_step and nbr_unhappy_agents
        sample_size = max(1, round(nbr_unhappy_agents/2)) if nbr_unhappy_agents <= 4 else \
                      min(self.max_agents_per_step, nbr_unhappy_agents)
        for agent in sample(self.unhappy_agents, sample_size):
            agent.find_new_spot_if_unhappy(self.empty_patches)
        self.update_all()

    def update_all(self):
        # Update Agents
        for agent in self.agents:
            agent.update()

        # Update Globals
        percent_similar = round(sum(agent.pct_similar for agent in self.agents)/len(self.agents))
        if wpb.WORLD.TICKS == 0:
            print()
        print(f'\t{wpb.WORLD.TICKS:2}. agents: {len(self.agents)};  %-similar: {percent_similar}%;  ', end='')

        self.unhappy_agents = [agent for agent in self.agents if not agent.is_happy]
        unhappy_count = len(self.unhappy_agents)
        percent_unhappy = round(100 * unhappy_count / len(self.agents), 2)
        print(f'nbr-unhappy: {unhappy_count:3};  %-unhappy: {percent_unhappy}.')


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_elements = [[sg.Text('density'),
                sg.Slider(key='density', range=(50, 95), resolution=5, size=(10, 20),
                          default_value=90, orientation='horizontal', pad=((0, 0), (0, 20)),
                          tooltip='The ratio of households to housing units')],

                [sg.Text('% similar wanted',
                         tooltip='The percentage of similar people among the occupied 8 neighbors required ' 
                                 'to make someone happy.'),
                sg.Combo(key='% similar wanted', values=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                         background_color='skyblue', default_value=100,
                         tooltip='The percentage of similar people among the occupied 8 neighbors required ' 
                                 'to make someone happy.')],
                ]

if __name__ == "__main__":
    from PyLogo.Examples.main import PyLogo
    PyLogo(SegregationWorld, "Schelling's segregation model", gui_elements, bounce=None)
