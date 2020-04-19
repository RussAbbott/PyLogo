
from __future__ import annotations

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
    
    
class Knapsack_Problem:
    
    # Every problem is a tuple: (capacity, items)
    # problems is a dictionary of problems. (So far, only one problem.)
    # problem 1 is the example from the reading.
    problems = {'Problem 1': {'capacity': 9,
                              'items': [Item(6, 2), Item(5, 3), Item(8, 6), Item(9, 7),
                                        Item(6, 5), Item(7, 9), Item(3, 4)],
                              'solution': '1001000'},
                'Problem 2': {'capacity': 10,
                              'items': [Item(4, 1), Item(8, 4), Item(7, 5), Item(9, 6), ],
                              'solution': '1101'},
                'Problem 3': {'capacity': 102,
                              'items': [Item(15, 2), Item(100, 20), Item(90, 20), Item(60, 30),
                                        Item(40, 40), Item(15, 30), Item(10, 60), Item(1, 100), ],
                              'solution': '11110100'},
                'Problem 4': {'capacity': 50,
                              'items': [Item(70, 31), Item(20, 10), Item(39, 20), Item(37, 19),
                                        Item(7, 4), Item(5, 3), Item(10, 6), ],
                              'solution': '1001000'},
                'Problem 5': {'capacity': 190,
                              'items': [Item(50, 56), Item(50, 59), Item(64, 80), Item(46, 64),
                                        Item(50, 75), Item(5, 17), ],
                              'solution': '110010'},
                'Problem 6': {'capacity': 104,
                              'items': [Item(350, 25), Item(400, 35), Item(450, 45), Item(20, 5),
                                        Item(70, 25), Item(8, 3), Item(5, 2), Item(5, 2), ],
                              'solution': '10111011'},

                }
    problem_names = list(problems.keys())
    
    def __init__(self, problem_name):
        problem = Knapsack_Problem.problems[problem_name]
        self.capacity = problem['capacity']
        items = problem['items']
        # Sort the items by density
        self.items = sorted(items, key=lambda item: item.value/item.weight, reverse=True)
        self.solution = problem['solution']
        self.fitness_target = self.maximum_fitness_target()

    def __str__(self):
        chromo = None if self.solution is None else [int(i) for i in self.solution]
        return f'\n  capacity: {self.capacity}\n' \
               f'  items(value, weight)): {", ".join([str(item) for item in self.items])}\n' \
               f'  solution: {None if chromo is None else Knapsack_Individual(chromo)}'

    def maximum_fitness_target(self):
        total_value = 0
        total_weight = 0
        for item in self.items:
            total_value += item.value
            total_weight += item.weight
            if total_weight >= self.capacity:
                total_value -= item.value
                total_weight -= item.weight
                avail_weight = self.capacity - total_weight
                pct_of_last = avail_weight/item.weight
                total_value += item.value*pct_of_last
                total_weight += item.weight*pct_of_last
                break
        # avg_density = total_value / total_weight
        # GA_World.fitness_target = floor(avg_density * capacity)
        fitness_target = floor(total_value)
        return fitness_target
        # print(total_value, total_weight, capacity, GA_World.fitness_target)



class Knapsack_Chromosome(Chromosome):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.

    """

    def __str__(self):
        return "".join([str(gene) for gene in self])

    def chromosome_fitness(self) -> float:
        items = Knapsack_World.problem.items
        return self.total_value(items)

    def total_value(self, items: List[Item]):
        total_val = sum([self[i] * items[i].value for i in range(len(self))])
        return total_val


class Knapsack_Individual(Individual):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_weight = None
        self.trim_chromosome()
        self.fitness = self.compute_fitness()

    def __eq__(self, other):
        return self.chromosome == other.chromosome

    def __str__(self):
        return f'{self.fitness}/{self.total_weight}<-{self.chromosome}'

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
        capacity = Knapsack_World.problem.capacity
        items = Knapsack_World.problem.items
        chromosome = self.chromosome
        self.total_weight = sum([chromosome[i] * items[i].weight for i in range(len(chromosome))])
        if self.total_weight <= capacity:
            return
        selected_indices = [i for i in range(len(chromosome)) if chromosome[i]]
        chromo_list = list(chromosome)
        shuffle(selected_indices)
        for i in selected_indices:
            self.total_weight -= items[i].weight
            chromo_list[i] = 0
            if self.total_weight <= capacity:
                break
        self.chromosome = Knapsack_Chromosome(chromo_list)


class Knapsack_World(GA_World):

    # problem is the user-selected problem
    problem: Knapsack_Problem = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cycle_length = SimEngine.gui_get('cycle_length')

    def gen_individual(self):
        # A Chromosome has as many positions as the problem has items.
        chromosome_list: List = [choice([0, 1]) for _ in range(len(Knapsack_World.problem.items))]
        chromosome = Knapsack_Chromosome(chromosome_list)
        individual = Knapsack_Individual(chromosome)
        return individual

    def set_results(self):
        super().set_results()
        print(f"{self.generations}) Pop (value/weight<-selection):  "
              f"{',  '.join([str(ind) for ind in self.population])}")
        print(f'{" "*(len(str(self.generations))+2)}Best (value/weight<-selection):  {self.best_ind}')
        if str(self.best_ind.chromosome) == Knapsack_World.problem.solution:
            self.done = True

    def setup(self):
        GA_World.individual_class = Knapsack_Individual
        GA_World.chromosome_class = Knapsack_Chromosome

        problem_name = SimEngine.gui_get('Problem')
        Knapsack_World.problem = Knapsack_Problem(problem_name)
        fitness_target = Knapsack_World.problem.fitness_target
        SimEngine.gui_set('fitness_target', value=f'{fitness_target}')
        GA_World.fitness_target = fitness_target
        print(f'\nNew Problem: {Knapsack_World.problem}')

        SimEngine.gui_set('Max generations', value=50)
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

knapsack_gui_left_upper = gui_left_upper + [
    [sg.Text('Prob invert selection', pad=((0, 5), (20, 0))),
     sg.Slider(key='invert selection', range=(0, 100), default_value=25, orientation='horizontal', size=(10, 20))
     ],

    [sg.Text('Problem selection', pad=(None, (20, 0))),
     sg.Combo(key='Problem', default_value=choice(Knapsack_Problem.problem_names), pad=((10, 0), (20, 0)),
              values=Knapsack_Problem.problem_names)
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
