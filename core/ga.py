
# This allows us to use the type Individual within the Individual class.
from __future__ import annotations

from collections import namedtuple
from random import choice, randint, sample
from typing import Any, List, NewType, Sequence, Tuple

import core.gui as gui
from core.gui import GOSTOP, GO_ONCE
from core.sim_engine import gui_get, gui_set
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
        child_chromosome_end = tuple(gene for gene in other_chromosome_rotated if gene not in child_chromosome_start)

        child_chromosome: Chromosome = GA_World.chromosome_class(child_chromosome_start + child_chromosome_end)
        return child_chromosome[:len(self)]

    def cx_uniform(self: Chromosome, other_chromosome: Chromosome) -> Tuple[Chromosome, Chromosome]:
        pairs = [choice([(a, b), (b, a)]) for (a, b) in zip(self, other_chromosome)]
        (tuple_1, tuple_2) = tuple(zip(*pairs))
        chromo_pair = (GA_World.chromosome_class(tuple_1), GA_World.chromosome_class(tuple_2))
        return chromo_pair

    def invert_a_gene(self):
        """ Switch a random gene between 0 and 1. """
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
        self.fitness: float = self.compute_fitness()

    def compute_fitness(self) -> float:
        pass

    def duplicates(self, other):
        return self.chromosome == other.chromosome

    def cx_all_diff(self, other: Individual) -> Tuple[Individual, Individual]:
        """
        Perform crossover between self and other while preserving all_different.
        """
        child_1 = GA_World.individual_class((self.chromosome).cx_all_diff_chromosome(other.chromosome))
        child_2 = GA_World.individual_class((other.chromosome).cx_all_diff_chromosome(self.chromosome))
        return (child_1, child_2)

    def cx_uniform(self, other: Individual) -> Tuple[Individual, Individual]:
        (chromo_1, chromo_2) = self.chromosome.cx_uniform(other.chromosome)
        return (GA_World.individual_class(chromo_1), GA_World.individual_class(chromo_2))

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

    def eliminate_duplicates(self, population):
        sorted_population = self.sort_population(population)
        comparison_individual = sorted_population[0]
        for i in range(1, len(sorted_population)):
            if sorted_population[i].duplicates(comparison_individual):
                sorted_population[i] = self.gen_new_individual()
            else:
                comparison_individual = sorted_population[i]
        sorted_population = self.sort_population(sorted_population)
        return sorted_population

    # noinspection PyNoneFunctionAssignment
    def generate_2_children(self):
        """
        Generate two children and put them into the population.
        """
        tourn_size = gui_get('tourn_size')

        parent_1_indx: int = self.select_gene_index(self.BEST, tourn_size)
        parent_1 = self.population[parent_1_indx]

        parent_2_indx: int = self.select_gene_index(self.BEST, tourn_size)
        parent_2 = self.population[parent_2_indx]

        if parent_1 == parent_2:
            parent_2 = self.gen_new_individual()

        # Some percent of the time, mutate the parents without mating them.
        # This lets the better individuals get mutated directly.
        (child_1, child_2) = (parent_1, parent_2) if randint(0, 100) < gui_get('no_mating') else \
                             parent_1.mate_with(parent_2)

        child_1_mutated: Individual = child_1.mutate()
        if child_1_mutated in self.population:
            child_1_mutated = self.gen_new_individual()

        child_2_mutated: Individual = child_2.mutate()
        if child_2_mutated in self.population:
            child_2_mutated = self.gen_new_individual()

        # The population is not immutable. We change it by writing new individuals into it.
        dest_1_indx: int = self.select_gene_index(self.WORST, tourn_size)
        self.population[dest_1_indx] = min([child_1, child_1_mutated], key=lambda c: c.discrepancy)

        dest_2_indx: int = self.select_gene_index(self.WORST, tourn_size)
        self.population[dest_2_indx] = min([child_2, child_2_mutated], key=lambda c: c.discrepancy)

    def gen_gene_pool(self):
        pass

    @staticmethod
    def gen_individual() -> Individual:
        """ Override in subclass. """
        pass

    def gen_initial_population(self):
        """
        Generate the initial population. gen_new_individual uses gen_individual from the subclass.
        """
        # Must do it this way because self.gen_new_individual checks to see if each new individual
        # is already in self.population.
        self.population = []
        for _ in range(self.pop_size):
            self.population.append(self.gen_new_individual())

    def gen_new_individual(self) -> Individual:
        """
        Generate a new individual. Ensure, if possible, that the new individual is unique,
        i.e., not already in the population. If that's not possible (because the population
        is too large for the gene pool and virtually all gene combinations are already in
         use) generate a random new individual and warn the user.

        """
        # Try for a unique individual.
        for _ in range(10):
            new_ind = self.gen_individual()
            if new_ind not in self.population:
                # Found a unique individual, return it.
                return new_ind
        else:
            # Did not find a unique individual. Warn the user and generate a random individual.
            print(f"Population too large for gene pool. Can't guarantee unique individuals.")
            return self.gen_individual()

    def get_best_individual(self) -> Individual:
        best_index = self.select_gene_index(self.BEST, len(self.population))
        best_individual = self.population[best_index]
        return best_individual

    def handle_event(self, event):
        if event == 'fitness_target':
            GA_World.fitness_target = gui_get('fitness_target')
            self.resume_ga()
            return
        elif event == 'pop_size':
            new_pop_size = gui_get('pop_size')
            if new_pop_size <= self.pop_size:
                self.population = self.population[:new_pop_size]
            else:
                for i in range(self.pop_size, new_pop_size):
                    self.population.append(self.gen_new_individual())
            self.pop_size = new_pop_size
            self.resume_ga()
            return
        else:
            super().handle_event(event)

    def resume_ga(self):
        """ 
        This is used when one of the parameters changes dynamically. 
        It is called from handle_event. (See above.)
        """
        self.best_ind = None
        self.generations = 0
        if self.done:
            self.done = False
            gui_set('best_fitness', value=None)
            gui_set(GOSTOP, enabled=True)
            gui_set(GO_ONCE, enabled=True)
            go_stop_button = gui.WINDOW[GOSTOP]
            go_stop_button.click()
        self.set_results()

    def select_gene_index(self, best_or_worst, tournament_size) -> int:
        """
        Run a tournament to select the index of a best or worst individual in a sample.
        If tournament_size is the size of the entire population, look at the entire population
        and select the index of the best/worst
        """
        candidate_indices = sample(range(self.pop_size), min(tournament_size, self.pop_size))

        # min_or_max is min if we're looking for the best
        # because we are looking for the smallest discrepancy.
        min_or_max = min if best_or_worst == self.BEST else max
        selected_index = min_or_max(candidate_indices, key=lambda i: self.population[i].discrepancy)
        return selected_index

    def set_results(self):
        """ Find and display the best individual. """
        current_best_ind = self.get_best_individual()
        if self.best_ind is None or current_best_ind.discrepancy < self.best_ind.discrepancy:
            self.best_ind = current_best_ind

        gui_set('best_fitness', value=round(self.best_ind.fitness, 1))
        gui_set('discrepancy', value=round(self.best_ind.discrepancy, 1))
        gui_set('generations', value=self.generations)

        if self.best_ind.discrepancy == 0 or self.generations >= gui_get('Max generations'):
            self.done = True

    def setup(self):
        if not World.agents:
            World.agents = set()
            self.gen_gene_pool()

        # self.pop_size must be even since we generate children two at a time.
        # If it was set by the specific problem's setup function, it will not be None.
        if self.pop_size is None:
            self.pop_size = gui_get('pop_size')

        # Create the initial population of individuals.
        self.gen_initial_population()

        self.tournament_size = gui_get('tourn_size')
        if GA_World.fitness_target is None:
            GA_World.fitness_target = gui_get('fitness_target')

        self.best_ind = None
        self.generations = 0
        self.set_results()

    @staticmethod
    def sort_population(population):
        return sorted(population, key=lambda i: i.fitness, reverse=True)

    def step(self):
        # Loop for self.pop_size//2 steps since we generate two individuals for each time around.
        for i in range(self.pop_size//2):
            self.generate_2_children()

        self.generations += 1
        self.set_results()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [

                   [sg.Text('Best:', pad=(None, (0, 0))),
                    sg.Text('000000.0', key='best_fitness', pad=(None, (0, 0))),

                    sg.Text('Discrep:', key='Discrep:', pad=((5, 0), (0, 0))),
                    sg.Text('00000.0', key='discrepancy', pad=(None, (0, 0))),

                    sg.Text('Gens:', key='Gens:', pad=((5, 0), (0, 0))),
                    sg.Text('00000', key='generations', pad=(None, (0, 0))),
                    ],

                   [sg.Text('Population size\n(must be even)', pad=((0, 5), (20, 0))),
                    sg.Slider(key='pop_size', range=(5, 500), resolution=5, default_value=10,
                              orientation='horizontal', size=(10, 20), enable_events=True)
                    ],

                   [sg.Text('Tournament size', pad=((0, 5), (10, 0))),
                    sg.Slider(key='tourn_size', range=(3, 15), resolution=1, default_value=7,
                              orientation='horizontal', size=(10, 20))
                    ],

                   [sg.Text('Max generations:', pad=(None, (10, 0))),
                    sg.Combo(key='Max generations', values=[10, 50, 100, 250, 500, float('inf')], default_value=100,
                             pad=(None, (10, 0)))
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
