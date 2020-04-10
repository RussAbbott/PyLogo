
from collections import namedtuple
from itertools import count
from random import choice, randint, sample
from typing import List, Tuple

from core.ga import Chromosome, GA_World, Individual, gui_left_upper
from core.sim_engine import SimEngine

Gene = namedtuple('Gene', ['id', 'val'])


class Segregation_Individual(Individual):

    def __init__(self, *args, **kwargs):
        self.satisfactions = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        sats = self.satisfactions
        return f'{self.fitness}: {Segregation_Individual.chrom_to_string(self.chromosome)}\n' \
               f'{" "*len(str(self.fitness))}  {"".join([" " if sats[i] else "^" for i in range(len(sats))])}'

    @staticmethod
    def chrom_to_string(chromosome):
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
    def exchange_genes_in_chromosome(chromosome, satisfactions) -> Tuple[Chromosome, int, List[bool]]:
        len_chrom = len(chromosome)
        unhappy_zero_indices = Segregation_Individual.unhappy_elements(0, chromosome, satisfactions, len_chrom)
        unhappy_one_indices = Segregation_Individual.unhappy_elements(1, chromosome, satisfactions, len_chrom)
        if not unhappy_zero_indices:
            unhappy_zero_indices = list(range(len_chrom))
        if not unhappy_one_indices:
            unhappy_one_indices = list(range(len_chrom))
        (zero_index, one_index) = (choice(unhappy_zero_indices), choice(unhappy_one_indices))
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

    def mutate(self) -> Individual:
        if randint(0, 100) <= SimEngine.gui_get('exchange_genes'):
            (self.chromosome, self.fitness, self.satisfactions) = \
                self.exchange_genes_in_chromosome(self.chromosome, self.satisfactions)

        elif randint(0, 100) <= SimEngine.gui_get('reverse_subseq'):
            self.chromosome = self.reverse_subseq(self.chromosome)
            (self.satisfactions, self.fitness) = self.compute_chromosome_fitness(self.chromosome)

        elif randint(0, 100) <= SimEngine.gui_get('move_gene'):
            self.chromosome = self.move_gene(self.chromosome)
            (self.satisfactions, self.fitness) = self.compute_chromosome_fitness(self.chromosome)

        return self

    @staticmethod
    def unhappy_elements(value, chromosome, satisfactions, length):
        unhappy_indices = [i for i in range(length) if chromosome[i].val == value and not satisfactions[i]]
        return unhappy_indices


class Segregation_World(GA_World):
    
    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.chromosome_length = None

    def gen_individual(self):
        zeros = [0]*(self.chromosome_length//2)
        ones = [1]*(self.chromosome_length//2)
        mixture = sample(zeros + ones, self.chromosome_length)
        chromosome_list: Tuple[Gene] = tuple(Gene(id, val) for (id, val) in zip(count(), mixture))
        individual = Segregation_World.individual_class(Segregation_World.seq_to_chromosome(chromosome_list))
        return individual

    def initial_individuals(self) -> List[Segregation_Individual]:
        individuals = [self.gen_individual() for _ in range(self.pop_size)]
        # Individual.count = self.pop_size
        return individuals

    def set_results(self):
        super().set_results()
        print(str(self.best_ind))

    def setup(self):
        GA_World.individual_class = Segregation_Individual
        self.chromosome_length = SimEngine.gui_get('chrom_length')
        self.mating_op = Individual.cx_all_diff
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
seg_gui_left_upper = gui_left_upper + [
                      [sg.Text('Exchange two genes', pad=((0, 5), (20, 0))),
                       sg.Slider(key='exchange_genes', range=(0, 100), default_value=95,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('fitness_target', pad=((0, 5), (20, 0))),
                       sg.Slider(key='fitness_target', default_value=0, enable_events=True,
                                 orientation='horizontal', size=(10, 20), range=(0, 10))
                       ],

                      [sg.Text('Chromosome length', pad=(None, (20, 0))),
                       sg.Slider(key='chrom_length', range=(10, 500), default_value=100, pad=((10, 0), (0, 0)),
                                 orientation='horizontal', size=(10, 20), enable_events=True)
                       ],

                         ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Segregation_World, 'GA Segregation', seg_gui_left_upper)
