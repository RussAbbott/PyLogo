
from __future__ import annotations

from itertools import count
from random import randint, sample
from typing import List, Sequence, Tuple

from Examples.ga_examples.ga_segregation import Gene, Segregation_Chromosome
from core.ga import GA_World, Individual, gui_left_upper
from core.sim_engine import gui_get, gui_set


class Parentheses_Chromosome(Segregation_Chromosome):

    def chromosome_fitness(self) -> Tuple[List[bool], int]:
        left_satisfactions = Parentheses_Chromosome.chromosome_satisfactions_from_end(0, self,
                                                                                      {'(': 1, ' ': 0, ')': -1})
        right_satisfactions = Parentheses_Chromosome.chromosome_satisfactions_from_end(len(self) - 1, self,
                                                                                       {'(': -1, ' ': 0, ')': 1})
        len_self = len(self)
        satisfactions = [left_satisfactions[i] and right_satisfactions[i] for i in range(len_self)]
        fitness = len_self - sum(satisfactions)
        return (satisfactions, fitness)

    @staticmethod
    def chromosome_satisfactions_from_end(start, chromo, balance_value) -> List[bool]:
        len_chrom = len(chromo)
        (end, step) = (len_chrom, 1) if start == 0 else (-1, -1)
        # A chromosome is a tuple of Genes, each of which is a Gene(id, val), where val 0 or 1.
        errors = 0
        balance = 0
        # balance_value = {'(': 1, ' ': 0, ')': -1}
        satisfied = [True]*len_chrom
        for i in range(start, end, step):
            balance += balance_value[chromo[i].val]
            if balance < 0:
                errors += 1
                balance = 0
                satisfied[i] = False
        return satisfied

    def chromosome_string(self):
        return ' '.join([str(gene.val) for gene in self])


class Parentheses_Individual(Individual):

    def __init__(self, chromosome: Sequence[Gene]):
        self.satisfied = None
        self.chromosome: Parentheses_Chromosome = Parentheses_Chromosome(chromosome)
        super().__init__(self.chromosome)

    def __str__(self):
        return f'{self.fitness}: ' \
               f'{self.chromosome.chromosome_string()}' \
               f'\n' \
               f'{" "*len(str(self.fitness))}  {self.satisfied_string()}'

    def compute_fitness(self) -> float:
        (self.satisfied, fitness) = self.chromosome.chromosome_fitness()
        return fitness

    def mate_with(self, other):
        return self.cx_uniform(other)

    def mutate(self) -> Individual:
        chromosome = self.chromosome
        satisfied = self.satisfied

        no_mutation = gui_get('no_mutation')
        move_unsatisfied = gui_get('move_unsatisfied_gene')
        exchange_unsatisfied_genes = gui_get('exchange_unsatisfied_genes')
        reverse_subseq = gui_get('reverse_subseq')

        mutations_options = move_unsatisfied + exchange_unsatisfied_genes + reverse_subseq + no_mutation
        mutation_choice = randint(0, mutations_options)

        if mutation_choice <= move_unsatisfied:
            unsatisfied_indices = [i for i in range(len(satisfied)) if not satisfied[i]]
            if not unsatisfied_indices:
                return self
            new_chromosome = chromosome.move_unsatisfied_gene(unsatisfied_indices)

        elif mutation_choice <= move_unsatisfied + exchange_unsatisfied_genes:
            new_chromosome = chromosome.exchange_unsatisfied_genes(satisfied)

        elif mutation_choice <= move_unsatisfied + exchange_unsatisfied_genes + reverse_subseq:
            new_chromosome = chromosome.reverse_subseq()

        else:
            return self

        new_individual = GA_World.individual_class(new_chromosome)
        return new_individual

    def satisfied_string(self):
        satisfied: List[bool] = self.satisfied
        sat_str = f'{" ".join([" " if satisfied[i] else "^" for i in range(len(satisfied))])}'
        return sat_str


class Parentheses_World(GA_World):

    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)

    def gen_gene_pool(self):
        chromosome_length = gui_get('chrom_length')
        lefts_rights = chromosome_length//2
        lefts = ['('] * lefts_rights
        rights = [')'] * lefts_rights
        GA_World.gene_pool = sample(lefts + rights, chromosome_length)

    @staticmethod
    def gen_individual():
        chromosome_tuple: Tuple[Gene] = GA_World.chromosome_class(Gene(id, val)
                                                                  for (id, val) in zip(count(), GA_World.gene_pool))
        individual = GA_World.individual_class(chromosome_tuple)
        return individual

    def set_results(self):
        """ Find and display the best individual. """
        super().set_results()
        assert isinstance(self.best_ind, Parentheses_Individual)
        best_ind: Parentheses_Individual = self.best_ind
        print(f'Gen {self.generations}.  {best_ind.fitness}: {best_ind.chromosome.chromosome_string()}\n'
              f'{" "*(9 + len(str(self.generations))+len(str(best_ind.fitness)))}'
              f'{best_ind.satisfied_string()}')

    def setup(self):
        GA_World.individual_class = Parentheses_Individual
        GA_World.chromosome_class = Parentheses_Chromosome
        gui_set('Max generations', value=float('inf'))
        Parentheses_World.world = self
        print('---')
        super().setup()


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
paren_gui_left_upper = gui_left_upper \
                     + [
                        [sg.Text('Prob no mutation', pad=((0, 5), (10, 0))),
                         sg.Slider(key='no_mutation', range=(0, 100), resolution=1, default_value=10,
                                   orientation='horizontal', size=(10, 20))
                         ],

                         [sg.Text('Prob move unsatisfied gene', pad=((0, 5), (20, 0))),
                          sg.Slider(key='move_unsatisfied_gene', range=(0, 100), default_value=25,
                                    orientation='horizontal', size=(10, 20))
                          ],

                        [sg.Text('Prob exchange two unsatisfied genes', pad=((0, 5), (20, 0))),
                         sg.Slider(key='exchange_unsatisfied_genes', range=(0, 100), default_value=25,
                                   orientation='horizontal', size=(10, 20))
                         ],

                        [sg.Text('Prob reverse subseq', pad=((0, 5), (20, 0))),
                         sg.Slider(key='reverse_subseq', range=(0, 100), default_value=5,
                                   orientation='horizontal', size=(10, 20))
                         ],

                        [sg.Text('Fitness target', pad=((0, 5), (20, 0))),
                         sg.Slider(key='fitness_target', default_value=0, enable_events=True,
                                   orientation='horizontal', size=(10, 20), range=(0, 10))
                         ],

                        [sg.Text('Chromosome length', pad=(None, (20, 0))),
                         sg.Slider(key='chrom_length', range=(4, 140), enable_events=True, size=(10, 20),
                                   pad=((10, 0), (0, 0)), orientation='horizontal', default_value=50,
                                   resolution=2)
                         ],

                        ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Parentheses_World, 'GA Parentheses', paren_gui_left_upper, patch_size=10, board_rows_cols=(10, 10))
