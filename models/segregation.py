
from random import choice, randint, sample

from pygame import Color

from core.agent import Agent, PYGAME_COLORS
from core.sim_engine import gui_get
from core.world_patch_block import Patch, World


class SegregationAgent(Agent):

    pct_similar_wanted = None

    def __init__(self, color=None):
        super().__init__(color=color)
        self.is_happy = None
        self.pct_similar = None
        # self.pct_similar_wanted = None

    def find_new_spot(self, empty_patches):
        """
        If this agent is happy, do nothing.
        If it's unhappy move it to an empty patch where it is happy if one can be found.
        Otherwise, move it to any empty patch.

        Keep track of the empty patches instead of wandering around looking for one.
        The original NetLogo code doesn't check to see if the agent would be happy in its new spot.
        (Doing so doesn't guarantee that the formerly happy neighbors in the new spot remain happy!)
        """
        # Keep track of the current patch. Will add to empty patches after this Agent moves.
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
        agents_nearby_list = [agent for patch in self.current_patch().neighbors_8() for agent in patch.agents]
        total_nearby_count = len(agents_nearby_list)
        similar_nearby_count = len([agent for agent in agents_nearby_list if agent.color == self.color])
        # Isolated agents, i.e., with no neighbors, are considered
        # to have 100% similar neighbors, and are counted as happy.
        similar_here_pct = 100 if total_nearby_count == 0 else round(100 * similar_nearby_count / total_nearby_count)
        return similar_here_pct

    def pct_similarity_satisfied_here(self, patch) -> float:
        """
        Returns the degree to which the similarity here satisfies pct_similar_wanted.
        Returns a value between 0 and 1. (Never more than 1.)
        Doesn't favor patches with more similar neighbors over patches with just a
        sufficient number of similar neighbors.
        """
        return min(1.0, self.pct_similar_here(patch)/SegregationAgent.pct_similar_wanted)


    def update(self):
        """
        Determine pct_similar and whether this agent is happy.
        """
        self.pct_similar = self.pct_similar_here(self.current_patch())
        self.is_happy = self.pct_similar >= SegregationAgent.pct_similar_wanted


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
        self.max_agents_per_step = None
        self.patch_color = Color('white')
        self.color_items = None

    def colors_string(self):
        return f'{self.parse_color(self.color_items[0])} and {self.parse_color(self.color_items[1])}.'

    def draw(self):
        for patch in self.patches:
            if not patch.agents:
                patch.draw()
        for agent in World.agents:
            current_patch = agent.current_patch()
            current_patch.set_color(agent.color)
            current_patch.draw()
            current_patch.set_color(self.patch_color)

    def final_thoughts(self):
        print(f'\n\t Again, the colors: {self.colors_string()}')
        super().final_thoughts()

    @staticmethod
    def parse_color(color):
        (color_name, (r, g, b)) = color
        return f'"{color_name}"-(red: {r}, green: {g}, blue: {b})'

    @staticmethod
    def select_the_colors():
        """
        Require reasonably intense colors for which r, g, and b are not too close to each other
        and which are reasonably different. Use PYGAME_COLORS for more options.
        """
        # Don't use the NetLogo pallette. It's too limited.
        Agent.color_palette = PYGAME_COLORS
        while True:
            colors = sample(Agent.color_palette, 2)

            # Ensure that overall the colors are different enough.
            sums = [sum(color[1]) for color in colors]

            # Require at least one color to be somewhat subdued and one to be somewhat bright
            if not (250 < min(sums) < 500 < max(sums) < 750):
                continue

            # Reject any pair of colors that are too close to each other.
            rgb_pairs = zip(list(colors)[0][1], list(colors)[1][1])
            colors_diff = sum(abs(c1 - c2) for (c1, c2) in rgb_pairs)
            if colors_diff < 500:
                continue
            return colors if sums[0] < sums[1] else [colors[1], colors[0]]

    def setup(self):
        density = gui_get('density')
        SegregationAgent.pct_similar_wanted = gui_get('% similar wanted')
        self.color_items = self.select_the_colors()
        (color_a, color_b) = [color_item[1] for color_item in self.color_items]
        print(f'\n\t The colors: {self.colors_string()}')
        self.empty_patches = set()
        self.max_agents_per_step = gui_get('max_agents_per_step')
        for patch in self.patches:
            patch.set_color(self.patch_color)
            patch.neighbors_8()  # Calling neighbors_8 stores it as a cached value

            # Create the Agents. The density is approximate.
            if randint(0, 100) <= density:
                agent = SegregationAgent(color=choice([color_a, color_b]))
                # agent.pct_similar_wanted = pct_similar_wanted
                agent.move_to_patch(patch)
            else:
                self.empty_patches.add(patch)
        self.update_all()

    def step(self):
        nbr_unhappy_agents = len(self.unhappy_agents)
        # If there are only a few unhappy agents, move them carefully.
        # Otherwise move the smaller of self.max_agents_per_step and nbr_unhappy_agents/2
        sample_size = min(self.max_agents_per_step, max(1, nbr_unhappy_agents//2))
        for agent in sample(self.unhappy_agents, sample_size):
            agent.find_new_spot(self.empty_patches)
        self.update_all()

    def update_all(self):
        # Update Agents
        for agent in World.agents:
            agent.update()

        # Update Globals
        percent_similar = round(sum(agent.pct_similar for agent in World.agents)/len(World.agents))
        if World.ticks == 0:
            print()
        print(f'\t{World.ticks:2}. agents: {len(World.agents)};  %-similar: {percent_similar}%;  ', end='')

        self.unhappy_agents = [agent for agent in World.agents if not agent.is_happy]
        unhappy_count = len(self.unhappy_agents)
        percent_unhappy = round(100 * unhappy_count / len(World.agents), 2)
        print(f'nbr-unhappy: {unhappy_count:3};  %-unhappy: {percent_unhappy}.')
        self.done = unhappy_count == 0


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [[sg.Text('density'),
                   sg.Slider(key='density', range=(50, 95), resolution=5, size=(10, 20),
                             default_value=90, orientation='horizontal', pad=((0, 0), (0, 20)),
                             tooltip='The ratio of households to housing units')],

                  [sg.Text('% similar wanted',
                           tooltip='The percentage of similar people among the occupied 8 neighbors required ' 
                                   'to make someone happy.'),
                  sg.Combo(key='% similar wanted', values=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                           default_value=100,
                           tooltip='The percentage of similar people among the occupied 8 neighbors required ' 
                                   'to make someone happy.')],

                  [sg.Text('Max agents per step'),
                   sg.Slider(key='max_agents_per_step', range=(10, 2000), resolution=10, size=(10, 20),
                             default_value=500, orientation='horizontal', pad=((0, 0), (0, 20)),
                             tooltip='Maximium number of unhappy agents to move each step.')],
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(SegregationWorld, "Schelling's segregation model", gui_left_upper)
