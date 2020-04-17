
from random import choice, randint
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
        (max_weight, items) = Knapsack_World.problem
        len_chrom = len(self)
        total_value = sum([self[i] * items[i].value for i in range(len_chrom)])
        total_weight = sum([self[i] * items[i].weight for i in range(len_chrom)])
        return 0 if total_weight > max_weight else total_value


class Knapsack_Individual(Individual):

    def __eq__(self, other):
        return self.chromosome == other.chromosome

    def __str__(self):
        return f'{self.fitness}<-{"".join([str(gene) for gene in self.chromosome])}'

    def compute_fitness(self) -> float:
        return self.chromosome.chromosome_fitness()

    def mate_with(self, other):
        return self.cx_uniform(other)

    def mutate(self) -> Individual:
        chromosome = self.chromosome

        if randint(0, 100) <= SimEngine.gui_get('invert selection'):
            new_chromosome = chromosome.invert_a_gene()
            new_individual = GA_World.individual_class(new_chromosome)
            return new_individual
        else:
            return self


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
        individual = GA_World.individual_class(GA_World.chromosome_class(chromosome_list))
        return individual

    def set_results(self):
        super().set_results()
        print(f"Pop (fitness<-selection):  {',  '.join([str(ind) for ind in self.population])}")
        print(f'  Best (fitness<-selection):  {self.best_ind}')


    def setup(self):
        GA_World.individual_class = Knapsack_Individual
        GA_World.chromosome_class = Knapsack_Chromosome
        problem_name = SimEngine.gui_get('Problem')
        Knapsack_World.problem = Knapsack_World.problems[problem_name]
        (weight, items) = Knapsack_World.problem
        print(f'\nNew Problem: max weight: {weight}, items (value, weight): {", ".join([str(item) for item in items])}')
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

knapsack_gui_left_upper = gui_left_upper + [
    [sg.Text('Prob invert selection', pad=((0, 5), (20, 0))),
     sg.Slider(key='invert selection', range=(0, 100), default_value=25, orientation='horizontal', size=(10, 20))
     ],

    [sg.Text('fitness target', pad=(None, (20, 0))),
     sg.Slider(key='fitness_target', range=(0, 100), default_value=15, orientation='horizontal',
               pad=((10, 0), (20, 0)), enable_events=True)
     ],

    [sg.Text('Problem selection', pad=(None, (20, 0))),
     sg.Combo(key='Problem', default_value='Problem 1', pad=((10, 0), (20, 0)),
              values=['Problem 1'])
     ],

    ]

if __name__ == "__main__":
    from core.agent import PyLogo

    # gui_left_upper is from core.ga
    PyLogo(Knapsack_World, 'Simple Knapsack problem', knapsack_gui_left_upper,
           patch_size=5, board_rows_cols=(5, 5))
