
from math import floor
from random import choice, randint, shuffle
from typing import List

from core.ga import Chromosome, GA_World, Individual, gui_left_upper
from core.sim_engine import SimEngine


class Item:
    """ These are the items from which to select. """

    def __init__(self, value, weight):
        super().__init__()
        self.value = value
        self.weight = weight

    def __str__(self):
        return f'{(self.value, self.weight)}'


class Knapsack_Chromosome(Chromosome):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.

    """

    def chromosome_fitness(self) -> float:
        (_max_weight, items) = Knapsack_World.problem
        total_value = sum([self[i] * items[i].value for i in range(len(self))])
        return total_value


class Knapsack_Individual(Individual):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_weight = None
        self.trim_chromosome()
        self.fitness = self.compute_fitness()

    def __eq__(self, other):
        return self.chromosome == other.chromosome

    def __str__(self):
        return f'{self.fitness}/{self.total_weight}<-{"".join([str(gene) for gene in self.chromosome])}'

    def compute_fitness(self) -> float:
        return self.chromosome.chromosome_fitness()

    def mate_with(self, other):
        return self.cx_uniform(other)

    def mutate(self) -> Individual:

        if randint(0, 100) <= SimEngine.gui_get('invert selection'):
            new_chromosome = self.chromosome.invert_a_gene()
            new_individual = GA_World.individual_class(new_chromosome)
            return new_individual
        else:
            return self

    def trim_chromosome(self):
        (max_weight, items) = Knapsack_World.problem
        chromosome = self.chromosome
        self.total_weight = sum([chromosome[i] * items[i].weight for i in range(len(chromosome))])
        if self.total_weight <= max_weight:
            return
        selected_indices = [i for i in range(len(chromosome)) if chromosome[i]]
        chromo_list = list(chromosome)
        shuffle(selected_indices)
        for i in selected_indices:
            self.total_weight -= items[i].weight
            chromo_list[i] = 0
            if self.total_weight <= max_weight:
                break
        self.chromosome = Knapsack_Chromosome(chromo_list)


class Knapsack_World(GA_World):

    # Every problem is a tuple: (max_weight, items)
    # problems is a dictionary of problems. (So far, only one problem.)
    # problem 1 is the example from the reading.
    problems = {'Problem 1': (9, [Item(6, 2), Item(5, 3), Item(8, 6), Item(9, 7), Item(6, 5), Item(7, 9), Item(3, 4)])}

    # problem is the user-selected problem
    problem = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cycle_length = SimEngine.gui_get('cycle_length')

    def gen_individual(self):
        # A Chromosome has as many positions as the problem has items.
        chromosome_list: List = [choice([0, 1]) for _ in range(len(Knapsack_World.problem[1]))]
        chromosome = Knapsack_Chromosome(chromosome_list)
        individual = Knapsack_Individual(chromosome)
        return individual

    @staticmethod
    def set_maximum_fitness_target(items, max_weight):
        total_value = 0
        total_weight = 0
        for item in items:
            total_value += item.value
            total_weight += item.weight
            if total_weight >= max_weight:
                break
        avg_density = total_value / total_weight
        GA_World.fitness_target = floor(avg_density * max_weight)

    def set_results(self):
        print('GA_World.fitness_target 2', GA_World.fitness_target)
        super().set_results()
        print(f"{self.generations}) Pop (value/weight<-selection):  {',  '.join([str(ind) for ind in self.population])}")
        print(f'     Best (value/weight<-selection):  {self.best_ind}')

    def setup(self):
        GA_World.individual_class = Knapsack_Individual
        GA_World.chromosome_class = Knapsack_Chromosome
        problem_name = SimEngine.gui_get('Problem')
        Knapsack_World.problem = Knapsack_World.problems[problem_name]
        (max_weight, items) = Knapsack_World.problem
        Knapsack_World.set_maximum_fitness_target(items, max_weight)
        SimEngine.gui_set('fitness_target', value=f'{GA_World.fitness_target}')
        print(f'\nNew Problem (max weight: {max_weight}, items(value, weight)): '
              f'{", ".join([str(item) for item in items])}')
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

knapsack_gui_left_upper = gui_left_upper + [
    [sg.Text('Prob invert selection', pad=((0, 5), (20, 0))),
     sg.Slider(key='invert selection', range=(0, 100), default_value=25, orientation='horizontal', size=(10, 20))
     ],

    [sg.Text('Problem selection', pad=(None, (20, 0))),
     sg.Combo(key='Problem', default_value='Problem 1', pad=((10, 0), (20, 0)),
              values=['Problem 1'])
     ],

    [sg.Text('Fitness target:', pad=(None, (10, 0))),
     sg.Text('      ', key='fitness_target', pad=(None, (10, 0)))
     ],

    ]

if __name__ == "__main__":
    from core.agent import PyLogo

    # gui_left_upper is from core.ga
    PyLogo(Knapsack_World, 'Simple Knapsack problem', knapsack_gui_left_upper,
           patch_size=5, board_rows_cols=(5, 5))
