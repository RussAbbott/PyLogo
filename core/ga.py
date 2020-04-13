
# This allows us to use the type Individual within the Individual class.
from __future__ import annotations

from random import choice, randint, sample
from typing import Any, List, NewType, Sequence, Tuple

import core.gui as gui
from core.gui import GOSTOP, GO_ONCE
from core.sim_engine import SimEngine
from core.world_patch_block import World

# Create a Gene type for pre-execution type checking.
# This will be "overridden" in ga_segregation.
Gene = NewType('Gene', Any)


class Chromosome(tuple):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.

    """

    def chromosome_fitness(self) -> float:
        pass

        # len_chrom = len(self)
        # # A chromosome is a tuple of Genes, each of which is a Pixel_xy. We use mod (%)
        # # so that we can include the distance from chromosome[len_chrom - 1] to chromosome[0]
        # distances = [self[i].distance_to(self[(i+1) % len_chrom]) for i in range(len_chrom)]
        # fitness = sum(distances)
        # return fitness

    def cx_all_diff_chromosome(self: Chromosome, other_chromosome: Chromosome) -> Chromosome:
        """
        chromosome_1 and other_chromosome are the same length.
        chromosome_1 is self

        Returns: a selection from chromosome_1 and other_chromosome preserving all_different
        """
        # This ensures that the rotations are non-trivial.
        inner_indices = range(1, len(self) - 1) if len(self) > 2 else range(len(self))
        self_rotated: Chromosome = self.rotate_by(choice(inner_indices))
        other_chromosome_rotated: Chromosome = other_chromosome.rotate_by(choice(inner_indices))
        indx = choice(inner_indices)

        child_chromosome_start: Chromosome = self_rotated[:indx]
        child_chromosome_end = tuple(gene for gene in other_chromosome_rotated
                                                                     if gene not in child_chromosome_start)

        child_chromosome: Chromosome = GA_World.chromosome_class(child_chromosome_start + child_chromosome_end)
        return child_chromosome[:len(self)]

    def move_gene(self) -> Sequence:
        """
        This mutation operator moves a gene from one place to another.
        """
        (from_index, to_index) = sorted(sample(list(range(len(self))), 2))
        list_chromosome: List[Gene] = list(self)
        gene_to_move: Gene = list_chromosome[from_index]
        revised_list: List[Gene] = list_chromosome[:from_index] + list_chromosome[from_index+1:]
        revised_list.insert(to_index, gene_to_move)
        # return GA_World.chromosome_class(revised_list)
        return revised_list

    def reverse_subseq(self: Chromosome) -> Sequence:
        """ Reverse a subsequence of this chromosome. """
        # Ensure that the two index positions are different.
        (indx_1, indx_2) = sorted(sample(list(range(len(self))), 2))
        list_chromosome = list(self)
        list_chromosome[indx_1:indx_2] = reversed(list_chromosome[indx_1:indx_2])
        # return GA_World.chromosome_class(list_chromosome)
        return list_chromosome

    def rotate_by(self, amt: int) -> Chromosome:
        return GA_World.chromosome_class(self[amt:] + self[:amt])


class Individual:
    """
    Note: An Individual is NOT an agent. Individual is a separate, stand-alone class.

    An Individual consists of a chromosome and a fitness. 
    The chromosome is a sequence of Genes. (See type definitions above.) 
    A chromosomes is stored as a tuple (reather than a list) to ensure that it is immutable.
    """
    def __init__(self, chromosome: Sequence[Gene] = None):
        self.chromosome: Chromosome = GA_World.chromosome_class(chromosome)
        self.fitness = self.compute_fitness()

    def compute_fitness(self) -> float:
        pass

    @staticmethod
    def cx_all_diff(ind_1, ind_2) -> Tuple[Individual, Individual]:
        """
        Perform crossover between self and other while preserving all_different.
        """
        child_1 = GA_World.individual_class((ind_1.chromosome).cx_all_diff_chromosome(ind_2.chromosome))
        child_2 = GA_World.individual_class((ind_2.chromosome).cx_all_diff_chromosome(ind_1.chromosome))
        return (child_1, child_2)

    @property
    def discrepancy(self) -> float:
        discr = abs(self.fitness - GA_World.fitness_target)
        return discr

    def mate_with(self, other) -> Tuple[Individual, Individual]:
        pass

    def mutate(self) -> Individual:
        pass

    # @staticmethod
    # def rotate_by(chromosome: Chromosome, amt: int) -> Chromosome:
    #     return chromosome[amt:] + chromosome[:amt]
    #


class GA_World(World):
    """
    The Population holds the collection of Individuals that will undergo evolution.
    """
    fitness_target = None
    individual_class = Individual
    chromosome_class = Chromosome

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # noinspection PyTypeChecker
        self.best_ind: Individual = None
        self.generations = None
        self.pop_size = None
        # noinspection PyTypeChecker
        self.population: List[Individual] = None

        self.mating_op = None
        self.tournament_size = None

        self.BEST = 'best'
        self.WORST = 'worst'

    # noinspection PyNoneFunctionAssignment
    def generate_2_children(self):
        """ Generate two children and put them into the population. """
        parent_1 = self.get_parent()
        parent_2 = self.get_parent()
        (child_1, child_2) = parent_1.mate_with(parent_2)
        child_1_mutated: Individual = child_1.mutate()
        child_2_mutated: Individual = child_2.mutate()

        child_1_mutated.compute_fitness()
        child_2_mutated.compute_fitness()

        dest_1_indx: int = self.select_gene_index(self.WORST, self.tournament_size)
        dest_2_indx: int = self.select_gene_index(self.WORST, self.tournament_size)
        # noinspection PyTypeChecker
        self.population[dest_1_indx] = min([child_1, child_1_mutated], key=lambda c: c.discrepancy)
        # noinspection PyTypeChecker
        self.population[dest_2_indx] = min([child_2, child_2_mutated], key=lambda c: c.discrepancy)

    def gen_individual(self) -> Individual:
        pass

    def get_best_individual(self) -> Individual:
        best_index = self.select_gene_index(self.BEST, len(self.population))
        best_individual = self.population[best_index]
        return best_individual

    def get_parent(self) -> Individual:
        if randint(0, 99) < SimEngine.gui_get('prob_random_parent'):
            parent = self.gen_individual()
        else:
            parent_indx = self.select_gene_index(self.BEST, self.tournament_size)
            parent = self.population[parent_indx]
        # noinspection PyTypeChecker
        return parent

    def handle_event(self, event):
        if event == 'fitness_target':
            GA_World.fitness_target = SimEngine.gui_get('fitness_target')
            self.resume_ga()
            return
        super().handle_event(event)

    def initial_population(self) -> List[Individual]:
        """
        Generate the initial population. Use gen_individual from the subclass.
        """
        population = [self.gen_individual() for _ in range(self.pop_size)]
        return population

    def resume_ga(self):
        """ 
        This is used when one of the parameters changes dynamically. 
        It is called from handle_event. (See above.)
        """
        if self.done:
            self.done = False
            self.best_ind = None
            SimEngine.gui_set('best_fitness', value=None)
            go_stop_button = gui.WINDOW[GOSTOP]
            SimEngine.gui_set(GOSTOP, enabled=True)
            SimEngine.gui_set(GO_ONCE, enabled=True)
            go_stop_button.click()
        self.set_results()

    def select_gene_index(self, best_or_worst, tournament_size) -> int:
        """ Run a tournament to select the index of a best or worst individual in a sample. """
        min_or_max = min if best_or_worst == self.BEST else max
        candidate_indices = sample(range(self.pop_size), min(tournament_size, self.pop_size))
        selected_index = min_or_max(candidate_indices, key=lambda i: self.population[i].discrepancy)
        return selected_index

    @staticmethod
    def seq_to_chromosome(sequence: Sequence[Gene]):  # -> Chromosome:
        """ Converts a list to a Chromosome. """
        return sequence
        # return GA_World.chromosome_class(tuple(sequence))

    def set_results(self):
        """ Find and display the best individual. """
        # noinspection PyNoneFunctionAssignment
        current_best_ind = self.get_best_individual()
        if self.best_ind is None or current_best_ind.discrepancy < self.best_ind.discrepancy:
            self.best_ind = current_best_ind
        SimEngine.gui_set('best_fitness', value=round(self.best_ind.fitness, 1))
        SimEngine.gui_set('discrepancy', value=round(self.best_ind.discrepancy, 1))
        SimEngine.gui_set('generations', value=self.generations)

    def setup(self):
        # Create a list of Individuals as the initial population.
        # self.pop_size must be even since we generate children two at a time.
        self.pop_size = (SimEngine.gui_get('pop_size')//2)*2
        self.tournament_size = SimEngine.gui_get('tourn_size')
        GA_World.fitness_target = SimEngine.gui_get('fitness_target')
        self.population = self.initial_population()
        self.best_ind = None
        self.generations = 0
        self.set_results()

    def step(self):
        if self.best_ind and self.best_ind.discrepancy < 0.05:
            self.done = True
            return

        for i in range(self.pop_size//2):
            self.generate_2_children()

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

                   [sg.Text('Population size\n(must be even)', pad=((0, 5), (20, 0))),
                    sg.Slider(key='pop_size', range=(4, 100), resolution=2, default_value=10,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Tournament size', pad=((0, 5), (10, 0))),
                    sg.Slider(key='tourn_size', range=(3, 15), resolution=1, default_value=7,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob move gene', pad=((0, 5), (20, 0))),
                    sg.Slider(key='move_gene', range=(0, 100), default_value=5,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob reverse subsequence', pad=((0, 5), (20, 0))),
                    sg.Slider(key='reverse_subseq', range=(0, 100), default_value=5,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob random parent', pad=((0, 5), (20, 0))),
                    sg.Slider(key='prob_random_parent', range=(0, 100), default_value=5,
                              orientation='horizontal', size=(10, 20))
                    ],

                   ]
