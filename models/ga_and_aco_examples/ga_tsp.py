from __future__ import annotations

from inspect import getmembers
from random import choice, random, sample, uniform
from typing import List, Tuple

from pygame import Color

import core.gui as gui
from core.agent import Agent
from core.ga import Chromosome, GA_World, Gene, Individual, gui_left_upper
from core.link import Link, draw_links, minimum_spanning_tree, seq_to_links
from core.pairs import Velocity
from core.sim_engine import SimEngine, gui_get, gui_set
from core.world_patch_block import World


def order_elements(elt_list):
    """
    Rotate and possibly reverse the elt_list so that city A comes first
    and the city that follows city A is less than the city that precedes it.
    """
    first_index = min(range(len(elt_list)), key=lambda i: elt_list[i])
    # In the second case, must leave the end index as None. If set to -1, it will
    # be taken as len(chromo)-1. The slice will produce the empty list.
    revised = elt_list[first_index:] + elt_list[:first_index] \
        if elt_list[(first_index + 1) % len(elt_list)] < elt_list[(first_index - 1)] else \
        elt_list[first_index::-1] + elt_list[len(elt_list) - 1:first_index:-1]
    return revised


class TSP_Agent(Agent):
    """ An agent is a point on the screen, not a GA individual. """

    show_labels = False

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
        return str(self.id) if TSP_Agent.show_labels else None


class TSP_Link(Link):

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(self.length) if gui_get('show_lengths') else None


class TSP_Chromosome(Chromosome):
    """
    An individual consists primarily of a sequence of Genes, called
    a chromosome. We create a class for it simply because it's a
    convenient place to store methods.
    """
    @staticmethod
    def factory(chromo):
        ordered_chromo = order_elements(chromo)
        new_chromo = TSP_Chromosome(ordered_chromo)
        return new_chromo

    def __str__(self):
        return TSP_Chromosome.chromo_str(self)


    # Functions to generate initial TSP paths

    @staticmethod
    def greedy_path() -> List[Gene]:
        """
        Generates a greedy path. Starts at a random Gene, i.e., a point on the screen
        and extends that path to the nearest neighboring point until all the points
        are included.

        Currently written to call random_path. You should replace that with a greedy algorithm.
        """
        return TSP_Chromosome.random_path()

    @staticmethod
    def random_path() -> List[Gene]:
        """
        Generates a random path. The function sample selectes a given number of
        elements from its first argument and returns them in a shuffled list.
        Since the second argument is the lengt of the first argument, sample
        will return a random permutation of the Genes, i.e., the points on the screen.

        Currently written to call random_path. You should replace that with a minimal
        spanning tree algorithm.
        """
        chromosome_list: List = sample(GA_World.gene_pool, len(GA_World.gene_pool))
        return chromosome_list

    @staticmethod
    def spanning_tree_path() -> List[Gene]:
        """
        Generates a path derived from a minimum spanning tree of the Genes.
        Constructs a minimum spanning tree. Then does a DFS of the tree, adding
        elements in the order encountered as long as they were not added earlier.

        Currently written to call random_path. You should replace that with a spanning_tree algorithm.
        """
        return TSP_Chromosome.random_path()

    # End functions to generate initial TSP paths


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

    def two_opt(self, original_fitness: float) -> TSP_Chromosome:
        """
        Move a random gene to the point in the chromosome that will produce the best result.

        Currently calls move_gene_in_chromosome. Should be replaced with code that does two_opt.
        """
        return self.move_gene_in_chromosome(original_fitness)


# noinspection PyTypeChecker
class TSP_Individual(Individual):

    def __init__(self, *args, generator=None, original_sequence=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator = generator
        self.original_sequence = original_sequence

    def __str__(self):
        return f'{round(self.fitness, 1)}: ({", ".join([str(gene) for gene in self.chromosome])})'

    def compute_fitness(self) -> float:
        fitness = (self.chromosome).chromosome_fitness()
        return fitness

    @property
    def discrepancy(self) -> float:
        return self.fitness

    def mate_with(self, other):
        children = self.cx_all_diff(other)
        return children

    def mutate(self) -> Individual:

        mutation_operations = []
        chromo = self.chromosome
        assert isinstance(chromo, TSP_Chromosome)
        if gui_get('Move element'):
            mutation_operations.append(chromo.move_gene_in_chromosome)
        if gui_get('2-Opt'):
            mutation_operations.append(chromo.two_opt)

        # If no mutation operations have been selected, return the individual unchnged.
        if not mutation_operations:
            return self
        else:
            # Otherwise, apply one of the selected mutation operation.
            operation = choice(mutation_operations)
            # Both of the current mutation operations require self.fitness as their argument.
            new_chromosome = operation(self.fitness)
            new_individual = GA_World.individual_class(new_chromosome)
            return new_individual


class TSP_World(GA_World):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msp_links = None

    def create_node(self):
        new_point = self.create_random_agent(color=Color('white'), shape_name='node', scale=1)
        new_point.set_velocity(TSP_World.random_velocity())
        # If the same individual is in the population
        # multiple times, don't process it more than once.
        updated_chromos = set()
        for ind in self.population:
            old_chromo = ind.chromosome
            if old_chromo not in updated_chromos:
                # noinspection PyUnresolvedReferences
                (new_chromo, ind.fitness) = old_chromo.add_gene_to_chromosome(ind.fitness, new_point)
                # noinspection PyArgumentList
                ind.chromosome = GA_World.chromosome_class(new_chromo)
                updated_chromos.add(new_chromo)

    def delete_node(self):
        # Can't use choice with a set.
        node = sample(World.agents, 1)[0]
        # If the same individual is in the population
        # multiple times, don't process it more than once.
        updated_chromos = set()
        for ind in self.population:
            old_chromo = ind.chromosome
            if old_chromo not in updated_chromos:
                new_chromo_list = list(old_chromo)
                new_chromo_list.remove(node)
                new_chromo = GA_World.chromosome_class(new_chromo_list)
                ind.chromosome = new_chromo
                updated_chromos.add(new_chromo)
        node.delete()

    def gen_gene_pool(self):
        # The gene_pool in this case consists of the point on the grid, which are agents.
        nbr_points = gui_get('nbr_points')
        self.create_random_agents(nbr_points, color=Color('white'), shape_name='node', scale=1)
        GA_World.gene_pool = World.agents
        for agent in GA_World.gene_pool:
            agent.set_velocity(TSP_World.random_velocity())

    @staticmethod
    def gen_individual():
        path_methods = [TSP_Chromosome.random_path]
        if gui_get('Greedy'):
            path_methods.append(TSP_Chromosome.greedy_path)
        if gui_get('Min spanning tree'):
            path_methods.append(TSP_Chromosome.spanning_tree_path)
        gen_path_method = choice(path_methods)
        chromosome_list: List = gen_path_method()
        chromo = GA_World.chromosome_class(chromosome_list)
        individual = GA_World.individual_class(chromo, generator=gen_path_method, original_sequence=chromosome_list)
        return individual

    def gen_initial_population(self):
        """
        Generate the initial population. gen_new_individual uses gen_individual from the subclass.
        """
        # Must do it this way because self.gen_new_individual checks to see if each new individual
        # is already in self.population.
        self.population = []
        for i in range(self.pop_size):
            new_individual = self.gen_new_individual()
            assert isinstance(new_individual, TSP_Individual)
            assert isinstance(new_individual.chromosome, TSP_Chromosome)
            generator_name = dict(getmembers(new_individual.generator))['__name__']
            if gui_get('Animate construction'):
                print(f'{i}. {generator_name} {"(no display)" if generator_name == "random_path" else ""}')
            if generator_name != 'random_path':
                msp_links = self.minimum_spanning_tree_links() if generator_name == 'spanning_tree_path' else []
                path_links = seq_to_links(new_individual.original_sequence, TSP_Link)
                if gui_get('Animate construction'):
                    for lnk in path_links:
                        lnk.set_color(Color('yellow' if lnk in msp_links else 'red'))
                    # World.links = set()
                    # draw_links(msp_links + path_links, World.links)
                    draw_links(msp_links + path_links)
            self.population.append(new_individual)

    def handle_event(self, event):
        if event.endswith('Node'):
            if event == 'Create Node':
                self.create_node()
            elif event == 'Delete Node':
                if len(GA_World.gene_pool) > 2:
                    self.delete_node()
            gui_set('nbr_points', value=len(GA_World.gene_pool))
            self.set_results()
        elif event == 'Reverse':
            for gene in GA_World.gene_pool:
                gene.velocity *= (-1)
        else:
            super().handle_event(event)

    def minimum_spanning_tree_links(self):
        if not self.msp_links:
            self.msp_links = minimum_spanning_tree(list(GA_World.gene_pool))
        return self.msp_links

    @staticmethod
    def random_velocity(limit=0.75):
        return Velocity((uniform(-limit, limit), uniform(-limit, limit)))

    def set_results(self):
        super().set_results()
        best_chromosome: TSP_Chromosome = self.best_ind.chromosome
        World.links = set(seq_to_links(best_chromosome, TSP_Link))

        # Never stop
        self.done = False

    def setup(self):
        Agent.id = 1
        GA_World.individual_class = TSP_Individual
        GA_World.chromosome_class = TSP_Chromosome.factory

        # The following GUI elements are defined in ga.py.
        # We can't set their default values in this file's GUI.
        # The only way to do it is explicitly.
        gui_set('Max generations', value=float('inf'))
        gui_set('prob_random_parent', value=20)

        # Don't display the following standard GA features.
        for label in ['Discrep:', 'discrepancy', 'Gens:', 'generations']:
            gui_set(label, visible=False)

        TSP_Agent.show_labels = gui_get('show_labels')

        (SimEngine.event, SimEngine.values) = gui.WINDOW.read(timeout=10)
        SimEngine.draw_world()

        # auto_setup is initially True (by default). The next line aborts setup in that case.
        # The purpose is to allow the system to create a display but not run gen_population,
        # which is run when the user clicks setup. That works because auto_setup is set to
        # False by SimEngine after setup run, which happens automatically. So, if auto_setup
        # is False, we will complete setup and generate the initial population.
        if not SimEngine.auto_setup:
            self.msp_links = None
            if gui_get('Animate construction'):
                print(f'\nGenerating the initial population of {gui_get("pop_size")} paths.')
            super().setup()

    def step(self):
        """
        Update the world by moving the agents.
        """
        # If the user hadn't clicked setup before clicking go, the
        # gene_pool will not have been generated. The following
        # call to setup replaces the user clicking setup.
        if GA_World.gene_pool is None:
            self.setup()
        if gui_get('move points'):
            for agent in GA_World.gene_pool:
                agent.move_by_velocity()
                if random() < 0.001:
                    agent.set_velocity(TSP_World.random_velocity())
            for ind in self.population:
                ind.fitness = ind.compute_fitness()
            self.best_ind = None
        TSP_Agent.show_labels = gui_get('show_labels')
        super().step()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

col = [[sg.Button('Create Node', tooltip='Create a node')],
       [sg.Button('Delete Node', tooltip='Delete one random node')]]

frame_layout_node_buttons = [[sg.Column(col, pad=(None, None)),
                              sg.Button('Reverse', tooltip='Reverse direction of motion')]]

frame_layout_generators = [[sg.Checkbox('Greedy', key='Greedy', default=True)],
                           [sg.Checkbox('Min spanning tree', key='Min spanning tree', default=True)]]

frame_layout_mutations = [[sg.Checkbox('Move element', key='Move element', default=True)],
                          [sg.Checkbox('2-Opt', key='2-Opt', default=True)]]

tsp_right_upper = [[
                    sg.Frame('Generators', frame_layout_generators, pad=((25, 0), (0, 0))),
                    sg.Frame('Mutations', frame_layout_mutations, pad=((25, 0), (0, 0))),
                    sg.Frame('Node control', frame_layout_node_buttons, pad=((25, 0), (0, 0))),
                    ]]

path_controls = [[sg.Checkbox('Move points', key='move points', pad=(None, (10, 0)), default=True),
                  sg.Checkbox('Animate construction', key='Animate construction', pad=((20, 0), (10, 0)),
                              default=True, enable_events=True)],

                 [sg.Checkbox('Show labels', key='show_labels', default=True, pad=((0, 0), (10, 0))),
                  sg.Checkbox('Show lengths', key='show_lengths', default=False, pad=((20, 0), (10, 0)))]
                 ]

# gui_left_upper is from core.ga
tsp_gui_left_upper = gui_left_upper + [

                      [sg.Text('Nbr points', pad=((0, 5), (10, 0))),
                       sg.Slider(key='nbr_points', range=(5, 200), default_value=15, orientation='horizontal',
                                 size=(10, 20))],

                      [sg.Frame('Path controls', path_controls, pad=(None, (10, 0)))]
                                       ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(TSP_World, 'TSP', tsp_gui_left_upper, gui_right_upper=tsp_right_upper,
           agent_class=TSP_Agent, bounce=(True, False))
