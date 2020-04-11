
from collections import namedtuple
from itertools import count
from random import choice, randint, sample
from typing import List, Tuple

from pygame.color import Color
from core.ga import Chromosome, GA_World, Individual, gui_left_upper
import core.gui as gui
from core.sim_engine import SimEngine
from core.world_patch_block import World


Gene = namedtuple('Gene', ['id', 'val'])


class Segregation_Individual(Individual):

    def __init__(self, *args, **kwargs):
        self.satisfactions = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        # sats = self.satisfactions
        return f'{self.fitness}: ' \
               f'{Segregation_Individual.chromosome_string(self.chromosome)}' \
               f'\n' \
               f'{" "*len(str(self.fitness))}  {Segregation_Individual.satisfactions_string(self.satisfactions)}'

    @staticmethod
    def chromosome_string(chromosome):
        return ''.join([str(gene.val) for gene in chromosome])

    def compute_fitness(self) -> float:
        (self.satisfactions, fitness) = Segregation_Individual.compute_chromosome_fitness(self.chromosome)
        return fitness

    @staticmethod
    def compute_chromosome_fitness(chromosome) -> Tuple[List[bool], int]:
        len_chrom = len(chromosome)
        # Recall that a chromosome is a tuple of Genes, each of which is a Gene(id, val), where val 0 or 1.
        satisfactions = [Segregation_Individual.is_happy(i, chromosome, len_chrom) for i in range(len_chrom)]
        fitness = len_chrom - sum(satisfactions)
        return (satisfactions, fitness)

    @staticmethod
    def element_indices(value, chromosome, length):
        unhappy_indices = [i for i in range(length) if chromosome[i].val == value]
        return unhappy_indices

    @staticmethod
    def exchange_genes_in_chromosome(chromosome, satisfactions) -> Tuple[Chromosome, int, List[bool]]:
        len_chrom = len(chromosome)
        candidate_zero_indices = Segregation_Individual.unhappy_element_indices(0, chromosome, satisfactions, len_chrom)
        candidate_one_indices = Segregation_Individual.unhappy_element_indices(1, chromosome, satisfactions, len_chrom)
        if not candidate_zero_indices:
            candidate_zero_indices = Segregation_Individual.element_indices(0, chromosome, len_chrom)
        if not candidate_one_indices:
            candidate_one_indices = Segregation_Individual.element_indices(1, chromosome, len_chrom)
        (zero_index, one_index) = (choice(candidate_zero_indices), choice(candidate_one_indices))
        c_list: List[int] = list(chromosome)
        (c_list[zero_index], c_list[one_index]) = (c_list[one_index], c_list[zero_index])
        # noinspection PyTypeChecker
        new_chrom: Chromosome = Chromosome(tuple(c_list))
        (satisfactions, new_fitness) = Segregation_Individual.compute_chromosome_fitness(new_chrom)
        return (new_chrom, new_fitness, satisfactions)

    @staticmethod
    def is_happy(i, chrom, len_chrom):
        """
        Is chrom[i] happy?
        It is happy if at least 2 of the four elements on either side (2 on each side) have the same value.
        """
        neigh_indices = [p for p in range(i-2, i+3) if p != i]
        # We use mod (%) so that we can wrap around. (Negatve wrap-around is automatic!)
        matches = [1 if chrom[p % len_chrom].val == chrom[i].val else -1 for p in neigh_indices]
        happy = sum(matches) >= 0
        return happy

    def mate_with(self, other):
        return self.cx_all_diff(self, other)

    @staticmethod
    def move_ga_gene(chromosome, satisfactions):
        """
        This mutation operator moves a gene from one place to another.
        This version selects a "bad" gene to move.
        """
        candidate_indices = Segregation_Individual.unhappy_elements_indices(satisfactions)
        if not candidate_indices:
            return chromosome
        from_index = choice(candidate_indices)
        to_index = choice(range(len(chromosome)))
        list_chromosome: List[Gene] = list(chromosome)
        gene_to_move: Gene = list_chromosome[from_index]
        revised_list: List[Gene] = list_chromosome[:from_index] + list_chromosome[from_index+1:]
        revised_list.insert(to_index, gene_to_move)
        return GA_World.seq_to_chromosome(revised_list)

    def mutate(self) -> Individual:
        if randint(0, 100) <= SimEngine.gui_get('exchange_genes'):
            (self.chromosome, self.fitness, self.satisfactions) = \
                self.exchange_genes_in_chromosome(self.chromosome, self.satisfactions)

        elif randint(0, 100) <= SimEngine.gui_get('move_ga_gene'):
            self.chromosome = self.move_ga_gene(self.chromosome, self.satisfactions)
            (self.satisfactions, self.fitness) = self.compute_chromosome_fitness(self.chromosome)

        elif randint(0, 100) <= SimEngine.gui_get('move_gene'):
            self.chromosome = self.move_gene(self.chromosome)
            (self.satisfactions, self.fitness) = self.compute_chromosome_fitness(self.chromosome)

        elif randint(0, 100) <= SimEngine.gui_get('reverse_subseq'):
            self.chromosome = self.reverse_subseq(self.chromosome)
            (self.satisfactions, self.fitness) = self.compute_chromosome_fitness(self.chromosome)

        return self

    @staticmethod
    def satisfactions_string(satisfactions: List[bool]):
        return f'{"".join([" " if satisfactions[i] else "^" for i in range(len(satisfactions))])}'

    def set_best_rotation(self):
        best_rotation = self.chromosome
        best_chrom_string = Segregation_Individual.chromosome_string(best_rotation)
        rotation_amt = 0
        for i in range(1, len(best_rotation)):
            rotation = Individual.rotate_by(self.chromosome, i)
            chrom_string_r = Segregation_Individual.chromosome_string(rotation)
            if chrom_string_r < best_chrom_string:
                best_rotation = rotation
                best_chrom_string = chrom_string_r
                rotation_amt = i
        self.chromosome = best_rotation
        self.satisfactions = Individual.rotate_by(self.satisfactions, rotation_amt)

    @staticmethod
    def unhappy_element_indices(value, chromosome, satisfactions, length):
        unhappy_indices = [i for i in range(length) if chromosome[i].val == value and not satisfactions[i]]
        return unhappy_indices

    @staticmethod
    def unhappy_elements_indices(satisfactions):
        unhappy_indices = [i for i in range(len(satisfactions)) if not satisfactions[i]]
        return unhappy_indices


class Segregation_World(GA_World):
    
    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.chromosome_length = None

    def display_best_ind(self):
        best_ind = self.best_ind
        best_ind.set_best_rotation()
        print(str(best_ind))
        self.insert_window()

    def gen_individual(self):
        zeros = [0]*(self.chromosome_length//2+2)
        ones = [1]*(self.chromosome_length//2+2)
        mixture = sample(zeros + ones, self.chromosome_length)
        chromosome_list: Tuple[Gene] = tuple(Gene(id, val) for (id, val) in zip(count(), mixture))
        individual = Segregation_World.individual_class(Segregation_World.seq_to_chromosome(chromosome_list))
        return individual

    def initial_individuals(self) -> List[Segregation_Individual]:
        individuals = [self.gen_individual() for _ in range(self.pop_size)]
        # Individual.count = self.pop_size
        return individuals

    def insert_window(self, window_rows=3):
        for i in range(0, gui.PATCH_ROWS, window_rows):
            for r in range(window_rows):
                if i + r + window_rows < gui.PATCH_ROWS:
                    for c in range(gui.PATCH_COLS):
                        World.patches_array[i+r, c].set_color(World.patches_array[i+r+window_rows, c].color)

        chrom_string = Segregation_Individual.chromosome_string(self.best_ind.chromosome)
        blue = Color('slateblue2')
        yellow = Color('yellow')
        for c in range(len(chrom_string)):
            World.patches_array[gui.PATCH_ROWS-3, c].set_color(yellow if chrom_string[c] == '1' else blue)
        sats = self.best_ind.satisfactions
        red = Color('red')
        black = Color('black')
        for c in range(len(sats)):
            World.patches_array[gui.PATCH_ROWS-2, c].set_color(black if sats[c] else red)

    def set_results(self):
        super().set_results()
        self.display_best_ind()

    def setup(self):
        GA_World.individual_class = Segregation_Individual
        self.chromosome_length = SimEngine.gui_get('chrom_length')
        self.mating_op = Individual.cx_all_diff
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
seg_gui_left_upper = gui_left_upper + [
                      [sg.Text('Move unhappy gene', pad=((0, 5), (20, 0))),
                       sg.Slider(key='move_ga_gene', range=(0, 100), default_value=30,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('Exchange two genes', pad=((0, 5), (20, 0))),
                       sg.Slider(key='exchange_genes', range=(0, 100), default_value=0,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('fitness_target', pad=((0, 5), (20, 0))),
                       sg.Slider(key='fitness_target', default_value=0, enable_events=True,
                                 orientation='horizontal', size=(10, 20), range=(0, 10))
                       ],

                      [sg.Text('Chromosome length', pad=(None, (20, 0))),
                       sg.Slider(key='chrom_length', range=(10, 250), default_value=200, pad=((10, 0), (0, 0)),
                                 orientation='horizontal', size=(10, 20), enable_events=True)
                       ],

                         ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Segregation_World, 'GA Segregation', seg_gui_left_upper,
           patch_size=3, board_rows_cols=(200, 200))
