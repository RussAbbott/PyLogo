
from copy import copy
from random import choices, random, uniform
from typing import List

from pygame import Color

from core.agent import Agent
from core.ga import GA_World
from core.link import Link, hash_object
from core.pairs import Velocity
from core.sim_engine import gui_get
from core.world_patch_block import World

from models.ga_and_aco_examples.ga_tsp import order_elements


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

    # The following are all very similar colors. Take your pick. Or select another one.
    # best_link_color = (100, 150, 255)
    # best_link_color = Color('steelblue1')      # (99, 184, 255, 255)
    # best_link_color = Color('steelblue2')      # (92, 172, 238, 255)
    # best_link_color = Color('skyblue')         # (135, 206, 235, 255)
    # best_link_color = Color('skyblue1')        # (135, 206, 255, 255)
    # best_link_color = Color('skyblue2')        # (126, 192, 238, 255)
    best_link_color = Color('skyblue3')        # (108, 166, 205, 255)
    # best_link_color = Color('cornflowerblue')  # (100, 149, 237, 255)
    # best_link_color = Color('deepskyblue2')    # (0, 178, 238, 255)
    # best_link_color = Color('lightskyblue2')   # (164, 211, 238, 255)
    # best_link_color = Color('lightskyblue3')   # (141, 182, 205, 255)
    # best_link_color = Color('cadetblue2')      # (142, 229, 238, 255)
    # best_link_color = Color('cadetblue3')      # (122, 197, 205, 255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_best = False
        self.pheromone_level = 50

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

            # This is a valid call to Color. PyCharm doesn't like it.
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
        self.prev_max_speed = self.max_speed = gui_get('Max_speed')

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
        World.links = set(ACO_Link(cities[i], cities[j]) for i in range(len(cities)-1)
                                                         for j in range(i+1, len(cities)))

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
        # We want to return to start_city only after all the other cities are visited.
        # So remove start_city from unvisited_cities. (pop removes the city it pops.)
        current_city = start_city = unvisited_cities.pop()

        tour = []
        while unvisited_cities:
            link_weight_pairs = [(lnk, (lnk.pheromone_level**alpha)/(max(1, lnk.length)**beta)) for lnk in World.links
                                 if lnk.includes(current_city) and lnk.other_side(current_city) in unvisited_cities]
            if best:
                # Get the best pair
                best_link_weight_pair = max(link_weight_pairs, key=lambda lnk_wt: lnk_wt[1])
                # Extract the link
                next_link = best_link_weight_pair[0]
            else:
                # Notice what this does. It "unzips" the pairs in link_weight_pairs.
                (lnks, weights) = zip(*link_weight_pairs)

                # The function random.choices returns a list of k items. Since k == 1, only one
                # item is in the list. Retrieve that item. It will be the next link on the tour.
                next_link = choices(lnks, weights=weights, k=1)[0]
                
            tour.append(next_link)

            next_city = next_link.other_side(current_city)
            unvisited_cities.remove(next_city)
            current_city = next_city

        # The final link links the final city to the start city.
        # DON'T create a new link. One already exists. Find it.
        # For undirected links (Like the ones we use) hash_object is a frozen set of the two link ends.
        final_link = [lnk for lnk in World.links if lnk.hash_object == hash_object(current_city, start_city)][0]
        tour.append(final_link)

        tour_length = round(self.total_dist(tour))
        if tour_length < self.best_tour_length:
            self.best_tour_length = tour_length
        return tour

    def handle_event(self, event):
        if event == 'Max_speed':
            self.prev_max_speed = self.max_speed
            self.max_speed = gui_get('Max_speed')/100
        else:
            super().handle_event(event)

    def mark_best_tour(self):
        """ Mark the links in the best tour. """
        # Generate a number of "best" tours in case best tours starting at different start cities are different.
        best_tour_links_list = [self.generate_a_tour(best=True) for _ in range(5)]
        best_tour_links = min(best_tour_links_list, key=lambda tour: self.total_dist(tour) )
        self.best_tour_length = round(self.total_dist(best_tour_links))

        # To get the start city, find the city that appears in the first two links.
        (link_0, link_1) = best_tour_links[:2]
        start_city = link_0.agent_1 if link_1.includes(link_0.agent_1) else link_0.agent_2
        city_sequence = [start_city]
        for lnk in best_tour_links[1:]:
            next_city = lnk.other_side(city_sequence[-1])
            city_sequence.append(next_city)
        best_tour_cities = order_elements(city_sequence)
        # Is this tour better than the current best_tour?
        if ACO_World.best_tour_cities != best_tour_cities:
            for lnk in World.links:
                lnk.is_best = False
            for lnk in best_tour_links:
                lnk.is_best = True
            print(f"{''.join([str(city) for city in best_tour_cities])}")
            ACO_World.best_tour_cities = best_tour_cities

    def move_cities(self):
        speed_change_factor = None if self.prev_max_speed == 0 else self.max_speed / self.prev_max_speed

        # self.max_speed has changed <==> speed_change_factor != 1
        if speed_change_factor != 1:

            for city in self.cities:
                # If the prev max speed was 0 (i.e., speed_change_factor is None), generate a new velocity.
                # Otherwise adjust the current velocity.
                new_velocity = ACO_World.random_velocity() if speed_change_factor is None else \
                               city.velocity * speed_change_factor
                city.set_velocity(new_velocity)

            # We've dealt with the change in self.max_speed. Set self.prev_max_speed = self.max_speed
            self.prev_max_speed = self.max_speed

        for city in self.cities:
            # Don't generate a new random velocity if we just did that (speed_change_factor == None).
            if speed_change_factor is not None and random() < 0.001:
                city.set_velocity(ACO_World.random_velocity())
            city.move_by_velocity()

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
        # call step once
        self.step()

    def step(self):

        if self.max_speed > 0:
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
        """ Update the links in this tour based on how good the tour is. """
        tour_length = round(self.total_dist(tour))
        # The factors 'update increment step' and 'update_weight' are arbitrary parameters.
        # 'update increment step' is intended to limit the rate at which the pheromone level
        # can approach 100. 'update_weight' puts a weight on how much a good tour is considered
        # important. The current tour is measured against the best current tour. The two factor
        # are divided by 100 and 10 because Sliders support only integers, not fractional values.

        # 'update increment step' is intended to limit the rate at
        # which the pheromone level is permitted to approach 100.
        def max_increment(lnk):
            """ The maximum abount by which lnk's peromone level may increase due to one tour. """
            return (100 - lnk.pheromone_level)*gui_get('update increment step')/100

        # raw_increment is the computed amount by which this your will increase
        # the pheromone level of all links in its current tour. Make it a function of
        # how the current tour compares to the curent best tour.
        raw_increment = (gui_get('update_weight')/10) * (self.best_tour_length/tour_length)

        for lnk in tour:
            lnk.pheromone_level += min(max_increment(lnk), raw_increment)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

path_controls = [[sg.Checkbox('Show city labels', key='show_labels', default=True, pad=((0, 0), (10, 0)))],

                 [sg.Checkbox('Show pheromone levels', key='show_phero_levels', default=True, pad=((0, 0), (10, 0)))],

                 [sg.Text('Max speed', pad=((0, 0), (10, 0))),
                  sg.Combo(values=[i*10 for i in range(11)], default_value=50, key='Max_speed', enable_events=True)]
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
                       sg.Slider(key='Min_pheromone', range=(0, 85), default_value=70, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Text('Min display level', pad=((0, 5), (10, 0))),
                       sg.Slider(key='Min_display_level', range=(30, 95), default_value=35, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Frame('Path controls', path_controls, pad=(None, (10, 0)))]
                                       ]

if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(ACO_World, 'ACO for TSP', aco_gui_left_upper, agent_class=ACO_Agent, bounce=True)
