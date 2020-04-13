
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


class Segregation_Chromosome(Chromosome):

    def compute_chromosome_fitness(self) -> Tuple[List[bool], int]:
        len_chrom = len(self)
        # A chromosome is a tuple of Genes, each of which is a Gene(id, val), where val 0 or 1.
        satisfactions = [self.is_happy(i, len_chrom) for i in range(len_chrom)]
        fitness = len_chrom - sum(satisfactions)
        return (satisfactions, fitness)

    def chromosome_string(self):
        return ''.join([str(gene.val) for gene in self])

    def exchange_genes_in_chromosome(self, satisfactions) -> Tuple[Chromosome, int, List[bool]]:
        len_chrom = len(self)
        candidate_zero_indices = self.unhappy_value_indices(0, satisfactions, len_chrom)
        if not candidate_zero_indices:
            return self
        candidate_one_indices = self.unhappy_value_indices(1, satisfactions, len_chrom)
        if not candidate_one_indices:
            return self

        (zero_index, one_index) = (choice(candidate_zero_indices), choice(candidate_one_indices))

        c_list: List[int] = list(self)
        (c_list[zero_index], c_list[one_index]) = (c_list[one_index], c_list[zero_index])

        # noinspection PyTypeChecker
        # new_chrom: Chromosome = GA_World.chromosome_class(c_list)
        return c_list

    def gene_value_indices(self, value, length):
        indices = [i for i in range(length) if self[i].val == value]
        return indices

    def is_happy(self, i, len_chrom):
        """
        Is chrom[i] happy?
        It is happy if at least 2 of the four elements on either side (2 on each side) have the same value.
        """
        neigh_indices = [p for p in range(i-2, i+3) if p != i]
        # Use mod (%) so that we can wrap around. (Negatve wrap-around is automatic!)
        matches = [1 if self[p % len_chrom].val == self[i].val else -1 for p in neigh_indices]
        happy = sum(matches) >= 0
        return happy

    def unhappy_value_indices(self, value, satisfactions, length):
        unhappy_indices = [i for i in range(length) if self[i].val == value and not satisfactions[i]]
        return unhappy_indices


class Segregation_Individual(Individual):

    def __init__(self, chromosome: Sequence[Gene]):
        self.satisfactions = None
        self.chromosome: Segregation_Chromosome = Segregation_Chromosome(chromosome)
        super().__init__(self.chromosome)

    def __str__(self):
        return f'{self.fitness}: ' \
               f'{self.chromosome.chromosome_string()}' \
               f'\n' \
               f'{" "*len(str(self.fitness))}  {Segregation_Individual.satisfactions_string(self.satisfactions)}'

    def compute_fitness(self) -> float:
        (self.satisfactions, fitness) = self.chromosome.compute_chromosome_fitness()
        return fitness

    def mate_with(self, other):
        return self.cx_all_diff(self, other)

    @staticmethod
    def move_ga_gene(chromosome, satisfactions):
        """
        This mutation operator moves a gene from one place to another.
        This version selects an unhappy gene to move.
        """
        candidate_indices = Segregation_Individual.unhappy_gene_value_indices(satisfactions)
        if not candidate_indices:
            return chromosome
        from_index = choice(candidate_indices)
        to_index = choice(range(len(chromosome)))
        list_chromosome: List[Gene] = list(chromosome)
        gene_to_move: Gene = list_chromosome[from_index]
        revised_list: List[Gene] = list_chromosome[:from_index] + list_chromosome[from_index+1:]
        revised_list.insert(to_index, gene_to_move)
        # return GA_World.chromosome_class(revised_list)
        return revised_list

    def mutate(self) -> Individual:
        chromosome = self.chromosome
        if randint(0, 100) <= SimEngine.gui_get('exchange_genes'):
            assert isinstance(self.chromosome, Segregation_Chromosome)
            chromosome = chromosome.exchange_genes_in_chromosome(self.satisfactions)

        elif randint(0, 100) <= SimEngine.gui_get('move_ga_gene'):
            chromosome = Segregation_Individual.move_ga_gene(chromosome, self.satisfactions)

        elif randint(0, 100) <= SimEngine.gui_get('move_gene'):
            chromosome = Individual.move_gene(chromosome)

        elif randint(0, 100) <= SimEngine.gui_get('reverse_subseq'):
            chromosome = Individual.reverse_subseq(chromosome)

        self.chromosome = GA_World.chromosome_class(chromosome)

        (self.satisfactions, self.fitness) = self.chromosome.compute_chromosome_fitness()
        return self

    @staticmethod
    def satisfactions_string(satisfactions: List[bool]):
        return f'{"".join([" " if satisfactions[i] else "^" for i in range(len(satisfactions))])}'

    @staticmethod
    def unhappy_gene_value_indices(satisfactions):
        unhappy_indices = [i for i in range(len(satisfactions)) if not satisfactions[i]]
        return unhappy_indices



class Segregation_World(GA_World):

    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.chromosome_length = None

    @staticmethod
    def display_best_ind(best_ind: Segregation_Individual):
        # best_ind.set_best_rotation()
        # print(str(best_ind))
        Segregation_World.insert_chrom_and_sats(best_ind.chromosome, best_ind.satisfactions)

    def gen_individual(self):
        # Use ceil to ensure we have enough genes.
        zeros = [0]*ceil(self.chromosome_length/2)
        ones = [1]*ceil(self.chromosome_length/2)
        mixture = sample(zeros + ones, self.chromosome_length)
        chromosome_tuple: Tuple[Gene] = GA_World.chromosome_class(Gene(id, val) for (id, val) in zip(count(), mixture))
        individual = GA_World.individual_class(chromosome_tuple)
        return individual

    @staticmethod
    def insert_chrom_and_sats(chromosome, satisfactions, window_rows=2):
        """ Scroll the screen and insert the current best chromosome with unhappy genes indicated. """
        Segregation_World.scroll_window(window_rows)

        chrom_string = chromosome.chromosome_string()
        green = Color('springgreen3')
        yellow = Color('yellow')
        indentation = (gui.PATCH_COLS - len(chrom_string))//2
        for c in range(len(chrom_string)):
            World.patches_array[gui.PATCH_ROWS-2, indentation+c].set_color(yellow if chrom_string[c] == '1' else green)
        red = Color('red')
        black = Color('black')
        for c in range(len(satisfactions)):
            World.patches_array[gui.PATCH_ROWS-1, indentation+c].set_color(black if satisfactions[c] else red)

    @staticmethod
    def scroll_window(window_rows):
        """ Scroll the screen up by window-rows lines """
        for i in range(0, gui.PATCH_ROWS, window_rows):
            for r in range(window_rows):
                if i + r + window_rows < gui.PATCH_ROWS:
                    for c in range(gui.PATCH_COLS):
                        World.patches_array[i + r, c].set_color(World.patches_array[i + r + window_rows, c].color)

    def set_results(self):
        """ Find and display the best individual. """
        super().set_results()
        # noinspection PyTypeChecker
        Segregation_World.display_best_ind(self.best_ind)

    def setup(self):
        GA_World.individual_class = Segregation_Individual
        GA_World.chromosome_class = Segregation_Chromosome
        self.chromosome_length = SimEngine.gui_get('chrom_length')
        self.mating_op = Individual.cx_all_diff
        super().setup()


# ########################################## Parameters for demos ######################################## #
demo = 'large'
# demo = 'small'
patch_size = 3 if demo == 'large' else 11
board_size = 201 if demo == 'large' else 51

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
seg_gui_left_upper = gui_left_upper + [
                      [sg.Text('Move unhappy gene', pad=((0, 5), (20, 0))),
                       sg.Slider(key='move_ga_gene', range=(0, 100), default_value=5,
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
    PyLogo(Segregation_World, 'GA Segregation', seg_gui_left_upper,
           patch_size=patch_size, board_rows_cols=(board_size, board_size))
