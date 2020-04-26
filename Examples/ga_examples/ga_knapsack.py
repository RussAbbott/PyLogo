
from __future__ import annotations

from math import floor
from random import choice, randint, shuffle
from typing import List

from core.ga import Chromosome, GA_World, Individual, gui_left_upper
from core.sim_engine import gui_get, gui_set


class Item:
    """ These are the items from which to select. """

    def __init__(self, value, weight):
        self.value = value
        self.weight = weight

    def __str__(self):
        return f'{self.value}/{self.weight}'
    
    
class Knapsack_Problem:
    
    # Every problem is a tuple: (capacity, items, solution (if known))

    # problems is a dictionary of problems.
    # Problem 1 is the example from the reading.
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
                'Problem 7': {'capacity': 15,
                              'items': [Item(5, 2), Item(12, 5), Item(7, 3), Item(9, 4), Item(12, 6),
                                        Item(14, 7), Item(6, 3), ],
                              'solution': '0111001'},
                'Random': None,
                }
    problem_names = list(problems.keys())
    
    def __init__(self, problem_name):
        problem = Knapsack_Problem.problems[problem_name]
        self.capacity = randint(10, 1000) if problem is None else problem['capacity']
        items = [Item(randint(1, 100), randint(1, 100)) for _ in range(randint(5, 50))] if problem is None else \
                problem['items']
        # Sort the items by density
        self.items = sorted(items, key=lambda item: item.value / item.weight, reverse=True)
        self.fitness_target = self.maximum_fitness_target()
        self.solution = f'<{self.fitness_target}>' if problem is None else problem['solution']

    def __str__(self):
        chromo = None if self.solution.startswith('<') else [int(i) for i in self.solution]
        return f'\n  Capacity: {self.capacity}\n' \
               f'  Items in density order (value/weight): {", ".join([str(item) for item in self.items])}\n' \
               f'  Solution: {self.solution if chromo is None else Knapsack_Individual(chromo)}'

    def generate_random_problem(self):
        self.capacity = randint(10, 1000)
        nbr_items = randint(5, 50)
        items = [Item(randint(1, 100), randint(1, 100)) for _ in range(nbr_items)]
        self.items = sorted(items, key=lambda item: item.value/item.weight, reverse=True)
        self.solution = None
        self.fitness_target = self.maximum_fitness_target()

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
        fitness_target = floor(total_value)
        return fitness_target



class Knapsack_Chromosome(Chromosome):
    """
    A Knapsack_Chromosome is a sequence of 1 and 0. Each position corresponds to one of the items
    in the problem. If the entry in position i is 1, the Individual is selcting that item. If
    it's 0, the Individual is not selecting that item.
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

        if randint(0, 100) <= gui_get('invert selection'):
            new_chromosome = self.chromosome.invert_a_gene()
            new_individual = GA_World.individual_class(new_chromosome)
            return new_individual
        else:
            return self

    def trim_chromosome(self):
        """ If the chromosome exceeds the problem capacity, remove items at random until it fits. """
        capacity = Knapsack_World.problem.capacity
        items = Knapsack_World.problem.items
        chromosome = self.chromosome
        self.total_weight = sum([chromosome[i] * items[i].weight for i in range(len(chromosome))])
        if self.total_weight <= capacity:
            return

        # Indices of selected items
        selected_indices = [i for i in range(len(chromosome)) if chromosome[i]]

        # shuffle reorders its argument randomly.
        # (It's not functional. It changes its argument.)
        shuffle(selected_indices)

        chromo_list = list(chromosome)
        for i in selected_indices:
            self.total_weight -= items[i].weight
            chromo_list[i] = 0
            if self.total_weight <= capacity:
                break
        self.chromosome = Knapsack_Chromosome(chromo_list)


class Knapsack_World(GA_World):

    # problem is the user-selected problem
    problem: Knapsack_Problem = None

    @staticmethod
    def gen_individual():
        # A Chromosome has as many positions as the problem has items.
        chromosome_list: List[int] = [choice([0, 1]) for _ in range(len(Knapsack_World.problem.items))]
        individual = Knapsack_Individual(chromosome_list)
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

        problem_name = gui_get('Problem')
        Knapsack_World.problem = Knapsack_Problem(problem_name)
        fitness_target = Knapsack_World.problem.fitness_target
        gui_set('fitness_target', value=fitness_target)
        GA_World.fitness_target = fitness_target
        print(f'\n{problem_name}: {Knapsack_World.problem}')

        gui_set('Max generations', value=250)
        super().setup()

    @staticmethod
    def sort_population(population):
        return sorted(population, key=lambda i: (i.fitness, -i.total_weight), reverse=True)


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
