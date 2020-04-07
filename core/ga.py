
from __future__ import annotations

from random import choice, randint, sample
from typing import Any, NewType, Optional, Sequence, Tuple

from core.sim_engine import SimEngine
from core.world_patch_block import World

Gene = NewType('Gene', Any)
Chromosome = NewType('Chromosome', Tuple[Gene])


class Individual:
    """
    Note: An individual is NOT an agent. Individual is a separate, stand-alone class.

    An individual is a sequence of chromosome. The chromosome are typically all of the same type, e.g.,
    a integer, a pixel, etc. The sequence is stored as a tuple to ensure that it is immutable.

    In loop.py points on the screen, i.e., Pixel_xy objects, are the chromosome. As far as PyLogo is
    concerned, they are agents. They serve as chromosome in individuals.
    """

    def __init__(self, chromosome: Sequence[Gene]):
        self.chromosome: Chromosome = chromosome if isinstance(chromosome, tuple) else \
                                      GA_World.seq_to_chromosome(chromosome)
        # No need to compute fitness multiple times. Cache it here.
        # if isinstance(self.chromosome, list):
        #     print('list')
        self.fitness = self.compute_fitness()

    def compute_fitness(self):
        pass

    @staticmethod
    def cx_all_diff(ind_1, ind_2) -> Tuple[Individual, Individual]:
        """
        Perform crossover between self and other while preserving all_different.
        """
        child_1 = GA_World.individual_class(Individual.cx_all_diff_chromosome(ind_1.chromosome, ind_2.chromosome))
        child_2 = GA_World.individual_class(Individual.cx_all_diff_chromosome(ind_2.chromosome, ind_1.chromosome))
        return (child_1, child_2)

    @staticmethod
    def cx_all_diff_chromosome(chromosome_1: Chromosome, chromosome_2: Chromosome) -> Chromosome:
        """
        chromosome_1 and chromosome_2 are the same length

        Returns: a selection from chromosome_1 and chromosome_2 preserving all_different
        """
        # This ensures that the rotations are non-trivial.
        inner_indices = range(1, len(chromosome_1)-1) if len(chromosome_1) > 2 else range(len(chromosome_1))
        chromosome_1_rotated: Chromosome = Individual.rotate_by(chromosome_1, choice(inner_indices))
        chromosome_2_rotated: Chromosome = Individual.rotate_by(chromosome_2, choice(inner_indices))
        indx = choice(inner_indices)

        child_chromosome_start: Chromosome = chromosome_1_rotated[:indx]
        child_chromosome_end: Chromosome = GA_World.seq_to_chromosome([gene for gene in chromosome_2_rotated
                                                                        if gene not in child_chromosome_start])

        child_chromosome: Chromosome = Chromosome(child_chromosome_start + child_chromosome_end)
        return child_chromosome[:len(chromosome_1)]

    @property
    def discrepancy(self):
        discr = abs(self.fitness - GA_World.fitness_target)
        return discr

    def mate_with(self, other) -> Tuple[Individual, Individual]:
        pass

    def mutate(self) -> Individual:
        pass

    # @staticmethod
    # def move_elt(chromosome: Chromosome):
    #     """
    #     This is our own mutation operator. It moves an Gene from one place to another in the list.
    #     """
    #     # Ensures that the two index positions are different.
    #     (indx_1, indx_2) = sample(list(range(len(chromosome))), 2)
    #     # Can't perform the next line on a tuple. So change it into
    #     # a list and then change it back into a tuple. That way the
    #     # original tuple is unchanged.
    #     list_chromosome: List[Gene] = list(chromosome)
    #     list_chromosome.insert(indx_2, list_chromosome.pop(indx_1))
    #     return GA_World.seq_to_chromosome(list_chromosome)
    #
    @staticmethod
    def reverse_subseq(chromosome):
        """
        This mutation operator swaps two chromosome.
        """
        # Ensure that the two index positions are different.
        (indx_1, indx_2) = sorted(sample(list(range(len(chromosome))), 2))
        list_chromosome = list(chromosome)
        list_chromosome[indx_1:indx_2] = reversed(list_chromosome[indx_1:indx_2])
        return GA_World.seq_to_chromosome(list_chromosome)

    @staticmethod
    def rotate_by(chromosome: Chromosome, amt: int) -> Chromosome:
        return chromosome[amt:] + chromosome[:amt]


class GA_World(World):
    """
    The Population holds the collection of Individuals that will undergo evolution.
    """
    fitness_target = None
    individual_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.best_ind: Optional[Individual] = None
        self.generations = None
        self.mating_op = None
        self.pop_size = None
        self.tournament_size = None

        self.BEST = 'best'
        self.WORST = 'worst'

    def generate_children(self):
        parent_1 = self.gen_parent()
        parent_2 = self.gen_parent()
        (child_1, child_2) = parent_1.mate_with(parent_2)
        child_1_mutated: Individual = child_1.mutate()
        child_2_mutated: Individual = child_2.mutate()

        child_1_mutated.compute_fitness()
        child_2_mutated.compute_fitness()

        dest_1_indx = self.select_gene_index(self.WORST, self.tournament_size)
        dest_2_indx = self.select_gene_index(self.WORST, self.tournament_size)
        self.individuals[dest_1_indx] = child_1_mutated
        self.individuals[dest_2_indx] = child_2_mutated

    def gen_individual(self):
        pass

    def gen_parent(self):
        if randint(0, 99) < SimEngine.gui_get('prob_random_parent'):
            parent = self.gen_individual()
            # if isinstance(parent.chromosome, list):
            #     print('list')
        else:
            parent_indx = self.select_gene_index(self.BEST, self.tournament_size)
            parent = self.individuals[parent_indx]
            # if isinstance(parent.chromosome, list):
            #     print('list')
        return parent

    def get_best_individual(self):
        best_index = self.select_gene_index(self.BEST, len(self.individuals))
        best_individual = self.individuals[best_index]
        return best_individual

    def handle_event(self, event):
        if event == 'fitness_target':
            GA_World.fitness_target = SimEngine.gui_get('fitness_target')
            return
        super().handle_event(event)

    def initial_individuals(self):
        pass

    def select_gene_index(self, best_or_worst, tournament_size) -> int:
        min_or_max = min if best_or_worst == self.BEST else max
        candidate_indices = sample(range(len(self.individuals)), tournament_size)
        selected_index = min_or_max(candidate_indices, key=lambda i: self.individuals[i].discrepancy)
        return selected_index

    @staticmethod
    def seq_to_chromosome(lst: Sequence[Gene]) -> Chromosome:
        return Chromosome(tuple(lst))

    def set_results(self):
        current_best_ind = self.get_best_individual()
        if self.best_ind is None or current_best_ind.discrepancy < self.best_ind.discrepancy:
            self.best_ind = current_best_ind
        SimEngine.gui_set('best_fitness', value=round(self.best_ind.fitness, 1))
        SimEngine.gui_set('discrepancy', value=round(self.best_ind.discrepancy, 1))
        SimEngine.gui_set('generations', value=self.generations)

    # noinspection PyAttributeOutsideInit
    def setup(self):
        # Create a list of Individuals as the initial population.
        self.pop_size = SimEngine.gui_get('pop_size')
        self.tournament_size = SimEngine.gui_get('tourn_size')
        GA_World.fitness_target = SimEngine.gui_get('fitness_target')
        self.individuals = self.initial_individuals()
        self.best_ind = None
        self.generations = 0
        self.set_results()

    def step(self):
        if self.best_ind and self.best_ind.discrepancy == 0:
            return

        for i in range(self.pop_size//2):
            # print(i)
            self.generate_children()

        self.generations += 1
        self.set_results()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [

                   [sg.Text('Best:', pad=(None, (0, 0))),
                    sg.Text('     0.0', key='best_fitness', pad=(None, (0, 0))),
                    sg.Text('Discrepancy:', pad=((20, 0), (0, 0))),
                    sg.Text('      .0', key='discrepancy', pad=(None, (0, 0)))],

                   [sg.Text('Generations:', pad=((0, 0), (0, 0))),
                    sg.Text('000000000', key='generations', pad=(None, (0, 0))),
                    ],

                   [sg.Text('Population size', pad=((0, 5), (20, 0))),
                    sg.Slider(key='pop_size', range=(10, 500), resolution=10, default_value=100,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Nbr points', pad=((0, 5), (10, 0))),
                    sg.Slider(key='nbr_points', range=(10, 200), default_value=100,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Tournament size', pad=((0, 5), (10, 0))),
                    sg.Slider(key='tourn_size', range=(3, 15), resolution=1, default_value=7,
                              orientation='horizontal', size=(10, 20))
                    ],

                   # [sg.Text('Prob move elt', pad=((0, 5), (20, 0))),
                   #  sg.Slider(key='move_elt_internally', range=(0, 100), default_value=20,
                   #            orientation='horizontal', size=(10, 20))
                   #  ],
                   #
                   [sg.Text('Prob reverse sublist', pad=((0, 5), (20, 0))),
                    sg.Slider(key='reverse_subseq', range=(0, 100), default_value=20,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob random parent', pad=((0, 5), (20, 0))),
                    sg.Slider(key='prob_random_parent', range=(0, 100), default_value=35,
                              orientation='horizontal', size=(10, 20))
                    ],

                   ]
