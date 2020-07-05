from pygame import Color  # Color Names (https://github.com/pygame/pygame/blob/master/src_py/colordict.py)
from random import choice, randint
from core.agent import Agent, PYGAME_COLORS
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World
import core.gui as gui
from math import floor

# Dimension 51 * 51

GRASS = [Color('green2'), Color('green3'), Color('green4')]
CARS = [Color('black'), Color('white'), Color('gray')]
DYNAMIC = Color('yellow')
STATIC = Color('orange')

# self.patches is 1D array of 51*51 elements. 2D index mapping > [TWO_DIM * row + col]
TWO_DIM = 51
TOP_LEFT = TWO_DIM * 5 + 5
TOP_RIGHT = TWO_DIM * 5 + 46
BOTTOM_LEFT = TWO_DIM * 46 + 5
BOTTOM_RIGHT = TWO_DIM * 46 + 46


class BraessParadoxAgent(Agent):

    def __init__(self, route):
        super().__init__()
        self.label = str(self.id)
        self.birth_tick = World.ticks
        self.ticks_here = 1
        self.route = route
        self.move_to_patch(World.patches[TOP_LEFT])
        if self.route == 0 or self.route == 2:
            self.set_heading(90)
        else:
            self.set_heading(180)
        self.set_color(choice(CARS))

    # Agent's movement
    def commuter_move(self):
        # Current patch's row and column
        pRow, pCol = self.current_patch().row_col

        if self.current_patch() == World.patches[TOP_RIGHT] and self.route == 0:
            self.set_heading(180)

        if self.current_patch() == World.patches[TOP_RIGHT] and self.route == 2:
            self.set_heading(225)

        if self.current_patch() == World.patches[BOTTOM_LEFT]:
            self.set_heading(90)

        if self.current_patch() == World.patches[BOTTOM_RIGHT]:
            self.end_commute()

        if self.ticks_here > BraessParadoxWorld.patch_vari[TWO_DIM * pRow + pCol]['delay']:
            BraessParadoxWorld.patch_vari[TWO_DIM * pRow + pCol]['last_here'] = World.ticks
            if self.heading == 90:
                self.move_to_patch(World.patches[TWO_DIM * pRow + (pCol + 1)])
            if self.heading == 180:
                self.move_to_patch(World.patches[TWO_DIM * (pRow + 1) + pCol])
            if self.heading == 225:
                self.forward(100)
            self.ticks_here = 1
        else:
            self.ticks_here += 1

    def end_commute(self):
        BraessParadoxWorld.travel_time = (World.ticks - self.birth_tick) / 450
        if BraessParadoxWorld.avg == 0:
            BraessParadoxWorld.avg = BraessParadoxWorld.travel_time
        else:
            BraessParadoxWorld.avg = ((19 * BraessParadoxWorld.avg + BraessParadoxWorld.travel_time) / 20)

        if self.route == 0:
            if BraessParadoxWorld.top == 0:
                BraessParadoxWorld.top = BraessParadoxWorld.travel_time
            else:
                BraessParadoxWorld.top = (BraessParadoxWorld.travel_time + (
                        SimEngine.gui_get(SMOOTHING) - 1) * BraessParadoxWorld.top) / SimEngine.gui_get(SMOOTHING)
        else:
            if self.route == 1:
                if BraessParadoxWorld.bottom == 0:
                    BraessParadoxWorld.bottom = BraessParadoxWorld.travel_time
                else:
                    BraessParadoxWorld.bottom = (BraessParadoxWorld.travel_time + (
                            SimEngine.gui_get(SMOOTHING) - 1) * BraessParadoxWorld.bottom) / SimEngine.gui_get(
                        SMOOTHING)
            else:
                if BraessParadoxWorld.middle == 0:
                    BraessParadoxWorld.middle = BraessParadoxWorld.travel_time
                else:
                    BraessParadoxWorld.middle = (BraessParadoxWorld.travel_time + (
                            SimEngine.gui_get(SMOOTHING) - 1) * BraessParadoxWorld.middle) / SimEngine.gui_get(
                        SMOOTHING)

        # World.agents.remove gave errors, so move the agent to off-road instead
        self.move_to_patch(World.patches[BOTTOM_RIGHT + 3])
        self.set_heading(0)
        print(BraessParadoxWorld.travel_time)


class BraessParadoxWorld(World):
    travel_time = None
    top = None
    bottom = None
    middle = None
    spawn_time = None
    middle_prev = None
    avg = None
    cars_spawned = None
    top_prob = None
    bottom_prob = None
    middle_prob = None
    patch_vari = None

    def init_glob_vari(self):
        BraessParadoxWorld.travel_time = 0
        BraessParadoxWorld.top = 0
        BraessParadoxWorld.bottom = 0
        BraessParadoxWorld.middle = 0
        BraessParadoxWorld.spawn_time = 0
        BraessParadoxWorld.middle_prev = SimEngine.gui_get(MIDDLE_ROUTE)
        BraessParadoxWorld.avg = 0
        BraessParadoxWorld.cars_spawned = 0
        BraessParadoxWorld.top_prob = 0
        BraessParadoxWorld.bottom_prob = 0
        BraessParadoxWorld.middle_prob = 0
        BraessParadoxWorld.patch_vari = []

    def setup_road(self):
        for patch in self.patches:
            # Create list same size as number of patches. Will use to hold the patch variables
            patch_variables = {'delay': 0, 'base_delay': None, 'road_type': None, 'last_here': 0}
            BraessParadoxWorld.patch_vari.append(patch_variables)
            patch.set_color(choice(GRASS))

        # Vertical roads
        Vert = 4
        while Vert < 48:
            self.patches[TWO_DIM * Vert + 4].set_color(Color('gray85'))
            self.patches[TWO_DIM * Vert + 5].set_color(Color('gray85'))
            self.patches[TWO_DIM * Vert + 6].set_color(Color('gray85'))
            self.patches[TWO_DIM * Vert + 45].set_color(Color('gray85'))
            self.patches[TWO_DIM * Vert + 46].set_color(Color('gray85'))
            self.patches[TWO_DIM * Vert + 47].set_color(Color('gray85'))
            Vert += 1

        # Horizontal roads
        Hori = 7
        while Hori < 45:
            self.patches[TWO_DIM * 4 + Hori].set_color(Color('gray85'))
            self.patches[TWO_DIM * 5 + Hori].set_color(Color('gray85'))
            self.patches[TWO_DIM * 6 + Hori].set_color(Color('gray85'))
            self.patches[TWO_DIM * 45 + Hori].set_color(Color('gray85'))
            self.patches[TWO_DIM * 46 + Hori].set_color(Color('gray85'))
            self.patches[TWO_DIM * 47 + Hori].set_color(Color('gray85'))
            Hori += 1

        # Corners
        self.patches[TOP_LEFT].set_color(Color('green'))
        self.patches[TOP_RIGHT].set_color(Color('blue'))
        self.patches[BOTTOM_LEFT].set_color(Color('blue'))
        self.patches[BOTTOM_RIGHT].set_color(Color('red'))
        self.patches[TWO_DIM * 4 + 4].set_color(Color('gray85'))

        self.draw_roads()

    def draw_roads(self):
        # draw dynanic roads
        dynamic = 6
        while dynamic < 46:
            self.patches[TWO_DIM * 5 + dynamic].set_color(DYNAMIC)
            BraessParadoxWorld.patch_vari[TWO_DIM * 5 + dynamic]['delay'] = 5
            BraessParadoxWorld.patch_vari[TWO_DIM * 5 + dynamic]['road_type'] = 0
            BraessParadoxWorld.patch_vari[TWO_DIM * 5 + dynamic]['base_delay'] = 10

            self.patches[TWO_DIM * 46 + dynamic].set_color(DYNAMIC)
            BraessParadoxWorld.patch_vari[TWO_DIM * 46 + dynamic]['delay'] = 5
            BraessParadoxWorld.patch_vari[TWO_DIM * 46 + dynamic]['road_type'] = 0
            BraessParadoxWorld.patch_vari[TWO_DIM * 46 + dynamic]['base_delay'] = 10
            dynamic += 1

        # draw static roads
        static = 6
        while static < 46:
            self.patches[TWO_DIM * static + 5].set_color(STATIC)
            BraessParadoxWorld.patch_vari[TWO_DIM * static + 5]['delay'] = 10
            BraessParadoxWorld.patch_vari[TWO_DIM * static + 5]['road_type'] = 1

            self.patches[TWO_DIM * static + 46].set_color(STATIC)
            BraessParadoxWorld.patch_vari[TWO_DIM * static + 46]['delay'] = 10
            BraessParadoxWorld.patch_vari[TWO_DIM * static + 46]['road_type'] = 1
            static += 1

        # draw middle road
        self.draw_middle()

    def draw_middle(self):
        if SimEngine.gui_get(MIDDLE_ROUTE):
            MidRow = 7
            MidCol = 44
            while MidRow < 45 and MidCol > 6:
                self.patches[TWO_DIM * MidRow + MidCol].set_color(Color('white'))
                if MidRow != 44:
                    self.patches[TWO_DIM * (MidRow + 1) + MidCol].set_color(Color('darkgray'))
                    self.patches[TWO_DIM * MidRow + MidCol - 1].set_color(Color('darkgray'))
                    if MidRow != 43:
                        self.patches[TWO_DIM * MidRow + MidCol - 2].set_color(Color('black'))
                if MidCol != 44 and MidCol != 43:
                    self.patches[TWO_DIM * MidRow + 2 + MidCol].set_color(Color('black'))
                MidRow += 1
                MidCol -= 1
        else:
            MidRow = 7
            MidCol = 44
            while MidRow < 45 and MidCol > 6:
                self.patches[TWO_DIM * MidRow + MidCol].set_color(Color('steelblue1'))
                if MidRow != 44:
                    self.patches[TWO_DIM * (MidRow + 1) + MidCol].set_color(Color('skyblue'))
                    self.patches[TWO_DIM * MidRow + MidCol - 1].set_color(Color('skyblue'))
                    if MidRow != 43:
                        self.patches[TWO_DIM * MidRow + MidCol - 2].set_color(Color('white'))
                if MidCol != 44 and MidCol != 43:
                    self.patches[TWO_DIM * MidRow + 2 + MidCol].set_color(Color('white'))

                MidRow += 1
                MidCol -= 1

    def spawn_commuters(self, spawn_rate):
        if BraessParadoxWorld.spawn_time > (250 / spawn_rate):
            route = self.new_route()
            BraessParadoxAgent(route)
            BraessParadoxWorld.cars_spawned += 1
            BraessParadoxWorld.spawn_time = 0

        else:
            BraessParadoxWorld.spawn_time += 1

    def new_route(self):
        if SimEngine.gui_get(MODE) == BRR:
            return self.best_random_route()
        else:
            if SimEngine.gui_get(MODE) == AR:
                return self.analytical_route()
            else:
                if SimEngine.gui_get(MODE) == PGR:
                    return self.probabilistic_greedy_route()
                else:
                    return 0

    def best_random_route(self):
        if SimEngine.gui_get(MIDDLE_ROUTE):
            if BraessParadoxWorld.middle == 0 or BraessParadoxWorld.top == 0 or BraessParadoxWorld.bottom == 0:
                return randint(0, 2)
            else:
                if randint(0, 99) < 100 - SimEngine.gui_get(RANDOMNESS):
                    if BraessParadoxWorld.middle < BraessParadoxWorld.top and BraessParadoxWorld.middle < BraessParadoxWorld.bottom:
                        return 2
                    else:
                        if BraessParadoxWorld.top < BraessParadoxWorld.middle and BraessParadoxWorld.top < BraessParadoxWorld.bottom:
                            return 0
                        else:
                            return 1
                else:
                    return randint(0, 2)
        else:
            if BraessParadoxWorld.top == 0 or BraessParadoxWorld.bottom == 0:
                return randint(0, 1)
            else:
                if randint(0, 99) < 100 - SimEngine.gui_get(RANDOMNESS):
                    if BraessParadoxWorld.top < BraessParadoxWorld.bottom:
                        return 0
                    else:
                        return 1
                else:
                    return randint(0, 1)

    def analytical_route(self):
        commuters = len(World.agents)
        top_route = 0
        middle_route = 0
        bottom_route = 0
        for agent in World.agents:
            if agent.route == 0:
                top_route += 1
            if agent.route == 1:
                bottom_route += 1
            if agent.route == 2:
                middle_route += 1

        if SimEngine.gui_get(MIDDLE_ROUTE):
            if commuters == 0:
                return randint(0, 2)
            else:
                top_score = ((top_route + middle_route) / commuters) * 1 + 1
                bottom_score = ((bottom_route + middle_route) / commuters) * 1 + 1
                middle_score = (middle_route / commuters) * 2
                print(f' tRoute: {top_route}, mRoute: {middle_route}, bRoute: {bottom_route}')
                print(f' top: {top_score}, middle: {middle_score}, bottom: {bottom_score}')
                print(f' commuters: {commuters}')
                if top_score < bottom_score and top_score < middle_score:
                    return 0
                else:
                    if bottom_score < middle_score and bottom_score < top_score:
                        return 1
                    else:
                        if top_score == bottom_score and middle_score == top_score:
                            return randint(0, 2)
                        else:
                            return 2
        else:
            if commuters == 0:
                return randint(0, 1)
            else:
                top_score = (top_route / commuters) * 1 + 1
                bottom_score = (bottom_route / commuters) * 1 + 1
                if top_score < bottom_score:
                    return 0
                else:
                    return 1

    def probabilistic_greedy_route(self):
        if SimEngine.gui_get(MIDDLE_ROUTE):
            if BraessParadoxWorld.middle == 0 or BraessParadoxWorld.top == 0 or BraessParadoxWorld.bottom == 0:
                return randint(0, 2)
            else:
                t_dif = 2 - BraessParadoxWorld.top
                if t_dif < 0:
                    t_dif = 0
                t_dif = t_dif ** ((SimEngine.gui_get(RANDOMNESS) / 10))

                b_dif = 2 - BraessParadoxWorld.bottom
                if b_dif < 0:
                    b_dif = 0
                b_dif = b_dif ** ((SimEngine.gui_get(RANDOMNESS) / 10))

                m_dif = 2 - BraessParadoxWorld.middle
                if m_dif < 0:
                    m_dif = 0
                m_dif = m_dif ** ((SimEngine.gui_get(RANDOMNESS) / 10))

                sigma_1 = 0
                sigma_2 = 0
                if not (t_dif + b_dif + m_dif) == 0:
                    sigma_1 = t_dif / (t_dif + b_dif + m_dif)
                    sigma_2 = b_dif / (t_dif + b_dif + m_dif)
                else:
                    sigma_1 = 0.33
                    sigma_2 = 0.33
                BraessParadoxWorld.top_prob = sigma_1
                BraessParadoxWorld.bottom_prob = sigma_2
                BraessParadoxWorld.middle_prob = 1 - sigma_1 - sigma_2
                split_1 = 1000 * sigma_1
                split_2 = 1000 * (sigma_1 + sigma_2)
                rand = randint(0, 999)
                if rand < split_1:
                    return 0
                else:
                    if rand < split_2:
                        return 1
                    else:
                        return 2
        else:
            if BraessParadoxWorld.top == 0 or BraessParadoxWorld.bottom == 0:
                return randint(0, 1)
            else:
                t_dif = (2 - BraessParadoxWorld.top) ** (SimEngine.gui_get(RANDOMNESS) / 10)
                b_dif = (2 - BraessParadoxWorld.bottom) ** (SimEngine.gui_get(RANDOMNESS) / 10)
                sigma = t_dif / (t_dif + b_dif)
                BraessParadoxWorld.top_prob = sigma
                BraessParadoxWorld.bottom_prob = 1 - sigma
                split = 1000 * sigma
                if randint(0, 999) < split:
                    return 0
                else:
                    return 1

    # Middle route can be turned off only if no commuters are going to use the route.
    def check_middle(self):
        middle_route = 0
        for agent in World.agents:
            if agent.route == 2:
                middle_route += 1

        if SimEngine.gui_get(MIDDLE_ROUTE) != BraessParadoxWorld.middle_prev:
            if SimEngine.gui_get(MIDDLE_ROUTE):
                self.draw_middle()
                BraessParadoxWorld.middle_prev = SimEngine.gui_get(MIDDLE_ROUTE)
            else:
                if middle_route == 0:
                    BraessParadoxWorld.middle_prev = SimEngine.gui_get(MIDDLE_ROUTE)

    def determine_congestion(self, dynamic_patch):
        if dynamic_patch['last_here'] == 0:
            dynamic_patch['delay'] = int(dynamic_patch['base_delay'] / 2)
        else:
            dynamic_patch['delay'] = floor(
                ((250 / SimEngine.gui_get(SPAWN_RATE)) / (World.ticks - dynamic_patch['last_here'] + 1)) *
                dynamic_patch['base_delay'])

    def setup(self):
        self.init_glob_vari()
        self.setup_road()
        Agent.id = 0
        SimEngine.gui_set('ticks', value=World.ticks)
        print(BraessParadoxWorld.spawn_time)

    def step(self):
        self.check_middle()
        SimEngine.gui_set('ticks', value=World.ticks)
        spawn_rate = SimEngine.gui_get(SPAWN_RATE)
        self.spawn_commuters(spawn_rate)
        # if World.ticks % 15 == 0:
        for agent in World.agents:
            agent.commuter_move()

        for patch in BraessParadoxWorld.patch_vari:
            if patch['road_type'] == 0:
                self.determine_congestion(patch)


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

SPAWN_RATE = 'spawn rate'
SMOOTHING = 'smoothing'
MODE = 'mode'
BRR = 'best known /w random deviation'
AR = 'empirical analytical'
PGR = 'probabilistic greedy'
RANDOMNESS = 'randomness'
MIDDLE_ROUTE = 'middle route'

gui_left_upper = [[sg.Text('Braess Paradox: Another Road')],
                  [sg.CB(MIDDLE_ROUTE, key=MIDDLE_ROUTE, pad=((30, 0), (0, 0)), enable_events=True)],

                  [sg.Text('Spawn Rate'),
                   sg.Slider(key=SPAWN_RATE, range=(1, 10), resolution=1, size=(10, 20),
                             default_value=10, orientation='horizontal', pad=((0, 0), (0, 10)),
                             tooltip='Adjust the rate of car gerenation')],

                  [sg.Text('Smoothing'),
                   sg.Slider(key=SMOOTHING, range=(1, 10), resolution=1, size=(10, 20),
                             default_value=10, orientation='horizontal', pad=((0, 0), (0, 10)),
                             tooltip='Kind of just here for now')],

                  [sg.Text('Mode'),
                   sg.Combo(key=MODE, values=['none', BRR, AR, PGR],
                            default_value='none',
                            tooltip='Route decision making algorithm to help choosing fastest route')],

                  [sg.Text('Randomness'),
                   sg.Slider(key=RANDOMNESS, range=(0, 100), resolution=1, size=(10, 20),
                             default_value=10, orientation='horizontal', pad=((0, 0), (0, 10)),
                             tooltip='Percentage of getting only the best route')],

                  [sg.Text('Ticks:', pad=(None, (10, 0))), sg.Text('        0', key='ticks', pad=(None, (10, 0)))]
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo

    PyLogo(BraessParadoxWorld, "Braess Paradox Model", gui_left_upper, auto_setup=False)