
from random import choice, randint, sample
from typing import List

from pygame import Color

from core.ga import Chromosome, GA_World, Gene, Individual, gui_left_upper
from core.link import Link
from core.sim_engine import SimEngine
from core.world_patch_block import World


class Loop_Link(Link):

    @property
    def label(self):
        """
        label is defined as a getter. No parentheses needed.
        Returns the length of the link.
        """
        return str(round(self.agent_1.distance_to(self.agent_2), 1))


# noinspection PyTypeChecker
class Loop_Individual(Individual):

    def __str__(self):
        return f'{self.fitness}: {[str(gene) for gene in self.chromosome]}'

    def add_gene(self, gene):
        best_pos_to_insert = min(range(len(self.chromosome)), 
                                 key=lambda pos: 
                                     Loop_Individual.new_discrepancy(self.fitness, self.chromosome, pos, gene))
        # self.chromosome.insert(best_pos_to_insert, gene)
        list_chromosome: List = list(self.chromosome)
        list_chromosome.insert(best_pos_to_insert, gene)
        self.chromosome = tuple(list_chromosome)

    @staticmethod
    def add_gene_to_chromosome(fitness: float, gene: Gene, list_chromosome: List[Gene]) -> Chromosome:
        best_pos_to_insert = min(range(len(list_chromosome)),
                                 key=lambda pos: Loop_Individual.new_discrepancy(fitness, list_chromosome, pos, gene))
        list_chromosome.insert(best_pos_to_insert, gene)
        return Chromosome(list_chromosome)

    def compute_fitness(self):
        chromosome = self.chromosome
        len_chrom = len(chromosome)
        # Recall that a chromosome is a tuple of Genes, each of which is a Pixel_xy.
        # total_distance = sum(p1.distance_to(p2) for (p1, p2) in point_pairs)
        total_distance = sum(chromosome[i].distance_to(chromosome[(i+1) % len_chrom]) for i in range(len_chrom))
        fitness = round(total_distance, 1)
        return fitness

    def mate_with(self, other):
        return self.cx_all_diff(self, other)

    def mutate(self) -> Individual:
        if randint(0, 100) <= SimEngine.gui_get('move_elt_internally'):
            # To keep PyCharm happy
            # assert isinstance(self.chromosome, Chromosome)
            self.move_elt(self.chromosome)

        if randint(0, 100) <= SimEngine.gui_get('replace_gene'):
            self.chromosome = self.replace_gene_in_chromosome(self.fitness, self.chromosome)

        if randint(0, 100) <= SimEngine.gui_get('reverse_sublist'):
            self.reverse_sublist(self.chromosome)

        self.fitness = self.compute_fitness()
        return self

    @staticmethod
    def new_discrepancy(current_fitness: float, chromosome, pos, gene):
        """
        Return what the discrepancy would be if gene were placed 
        between positions pos and pos+1
        """
        gene_at_pos = chromosome[pos]
        # Use % in case pos is the last gene position.
        gene_at_pos_plus_1 = chromosome[(pos+1) % len(chromosome)]
        new_fitness = current_fitness - gene_at_pos.distance_to(gene_at_pos_plus_1) \
                                      + gene_at_pos.distance_to(gene) \
                                      + gene.distance_to(gene_at_pos_plus_1)
        new_discrep = abs(GA_World.fitness_target - new_fitness)
        return new_discrep

    def replace_elt(self):
        list_chromosome = list(self.chromosome)
        list_chromosome.pop(choice(range(len(list_chromosome))))
        available_genes = GA_World.agents - set(list_chromosome)
        new_gene = sample(available_genes, 1)[0]
        self.add_gene(new_gene)

    @staticmethod
    def replace_gene_in_chromosome(fitness: float, chromosome) -> Chromosome:
        list_chromosome = list(chromosome)
        list_chromosome.pop(choice(range(len(chromosome))))
        available_genes = GA_World.agents - set(chromosome)
        new_gene = sample(available_genes, 1)[0]
        new_chromosome: Chromosome = Loop_Individual.add_gene_to_chromosome(fitness, new_gene, list_chromosome)
        return new_chromosome


class Loop_World(GA_World):
    
    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        self.cycle_length = SimEngine.gui_get('cycle_length')


    def gen_individual(self):
        chromosome = sample(World.agents, self.cycle_length)
        individual = GA_World.individual_class(chromosome)
        return individual

    def handle_event(self, event):
        if event == 'cycle_length':
            new_cycle_length = SimEngine.gui_get('cycle_length')
            if new_cycle_length != self.cycle_length:
                self.best_ind = None
                SimEngine.gui_set('best_fitness', value=None)
                self.cycle_length = new_cycle_length
                self.update_cycle_lengths(new_cycle_length)
                self.best_ind = self.get_best_individual()
                SimEngine.gui_set('best_fitness', value=self.best_ind.fitness)

            return
        super().handle_event(event)

    def initial_individuals(self) -> List[Loop_Individual]:
        self.cycle_length = SimEngine.gui_get('cycle_length')
        individuals = [self.gen_individual() for _ in range(self.pop_size)]
        Individual.count = self.pop_size
        return individuals

    def link_best_individual(self):
        best_ind_elts = self.best_ind.chromosome
        for i in range(len(best_ind_elts) - 1):
            Loop_Link(best_ind_elts[i], best_ind_elts[i+1])
        Loop_Link(best_ind_elts[-1], best_ind_elts[0])

    def setup(self):
        GA_World.individual_class = Loop_Individual
        nbr_points = SimEngine.gui_get('nbr_points')
        self.create_random_agents(nbr_points, color=Color('white'), shape_name='node')

        self.mating_op = Individual.cx_all_diff
        super().setup()
        self.link_best_individual()

    def step(self):
        super().step()
        World.links = set()
        self.link_best_individual()

    def update_cycle_lengths(self, cycle_length):
        for ind in self.individuals:
            if cycle_length < len(ind.chromosome):
                ind.chromosome = ind.chromosome[:cycle_length]
            else:
                available_genes = GA_World.agents - set(ind.chromosome)
                new_chromosome = sample(available_genes, cycle_length - len(ind.chromosome))
                for gene in new_chromosome:
                    ind.add_gene(gene)

            ind.fitness = ind.compute_fitness()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
loop_gui_left_upper = gui_left_upper + [
                      [sg.Text('Prob replace elt', pad=((0, 5), (20, 0))),
                       sg.Slider(key='replace_gene', range=(0, 100), default_value=95,
                                 orientation='horizontal', size=(10, 20))
                       ],

                      [sg.Text('fitness_target', pad=(None, (20, 0))),
                       sg.Combo(key='fitness_target', default_value=1500, pad=((10, 0), (20, 0)), enable_events=True,
                                values=[0, 100, 500, 700, 900, 1200, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000])
                       ],

                      [sg.Text('Cycle length', pad=(None, (20, 0))),
                       sg.Slider(key='cycle_length', range=(2, 20), default_value=10, pad=((10, 0), (0, 0)),
                                 orientation='horizontal', size=(10, 20), enable_events=True)
                       ],

    ]


if __name__ == "__main__":
    from core.agent import PyLogo
    # gui_left_upper is from core.ga
    PyLogo(Loop_World, 'Loops', loop_gui_left_upper)
