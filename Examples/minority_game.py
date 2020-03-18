from __future__ import annotations

from functools import reduce
from random import choice

import core.gui as gui
from core.agent import Agent
from core.sim_engine import SimEngine
from core.utils import int_round
from core.world_patch_block import World


class Minority_Game_Agent(Agent):

    def __init__(self, strategies, starting_patch):
        super().__init__()
        self.label = str(self.id)

        self.strategies = strategies
        self.guess = None
        self.init_agent(starting_patch)

    # noinspection PyAttributeOutsideInit
    def init_agent(self, starting_patch):
        """
        A continuation of __init__ also called from reset_agents(). Includes
        only what's needed to restart a race once one has already been run.
        """
        self.strategy_scores = [0] * len(self.strategies)
        # Could also use:          randint(0, len(self.strategies)-1)
        self.best_strategy_index = choice(range(len(self.strategies)))
        self.right = 0
        # Must do this because the system removes all agents from their patches when setup is called.
        # If this is called from reset_agents(), the agent's current_patch will not have it in its agents set.
        # Must add it so that move_to_patch() can remove it.
        if self not in self.current_patch().agents:
            self.current_patch().agents.add(self)
        self.move_to_patch(starting_patch)
        self.set_heading(90)

    def get_best_strategy_score(self):
        return self.strategy_scores[self.best_strategy_index]

    def make_selection(self, history_index):
        self.guess = self.strategies[self.best_strategy_index][history_index]
        return self.guess

    def update(self, history_as_index, winner):
        """
        Update this agent.
        """
        # Move winning agents forward one step.
        if self.guess == winner:
            self.right += 1
            self.forward(Minority_Game_World.one_step)

        self.update_strategy_scores(history_as_index, winner)

    def update_strategy_scores(self, history_as_index, winner):
        # Update the strategy scores and pick best strategy
        for strategy_id in range(len(self.strategies)):
            if self.strategies[strategy_id][history_as_index] == winner:
                self.strategy_scores[strategy_id] += 1
            # Pick the best strategy to use in the next round.
            if self.strategy_scores[strategy_id] > self.strategy_scores[self.best_strategy_index]:
                # noinspection PyAttributeOutsideInit
                self.best_strategy_index = strategy_id


class Minority_Game_Random_Agent(Minority_Game_Agent):

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-R'

    def get_best_strategy_score(self):
        return None

    def make_selection(self, _history_index):
        self.guess = choice([0, 1])
        return self.guess

    def update_strategy_scores(self, _history_as_index, _winner):
        # No strategies to update
        pass


class Minority_Game_Prev_Best_Strat_Agent(Minority_Game_Agent):
    """
    If there was a previous game, this agent uses its best strategy
    from that previous game throughout this game.
    If this is the first game, this agent does nothing special.
    """

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-PB'
        self.prev_game_best_strategy_index = None

    def init_agent(self, starting_patch):
        """
        A continuation of __init__ called also from reset_agents(), i.e., for second and
        subsequent games. Includes what's needed to restart a race once one has already
        been run. This agent must save the best strategy from the previous game, if there
        was one, and use it throughout this game.
        """
        super().init_agent(starting_patch)
        ...

    def make_selection(self, history_index):
        """
        You fill in this part. Instead of using self.best_strategy_index
        use the final best_strategy_index from the previous game.
        """
        self.guess = ...
        return self.guess


class Minority_Game_Spying_Agent(Minority_Game_Agent):
    """
    Before deciding on a selection, this agent spies on the other agents to see what they are going to do.
    """

    def __init__(self, strategies, starting_patch):
        super().__init__(strategies, starting_patch)
        self.label += '-Spy'

    def get_best_strategy_score(self):
        return None

    def make_selection(self, history_index):
        """
        You fill in this part.
        Find out what the other agents are going to do and do the opposite of the majority.
        """
        # noinspection PyUnusedLocal
        all_agents = World.agents
        self.guess = ...
        return self.guess

    def update_strategy_scores(self, _history_as_index, _winner):
        # No strategies to update
        pass


class Minority_Game_World(World):

    # These values are used by the agents.
    # Make them easy to access by putting them at the Minority_Game_World class level.
    copy_agents = None

    nbr_agents = None
    one_step = None
    steps_to_win = None

    random_agent_ids = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history_length = None
        self.history = []
        self.agent_vertical_separation = None

    @staticmethod
    def generate_a_strategy(strategy_length):
        strategy = tuple(choice((0, 1)) for _ in range(strategy_length))
        return strategy

    def generate_all_strategies(self):
        # Generate enough strategies for all agents.
        strategy_length = 2 ** self.history_length
        strategies_per_agent = SimEngine.gui_get(STRATEGIES_PER_AGENT)
        strategies = set()
        # Why a while loop rather than a for loop?
        # Why is strategies a set rather than a list?
        # Note strategies is made into a list after the loop.
        while len(strategies) < Minority_Game_World.nbr_agents * strategies_per_agent:
            strategies.add(self.generate_a_strategy(strategy_length))
        strategies = list(strategies)
        return (strategies, strategies_per_agent)
    
    def generate_the_agents(self):
        (strategies, strategies_per_agent) = self.generate_all_strategies()
        self.agent_vertical_separation = gui.PATCH_ROWS / Minority_Game_World.nbr_agents
        for agent_id in range(Minority_Game_World.nbr_agents):
            starting_patch = self.get_starting_patch(agent_id, self.agent_vertical_separation)
            strategies_for_this_agent = strategies[strategies_per_agent*agent_id:strategies_per_agent*(agent_id + 1)]

            # Which agent class (or subclass) is this agent?
            agent_class = Minority_Game_Random_Agent if agent_id in Minority_Game_World.random_agent_ids else \
                          Minority_Game_Agent
            # Create the agent
            agent_class(strategies_for_this_agent, starting_patch)

    def get_starting_patch(self, agent_id, agent_separation):
        starting_patch = self.patches_array[round((agent_id) * agent_separation), 0]
        return starting_patch

    def history_to_index(self):
        # The final argument (0) is optional.
        val = reduce(lambda so_far, next: so_far*2 + next, self.history, 0)
        return val

    @staticmethod
    def max_agent_right():
        return max(agent.right for agent in World.agents)

    def print_final_scores(self):
        print('\n\t       % right '
              '\n\t  -----------------'
              '\n\t  agent  best strat'
              )
        for agent in sorted(World.agents, key=lambda agent: agent.id):
            best_strategy_score = agent.get_best_strategy_score()
            print(f'{agent.id:2}.\t  {int_round(100 * agent.right / self.ticks):3}'
                  f'       {"--" if not best_strategy_score else int_round(100 * best_strategy_score / self.ticks)}'
                  )

    def print_step_info(self, history_as_index, winner):
        leading_agent_right = self.max_agent_right()
        leading_agent_strings = [f'{agent.id}: {agent.right}/{Minority_Game_World.steps_to_win}'
                                 for agent in World.agents if agent.right == leading_agent_right]
        leading_agents = '{' + ", ".join(leading_agent_strings) + '}'
        print(f'{self.ticks}. {self.history}, {history_as_index:2}, {winner}, {leading_agents}')

    def reset_agents(self):
        print('\n\nStarting next race with same agents, same strategies, and a new random history.\n')
        self.history = [choice((0, 1)) for _ in range(self.history_length)]
        World.agents = Minority_Game_World.copy_agents
        for agent in World.agents:
            starting_patch = self.get_starting_patch(agent.id, self.agent_vertical_separation)
            agent.init_agent(starting_patch)
        World.done = False

    def setup(self):
        Agent.id = 0
        Minority_Game_World.steps_to_win = SimEngine.gui_get(STEPS_TO_WIN)
        # Adjust how far one step is based on number of steps needed to win
        Minority_Game_World.one_step = (gui.PATCH_COLS - 2) * gui.BLOCK_SPACING() / Minority_Game_World.steps_to_win
        # For longer/shorter races, speed up/slow down frames/second
        gui.set_fps(round(6*Minority_Game_World.steps_to_win/50))

        # self.done will be True if this a repeat game with the same agents.
        if self.done:
            self.reset_agents()
            return

        # This is the normal setup.
        Minority_Game_World.nbr_agents = SimEngine.gui_get(NBR_AGENTS)
        if Minority_Game_World.nbr_agents % 2 == 0:
            Minority_Game_World.nbr_agents += (1 if Minority_Game_World.nbr_agents < gui.WINDOW[NBR_AGENTS].Range[1]
                                               else (-1))
            # gui.WINDOW[NBR_AGENTS].update(value=Minority_Game_World.nbr_agents)
            SimEngine.gui_set(NBR_AGENTS, value=Minority_Game_World.nbr_agents)
        Minority_Game_World.random_agent_ids = {0, Minority_Game_World.nbr_agents - 1}

        # Generate a random initial history
        self.history_length = SimEngine.gui_get(HISTORY_LENGTH)
        self.history = [choice([0, 1]) for _ in range(self.history_length)]

        self.generate_the_agents()

    # Like NetLogo, PyLogo is a framework: "Don't call us, we'll call you."
    def step(self):
        history_as_index = self.history_to_index()
        one_votes = sum(agent.make_selection(history_as_index) for agent in World.agents)
        winner = 0 if one_votes > Minority_Game_World.nbr_agents/2 else 1
        for agent in World.agents:
            agent.update(history_as_index, winner)

        self.print_step_info(history_as_index, winner)
        self.history = self.history[1:] + [winner]

        if self.max_agent_right() >= Minority_Game_World.steps_to_win:
            World.done = True
            # Keep the agents so that we can use them in the next game, if there is one.
            Minority_Game_World.copy_agents = World.agents
            self.print_final_scores()


# ############################################## Define GUI ############################################## #
# GUI string constants
HISTORY_LENGTH = 'History length'
NBR_AGENTS = 'Number of agents'
STEPS_TO_WIN = 'Steps to win'
STRATEGIES_PER_AGENT = 'Strategies per agent'

import PySimpleGUI as sg
gui_left_upper = [[sg.Text(HISTORY_LENGTH, tooltip='The length of the history record'),
                   sg.Slider(key=HISTORY_LENGTH, range=(0, 8), default_value=5,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The length of the history record')],

                  [sg.Text(NBR_AGENTS,
                           tooltip='The number of agents. \n(Must be an odd number.\nChecked during setup.)'),
                   sg.Slider(key=NBR_AGENTS, range=(1, 35), default_value=25,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of agents. \n(Must be an odd number.\nChecked during setup.)')],

                  [sg.Text(STRATEGIES_PER_AGENT, tooltip='The number of strategies generated for each agent'),
                   sg.Slider(key=STRATEGIES_PER_AGENT, range=(1, 200), default_value=100,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of strategies generated for each agent')],

                  [sg.Text(STEPS_TO_WIN, tooltip='The number of steps required to win'),
                   sg.Slider(key=STEPS_TO_WIN, range=(1, 500), default_value=50, resolution=25,
                             size=(10, 20), orientation='horizontal',
                             tooltip='The number of steps required to win')],
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo

    PyLogo(Minority_Game_World, 'Minority game', gui_left_upper, agent_class=Minority_Game_Agent, fps=6)
