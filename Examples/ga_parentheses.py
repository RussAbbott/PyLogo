
from collections import namedtuple
from itertools import count
from math import ceil
from random import choice, randint, sample
from typing import List, Sequence, Tuple

from pygame.color import Color

import core.gui as gui
from core.ga import Chromosome, GA_World, Individual, gui_left_upper
from core.sim_engine import SimEngine
from core.world_patch_block import World

Gene = namedtuple('Gene', ['id', 'val'])


class Parentheses_Chromosome(Chromosome):

    def compute_chromosome_fitness(self) -> float:
        """
        Compute the fitness based directly on the chromosome, which is all that matters.
        """
        errors = 0
        total = 0
        for i in range(len(self)):
            if self[i] == '(':
                total += 1
            # self[i] == ')'
            elif total == 0:
                errors += 1
            else:
                total -= 1
        fitness = total + errors
        return fitness

    def chromosome_string(self):
        return ''.join([str(gene.val) for gene in self])


class Parentheses_Individual(Individual):

    def __init__(self, chromosome: Sequence[Gene]):
        self.chromosome: Parentheses_Chromosome = Parentheses_Chromosome(chromosome)
        super().__init__(self.chromosome)

    def __str__(self):
        return f'{self.fitness}: ' \
               f'{self.chromosome.chromosome_string()}'

    def compute_fitness(self) -> float:
        fitness = self.chromosome.compute_chromosome_fitness()
        return fitness

    def mate_with(self, other):
        return self.cx_uniform(other)

    def mutate(self) -> Individual:
        chromosome = self.chromosome
        if randint(0, 100) <= SimEngine.gui_get('exchange_genes'):
        #     self.chromosome = self.chromosome.exchange_genes_in_chromosome()
        #
        # elif randint(0, 100) <= SimEngine.gui_get('move_ga_gene'):
        #     self.chromosome = self.chromosome.move_ga_gene()
        #
        # elif randint(0, 100) <= SimEngine.gui_get('move_gene'):
            self.chromosome = self.chromosome.move_gene()

        elif randint(0, 100) <= SimEngine.gui_get('reverse_subseq'):
            self.chromosome = self.chromosome.reverse_subseq(self.chromosome)

        self.chromosome = GA_World.chromosome_class(chromosome)

        self.fitness = self.chromosome.compute_chromosome_fitness()
        return self


class Parentheses_World(GA_World):
    
    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.chromosome_length = None

    @staticmethod
    def display_best_ind(best_ind: Parentheses_Individual):
        print(str(best_ind))
        # Parentheses_World.insert_chrom_and_sats(best_ind.chromosome, best_ind.satisfactions)

    def gen_individual(self):
        # Use ceil to ensure we have enough genes.
        lefts = ['(']*ceil(self.chromosome_length/2)
        rights = [')']*ceil(self.chromosome_length/2)
        mixture = sample(lefts + rights, self.chromosome_length)
        chromosome_list: Tuple[Gene] = Parentheses_World.chromosome_class(Gene(id, val) for (id, val) in zip(count(), mixture))
        individual = Parentheses_World.individual_class(Parentheses_World.chromosome_class(chromosome_list))
        return individual

    def set_results(self):
        """ Find and display the best individual. """
        super().set_results()
        print(str(self.best_ind))

    def setup(self):
        GA_World.individual_class = Parentheses_Individual
        GA_World.chromosome_class = Parentheses_Chromosome
        # GA_World.mating_op = Individual.cx_uniform
        self.chromosome_length = SimEngine.gui_get('chrom_length')
        super().setup()


# ########################################## Parameters for demos ######################################## #
patch_size = 11
board_size = 51

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
seg_gui_left_upper = gui_left_upper + [
                      [sg.Text('Move unhappy gene', pad=((0, 5), (20, 0))),
                       sg.Slider(key='move_paren_gene', range=(0, 100), default_value=5,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('Exchange two genes', pad=((0, 5), (20, 0))),
                       sg.Slider(key='exchange_genes', range=(0, 100), default_value=5,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('Fitness target', pad=((0, 5), (20, 0))),
                       sg.Slider(key='fitness_target', default_value=0, enable_events=True,
                                 orientation='horizontal', size=(10, 20), range=(0, 10))
                       ],

                      [sg.Text('Chromosome length', pad=(None, (20, 0))),
                       sg.Slider(key='chrom_length', range=(10, board_size), enable_events=True, size=(10, 20),
                                 pad=((10, 0), (0, 0)), orientation='horizontal', default_value=board_size)
                       ],

                         ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Parentheses_World, 'Parentheses', seg_gui_left_upper,
           patch_size=patch_size, board_rows_cols=(board_size, board_size))
