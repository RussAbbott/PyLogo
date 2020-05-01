
from copy import copy
from random import random, uniform
from typing import List

from pygame import Color

from core.agent import Agent
from core.ga import GA_World
from core.link import Link
from core.pairs import Velocity
from core.sim_engine import gui_get
from core.world_patch_block import World
from ga_and_aco_examples.ga_tsp import order_elements


class ACO_Agent(Agent):
    """ The agents are the cities. """

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return self.label

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns a letter identifier corresponding to the agent's id.
        """
        return chr(ord('A') + self.id) if gui_get('show_labels') else None


class ACO_Link(Link):

    best_link_color = (100, 150, 255)

    def __init__(self, *args, from_city=None, to_city=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_best = False
        self.pheromone_level = 50

        # The Link is not directed. But we want to keep track
        # of which cities it is being used to link together.
        self.from_city = from_city
        self.to_city = to_city

    def __str__(self):
        return f'{self.from_city}-->{self.to_city}'

    def draw(self):
        if self.is_best:
            self.set_color(ACO_Link.best_link_color)
            self.set_width(4)
        else:
            phero_level = self.pheromone_level
            if phero_level < gui_get('Min_display_level'):
                return

            # Determine the color between red and green based on the pheromone level.
            min_pheromone = gui_get('Min_pheromone')
            range = 100 - min_pheromone
            red = min(255, max(0, round(150*(range - (phero_level-min_pheromone))/range)))
            green = min(100, max(0, round(255*(phero_level-min_pheromone)/range)))

            # This is a valid call to Color
            # noinspection PyArgumentList
            color = Color(red, green, 0, 0)
            self.set_color(color)
            self.set_width(1)

        super().draw()

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the pheromone_level of the link as its label.
        """
        return str(round(self.pheromone_level)) if gui_get('show_phero_levels') else None


class ACO_World(GA_World):

    best_tour_cities = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_tour_length = None

    @property
    def cities(self):
        return World.agents

    @staticmethod
    def discount_pheromone_values():
        """
        Discount the pheromone values of all the links.
        This represents the pheromone "evaporation" rate. It's like the discount rate in
        reinforcement learning. The older information is, the less valuable it is considered to be.
        """
        discount = (100 - gui_get('discount factor')) / 100
        min_pheromone = gui_get('Min_pheromone')
        for lnk in World.links:
            lnk.pheromone_level = max(min_pheromone, discount * lnk.pheromone_level)

    def gen_cities_and_links(self):
        # The cities are represented by Agents.
        nbr_cities = gui_get('nbr_cities')
        self.create_random_agents(nbr_cities, color=Color('white'), shape_name='node', scale=1)
        for city in self.cities:
            city.set_velocity(ACO_World.random_velocity())

        # To create the links, make cities indexible.
        cities = list(self.cities)
        World.links = set(ACO_Link(cities[i], cities[j]) for i in range(len(cities)-1) for j in range(i+1, len(cities)))

    # noinspection PyUnusedLocal
    def generate_a_tour(self, best=False) -> List[ACO_Link]:
        """
        From a random starting point, return a list of links that
        makes a cycle from that starting point back to itself.

        If best is True, always follow the link with the highest weight.
        Otherwise follow links probabilistically based on their weights.
        """
        alpha = gui_get('alpha')
        beta = gui_get('beta')
        unvisited_cities = copy(self.cities)
        # pop remove start_city from unvisited_cities. We want to
        # return to start_city only after all the other cities.
        current_city = start_city = unvisited_cities.pop()

        tour = []
        while unvisited_cities:
            """ You write the loop body. """
            ...

        """ 
        Don't forget the final link back to the start city. 
        DON'T create a new link. One already exists. Find it. 
        """
        final_link = ...
        tour.append(final_link)

        (final_link.from_city, final_link.to_city) = (current_city, start_city)
        tour_length = round(self.total_dist(tour))
        if tour_length < self.best_tour_length:
            self.best_tour_length = tour_length
        return tour

    def mark_best_tour(self):
        """ Mark the links in the best tour. """
        best_tour_links_list = [self.generate_a_tour(best=True) for _ in range(5)]
        best_tour_links = min(best_tour_links_list, key=lambda tour: self.total_dist(tour) )
        self.best_tour_length = round(self.total_dist(best_tour_links))

        city_sequence = [lnk.from_city for lnk in best_tour_links]
        best_tour_cities = order_elements(city_sequence)
        # Is this tour better than the one on the previous step?
        if ACO_World.best_tour_cities != best_tour_cities:
            for lnk in World.links:
                lnk.is_best = False
            for lnk in best_tour_links:
                lnk.is_best = True
            print(f"{''.join([str(city) for city in best_tour_cities])}")
            ACO_World.best_tour_cities = best_tour_cities

    def move_cities(self):
        """ Max_speed limits city speed only when velocity is re-assigned."""
        if gui_get('Max_speed') > 0:
            for city in self.cities:
                city.move_by_velocity()
                if random() < 0.001:
                    city.set_velocity(ACO_World.random_velocity())

    @staticmethod
    def normalize_pheromone_levels():
        """ Make sure pheromones are between Min_pheromone and 100. """
        max_pheromone_level = max(lnk.pheromone_level for lnk in World.links)
        normalization_factor = 100/max_pheromone_level
        for lnk in World.links:
            lnk.pheromone_level = max(gui_get('Min_pheromone'), normalization_factor * lnk.pheromone_level)

    @staticmethod
    def random_velocity():
        limit = gui_get('Max_speed')
        return Velocity((uniform(-limit/100, limit/100), uniform(-limit/100, limit/100)))

    def setup(self):
        Agent.id = 0
        self.gen_cities_and_links()
        average_link_length = self.total_dist(World.links) / len(World.links)
        self.best_tour_length = round( len(self.cities) * average_link_length )

    def step(self):

        self.move_cities()

        self.discount_pheromone_values()

        # On each step, run tours_per_step tours.
        # This is the key element of the step function.
        for _ in range(gui_get('tours_per_step')):
            new_tour = self.generate_a_tour()
            self.update_pheromone_levels(new_tour)

        self.normalize_pheromone_levels()

        self.mark_best_tour()

    @staticmethod
    def total_dist(links):
        return sum(lnk.length for lnk in links)

    def update_pheromone_levels(self, tour: List[ACO_Link]):
        """
        Update the links in this tour based on how good the tour is.

        The following is an outline of what I did. You don't have to follow thay approach.
        """

        # noinspection PyUnusedLocal
        tour_length = round(self.total_dist(tour))

        # 'update increment step' is intended to limit the rate at
        # which the pheromone level is permitted to approach 100.
        def max_increment(lnk):
            """ The maximum abount by which lnk's peromone level may increase due to one tour. """
            return (100 - lnk.pheromone_level)*gui_get('update increment step')/100

        # raw_increment is the computed amount by which this tour will increase
        # the pheromone level of all its links.
        #
        # I made it a function of how the current tour compares to the curent best tour.
        # 'update_weight' puts a weight on how much a good tour is considered important.

        raw_increment = ...

        for lnk in tour:
            lnk.pheromone_level += min(max_increment(lnk), raw_increment)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

path_controls = [[sg.Checkbox('Show city labels', key='show_labels', default=True, pad=((0, 0), (10, 0)))],

                 [sg.Checkbox('Show pheromone levels', key='show_phero_levels', default=True, pad=((0, 0), (10, 0)))],

                 [sg.Text('Max speed', pad=(None, (10, 0))),
                  sg.Slider(range=(0, 100), default_value=50, pad=(None, None), key='Max_speed', size=(10, 20),
                            orientation='horizontal')]
                 ]

aco_gui_left_upper = [

                      [sg.Text('Nbr cities', pad=((0, 5), (10, 0))),
                       sg.Slider(key='nbr_cities', range=(3, 20), default_value=7, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('Tours per step', pad=((0, 5), (10, 0))),
                       sg.Slider(key='tours_per_step', range=(1, 100), default_value=50, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('alpha', pad=((0, 5), (10, 0))),
                       sg.Slider(key='alpha', range=(0, 5), default_value=2, orientation='horizontal', size=(5, 20)),

                       sg.Text('beta', pad=((10, 5), (10, 0))),
                       sg.Slider(key='beta', range=(0, 5), default_value=2, orientation='horizontal', size=(5, 20))],

                      [sg.Text('update weight', pad=((0, 5), (10, 0))),
                       sg.Slider(key='update_weight', range=(1, 20), default_value=8, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('update increment step', pad=((0, 5), (10, 0))),
                       sg.Slider(key='update increment step', range=(1, 20), default_value=5, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('Discount factor', pad=((0, 5), (10, 0))),
                       sg.Slider(key='discount factor', range=(0, 100), default_value=15, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('Min pheromone level', pad=((0, 5), (10, 0))),
                       sg.Slider(key='Min_pheromone', range=(0, 75), default_value=30, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('Min display level', pad=((0, 5), (10, 0))),
                       sg.Slider(key='Min_display_level', range=(30, 95), default_value=35, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Frame('Path controls', path_controls, pad=(None, (10, 0)))]
                                       ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(ACO_World, 'ACO for TSP', aco_gui_left_upper, agent_class=ACO_Agent, bounce=True)
