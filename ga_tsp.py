from __future__ import annotations

from random import random, sample, uniform
from typing import List, Tuple

from pygame import Color

from core.agent import Agent
from core.ga import Chromosome, GA_World, Gene, Individual, gui_left_upper
from core.link import Link
from core.pairs import Velocity
from core.sim_engine import gui_get, gui_set
from core.world_patch_block import World


class TSP_Agent(Agent):

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        return str(self.id)

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the position of the agent, i.e., the point
        """
        return str(self.id) if gui_get('show_labels') else None


class TSP_Link(Link):

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(round(self.agent_1.distance_to(self.agent_2), 1)) if gui_get('show_lengths') else None


class TSP_Chromosome(Chromosome):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.
    """
    @staticmethod
    def factory(chromo):
        first_index = min(range(len(chromo)), key=lambda i: chromo[i])
        # In the second case, must leave the end index as None. If set to -1, it will
        # be taken as len(chromo)-1. The slice will produce the empty list.
        revised = chromo[first_index:] + chromo[:first_index] \
                      if chromo[(first_index+1) % len(chromo)] < chromo[(first_index-1)] else \
                  chromo[first_index::-1] + chromo[len(chromo)-1:first_index:-1]
        new_chromo = TSP_Chromosome(revised)
        return new_chromo

    def __str__(self):
        return TSP_Chromosome.chromo_str(self)

    def add_gene_to_chromosome(self, orig_fitness: float, gene):
        """ Add gene to the chromosome to minimize the cycle distance. """
        (best_new_chrom, best_new_fitness) = (None, None)
        len_chrom = len(self)
        for i in sample(range(len_chrom), min(3, len_chrom)):
            (new_chrom, new_fitness) = self.trial_insertion(orig_fitness, i, gene)
            if best_new_fitness is None or new_fitness < best_new_fitness:
                (best_new_chrom, best_new_fitness) = (new_chrom, new_fitness)
        return (best_new_chrom, best_new_fitness)

    @staticmethod
    def chromo_str(chromo):
        return '(' + ', '.join([f'{pt}' for pt in chromo]) + ')'

    def chromosome_fitness(self) -> float:
        len_chrom = len(self)
        # A chromosome is a tuple of Genes, each of which is a Pixel_xy.
        # We use mod (%) so that we can include the distance from the gene
        # at chromosome[len_chrom - 1] to the gene at chromosome[0].
        distances = [self[i].distance_to(self[(i + 1) % len_chrom]) for i in range(len_chrom)]
        fitness = sum(distances)
        return fitness

    def link_chromosome(self):
        for i in range(len(self)):
            TSP_Link(self[i], self[(i+1) % len(self)])

    def move_gene_in_chromosome(self, original_fitness: float) -> TSP_Chromosome:
        """
        Move a random gene to the point in the chromosome that will produce the best result.
        """
        (best_new_chrom, best_new_fitness) = (None, None)
        len_chrom = len(self)
        for i in sample(range(len_chrom), min(3, len_chrom)):
            gene_before = self[i-1]
            removed_gene = self[i]
            i_p_1 = (i+1) % len_chrom
            gene_after = self[i_p_1]
            fitness_after_removal = original_fitness - gene_before.distance_to(removed_gene) \
                                                     - removed_gene.distance_to(gene_after)  \
                                                     + gene_before.distance_to(gene_after)

            # noinspection PyArgumentList
            partial_chromosome: TSP_Chromosome = GA_World.chromosome_class(self[:i] + self[i+1:])
            (new_chrom, new_fitness) = partial_chromosome.add_gene_to_chromosome(fitness_after_removal, removed_gene)
            if best_new_fitness is None or new_fitness < best_new_fitness:
                (best_new_chrom, best_new_fitness) = (new_chrom, new_fitness)

        return GA_World.chromosome_class(best_new_chrom)

    def trial_insertion(self, current_fitness: float, pos: int, new_gene: Gene) -> Tuple[Chromosome, int]:
        """
        Return what the discrepancy would be if gene were placed between positions pos-1 and pos
        """
        gene_at_pos = self[pos]
        # This works even if the chromosome has only one element. In that case,
        # both pos and (pos+1) % len(chromosome) will be 0. The gene at
        # these two positions will be chromosome[0]. In that case also,
        # current_fitness will be 0.
        gene_at_pos_plus_1 = self[(pos+1) % len(self)]
        new_fitness = current_fitness - gene_at_pos.distance_to(gene_at_pos_plus_1) \
                                      + gene_at_pos.distance_to(new_gene) \
                                      + new_gene.distance_to(gene_at_pos_plus_1)
        new_chrom = self[:pos] + (new_gene, ) + self[pos:]
        return (new_chrom, new_fitness)


# noinspection PyTypeChecker
class TSP_Individual(Individual):

    def __str__(self):
        return f'{self.fitness}: {[str(gene) for gene in self.chromosome]}'

    def compute_fitness(self) -> float:
        fitness = (self.chromosome).chromosome_fitness()
        # print(fitness)
        return fitness

    @property
    def discrepancy(self) -> float:
        return self.fitness

    def mate_with(self, other):
        children = self.cx_all_diff(other)
        return children

    def mutate(self) -> Individual:
        assert isinstance(self.chromosome, TSP_Chromosome)
        new_chromosome = (self.chromosome).move_gene_in_chromosome(self.fitness)
        new_individual = GA_World.individual_class(new_chromosome)
        return new_individual


class TSP_World(GA_World):
    
    cycle_length = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    def gen_gene_pool(self):
        # The gene_pool in this case are the point on the grid, which are agents.
        nbr_points = gui_get('nbr_points')
        self.create_random_agents(nbr_points, color=Color('white'), shape_name='node', scale=1)
        GA_World.gene_pool = World.agents
        for agent in GA_World.gene_pool:
            agent.set_velocity(TSP_World.random_velocity())

    @staticmethod
    def gen_individual():
        chromosome_list: List = sample(GA_World.gene_pool, len(GA_World.gene_pool))
        chromo = GA_World.chromosome_class(chromosome_list)
        individual = GA_World.individual_class(chromo)
        return individual

    def handle_event(self, event):
        if event == 'cycle_length':
            new_cycle_length = gui_get('cycle_length')
            if new_cycle_length != TSP_World.cycle_length:
                TSP_World.cycle_length = gui_get('cycle_length')
                # World.links = set()
                self.best_ind = None
                self.population = self.initial_population()
                # super().setup()
                self.resume_ga()
            return
        super().handle_event(event)

    @staticmethod
    def random_velocity(limit=0.5):
        return Velocity((uniform(-limit, limit), uniform(-limit, limit)))

    def set_results(self):
        super().set_results()
        World.links = set()
        best_chromosome: TSP_Chromosome = self.best_ind.chromosome
        best_chromosome.link_chromosome()
        # Never stop
        self.done = False

    def setup(self):
        GA_World.individual_class = TSP_Individual
        GA_World.chromosome_class = TSP_Chromosome.factory
        gui_set('Max generations', value=float('inf'))
        self.pop_size = 10
        gui_set('pop_size', value=self.pop_size)
        gui_set('prob_random_parent', value=20)
        gui_set('Discrep:', visible=False)
        gui_set('discrepancy', visible=False)
        gui_set('Gens:', visible=False)
        gui_set('generations', visible=False)
        super().setup()

    def step(self):
        """
        Update the world by moving the agents.
        """
        if gui_get('move_points'):
            for agent in GA_World.gene_pool:
                agent.move_by_velocity()
                if self.best_ind:
                    self.best_ind.fitness = self.best_ind.compute_fitness()
                if random() < 0.0001:
                    agent.set_velocity(TSP_World.random_velocity())
        super().step()
        # Never stop
        self.done = False


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
tsp_right_upper = [
                     [sg.Button('Create Node', tooltip='Create a node'),
                      sg.Button('Delete Node', tooltip='Delete one random node')]]

tsp_gui_left_upper = gui_left_upper + [

                      [sg.Text('Nbr points', pad=((0, 5), (10, 0))),
                       sg.Slider(key='nbr_points', range=(5, 200), default_value=5, orientation='horizontal',
                                 size=(10, 20))
                       ],

                      [sg.Checkbox('Move points', key='move_points', pad=(None, (10, 0)), default=False)],

                      [sg.Checkbox('Show labels', key='show_labels', default=True, pad=((0, 0), (10, 0))),
                       sg.Checkbox('Show lengths', key='show_lengths', default=False, pad=((20, 0), (10, 0)))]

    ]


if __name__ == "__main__":
    from core.agent import PyLogo
    # gui_left_upper is from core.ga
    PyLogo(TSP_World, 'TSP', tsp_gui_left_upper, gui_right_upper=tsp_right_upper, agent_class=TSP_Agent, bounce=True)
