
# This allows us to use the type Individual within the Individual class.
from __future__ import annotations

from collections import namedtuple
from random import choice, randint, sample
from typing import Any, List, NewType, Sequence, Tuple

import core.gui as gui
from core.gui import GOSTOP, GO_ONCE
from core.sim_engine import SimEngine
from core.world_patch_block import World

# Create a Gene type for pre-execution type checking.
# This will be "overridden" in ga_segregation.
Gene = NewType('Gene', Any)

Item = namedtuple('Item', ['value', 'weight'])


class Chromosome(tuple):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.
    """

    def chromosome_fitness(self) -> float:
        pass

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

    def cx_uniform(self: Chromosome, other_chromosome: Chromosome) -> Chromosome:
        new_c_list = [choice(pair) for pair in zip(self, other_chromosome)]
        new_chromosome = GA_World.chromosome_class(new_c_list)
        return new_chromosome

    def invert_a_gene(self):
        """ Convert a random gene between 0 and 1. """
        index = choice(list(range(len(self))))
        new_chromosome = self[:index] + (1-self[index], ) + self[index+1:]
        return new_chromosome

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

    def cx_all_diff(self, other: Individual) -> Tuple[Individual, Individual]:
        """
        Perform crossover between self and other while preserving all_different.
        """
        child_1 = GA_World.individual_class((self.chromosome).cx_all_diff_chromosome(other.chromosome))
        child_2 = GA_World.individual_class((other.chromosome).cx_all_diff_chromosome(self.chromosome))
        return (child_1, child_2)

    def cx_uniform(self, other: Individual) -> Tuple[Individual, Individual]:
        return (GA_World.individual_class(self.chromosome.cx_uniform(other.chromosome)),
                GA_World.individual_class(other.chromosome.cx_uniform(self.chromosome)))

    @property
    def discrepancy(self) -> float:
        discr = abs(self.fitness - GA_World.fitness_target)
        return discr

    def mate_with(self, other) -> Tuple[Individual, Individual]:
        pass

    def mutate(self) -> Individual:
        pass


class GA_World(World):
    """
    The Population holds the collection of Individuals that will undergo evolution.
    """
    chromosome_class = Chromosome
    fitness_target = None
    gene_pool = None
    individual_class = Individual

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # noinspection PyTypeChecker
        self.best_ind: Individual = None
        self.generations = None
        self.pop_size = None
        # noinspection PyTypeChecker
        self.population: List[Individual] = None

        self.tournament_size = None

        self.BEST = 'best'
        self.WORST = 'worst'

    # noinspection PyNoneFunctionAssignment
    def generate_2_children(self):
        """ Generate two children and put them into the population. """

        tour_size = SimEngine.gui_get('tourn_size')

        parent_1_indx: int = self.select_gene_index(self.BEST, tour_size)
        parent_1 = self.population[parent_1_indx]

        parent_2_indx: int = self.select_gene_index(self.BEST, tour_size)
        parent_2 = self.population[parent_2_indx]

        if parent_1 == parent_2:
            parent_2 = self.gen_individual()

        # Some percent of the time, mutate the parents without mating them.
        # This lets the better individuals get mutated directly.
        (child_1, child_2) = (parent_1, parent_2) if randint(0, 100) < SimEngine.gui_get('no_mating') else \
                             parent_1.mate_with(parent_2)

        child_1_mutated: Individual = child_1.mutate()
        child_2_mutated: Individual = child_2.mutate()

        # print(f'{(str(parent_1), str(parent_2))} -> {(str(child_1), str(child_2))} -> '
        #       f'{(str(child_1_mutated), str(child_2_mutated))}')

        dest_1_indx: int = self.select_gene_index(self.WORST, tour_size)
        self.population[dest_1_indx] = min([child_1, child_1_mutated], key=lambda c: c.discrepancy)

        dest_2_indx: int = self.select_gene_index(self.WORST, tour_size)
        self.population[dest_2_indx] = min([child_2, child_2_mutated], key=lambda c: c.discrepancy)

    def gen_gene_pool(self):
        pass

    def gen_individual(self) -> Individual:
        pass

    def get_best_individual(self) -> Individual:
        best_index = self.select_gene_index(self.BEST, len(self.population))
        best_individual = self.population[best_index]
        return best_individual

    def handle_event(self, event):
        if event == 'fitness_target':
            GA_World.fitness_target = SimEngine.gui_get('fitness_target')
            self.resume_ga()
            return
        if event == 'pop_size':
            new_pop_size = SimEngine.gui_get('pop_size')
            if new_pop_size <= self.pop_size:
                self.population = self.population[:new_pop_size]
            else:
                for i in range(self.pop_size, new_pop_size):
                    self.population.append(self.gen_individual())
            self.pop_size = new_pop_size
            self.resume_ga()
            return
        super().handle_event(event)

    def initial_population(self) -> List[Individual]:
        """
        Generate the initial population. Use gen_individual from the subclass.
        """
        self.gen_gene_pool()
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
            SimEngine.gui_set(GOSTOP, enabled=True)
            SimEngine.gui_set(GO_ONCE, enabled=True)
            go_stop_button = gui.WINDOW[GOSTOP]
            go_stop_button.click()
        self.set_results()

    def select_gene_index(self, best_or_worst, tournament_size) -> int:
        """ Run a tournament to select the index of a best or worst individual in a sample. """
        candidate_indices = sample(range(self.pop_size), min(tournament_size, self.pop_size))
        # min_or_max is min if we're looking for the best
        # because we are looking for the smallest discrepancy.
        min_or_max = min if best_or_worst == self.BEST else max
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
        if self.best_ind is None or current_best_ind.discrepancy <= self.best_ind.discrepancy:
            self.best_ind = current_best_ind
        SimEngine.gui_set('best_fitness', value=round(self.best_ind.fitness, 1))
        SimEngine.gui_set('discrepancy', value=round(self.best_ind.discrepancy, 1))
        SimEngine.gui_set('generations', value=self.generations)

    def setup(self):
        # Create a list of Individuals as the initial population.
        # self.pop_size must be even since we generate children two at a time.
        self.pop_size = SimEngine.gui_get('pop_size')
        self.population = self.initial_population()
        self.tournament_size = SimEngine.gui_get('tourn_size')
        if GA_World.fitness_target is None:
            GA_World.fitness_target = SimEngine.gui_get('fitness_target')
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
                    sg.Text('000000.0', key='best_fitness', pad=(None, (0, 0))),

                    sg.Text('Discrep:', pad=((5, 0), (0, 0))),
                    sg.Text('00000.0', key='discrepancy', pad=(None, (0, 0))),

                    sg.Text('Gens:', pad=((5, 0), (0, 0))),
                    sg.Text('00000', key='generations', pad=(None, (0, 0))),
                    ],

                   [sg.Text('Population size\n(must be even)', pad=((0, 5), (20, 0))),
                    sg.Slider(key='pop_size', range=(4, 100), resolution=2, default_value=10,
                              orientation='horizontal', size=(10, 20), enable_events=True)
                    ],

                   [sg.Text('Tournament size', pad=((0, 5), (10, 0))),
                    sg.Slider(key='tourn_size', range=(3, 15), resolution=1, default_value=4,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob no mating', pad=((0, 5), (10, 0))),
                    sg.Slider(key='no_mating', range=(1, 100), resolution=1, default_value=10,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Prob random parent', pad=((0, 5), (10, 0))),
                    sg.Slider(key='prob_random_parent', range=(0, 100), default_value=5,
                              orientation='horizontal', size=(10, 20))
                    ],

                   ]
