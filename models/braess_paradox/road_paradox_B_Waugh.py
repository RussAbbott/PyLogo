from math import floor
from random import choice, randint, random

# from core.pairs import Pixel_xy, RowCol
from pygame.color import Color

from core import gui
from core.agent import Agent
from core.gui import HOR_SEP
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World


class Commuter(Agent):
    def __init__(self, b_t, **kwargs):
        self.passed_tr = False
        self.passed_bl = False
        self.in_middle = False
        self.ticks_here = 0
        self.route = 0
        self.birth_tick = b_t
        kwargs['color'] = Color("red")

        super().__init__(**kwargs)

    def move(self, initial_speed, move_by_delay):
        if move_by_delay:
            self.forward(gui.BLOCK_SPACING())
            self.ticks_here = 1

        else:
            if self.in_middle:
                self.forward(initial_speed * 10)
            else:
                if self.current_patch().color == Color("green"):
                    speed = initial_speed
                else:
                    speed = (self.current_patch().color.b / 127)
                    if speed <= 1:
                        speed = 1
                self.forward(speed)

    def set_route(self, r):
        self.route = r

    def follow_route(self):
        if self.route == 1:
            self.face_xy(Commuter_World.bot_left.center_pixel)
        else:
            self.face_xy(Commuter_World.top_right.center_pixel)

    def middle(self):
        if self.route == 2:
            return True

    def __str__(self):
        return f'FLN-{self.id}'


class Road_Patch(Patch):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay = 0
        self.base_delay = 0
        self.road_type = 0
        self.last_here = 0

    def determine_congestion(self, spawn_rate, highway, move_by_delay):
        if self.last_here == 0:
            self.delay = int(self.base_delay / 2)
        else:
            self.delay = floor(((250 / spawn_rate) / (World.ticks - self.last_here + 1)) * self.base_delay)
        g = 255 + floor(255 * (0.5 - self.delay / self.base_delay))
        if g < 100:
            g = 100
        if g > 255:
            g = 255

        if self.delay > 10:
            self.delay = 10
        if self.delay < 4:
            self.delay = 4

        if move_by_delay:
            self.set_color(Color(g, g, g))
        else:
            if self in highway.top_road:
                prev_patch = highway.top_road[self.col - 12]
            else:
                prev_patch = highway.bottom_road[self.col - 12]

            prev_patch.set_color(Color(g, g, g))


class Highway:
    def __init__(self, t_r, b_r, l_r, r_r, m_r, o_r):
        self.top_road = t_r
        self.bottom_road = b_r
        self.left_road = l_r
        self.right_road = r_r
        self.outer_road = o_r
        self.middle_road = m_r
        self.middle_prev = True
        self.delay_prev = True

    def create_road(self):
        # outer roads
        for arr in self.outer_road:
            for patch in arr:
                patch.set_color(Color("orange"))
                patch.road_type = 0
        # middle road
        for patch in self.middle_road:
            patch.set_color(Color("yellow"))
            patch.road_type = 0
            patch.delay = 0
        # top road
        for patch in self.top_road:
            patch.set_color(Color("white"))
            patch.road_type = 1
            patch.delay = 5
            patch.base_delay = 10
        # bottom road
        for patch in self.bottom_road:
            patch.set_color(Color("white"))
            patch.road_type = 1
            patch.delay = 5
            patch.base_delay = 10
        # left road
        for patch in self.left_road:
            patch.set_color(Color(100, 100, 100))
            patch.road_type = 0
            patch.delay = 10
        # right road
        for patch in self.right_road:
            patch.set_color(Color(100, 100, 100))
            patch.road_type = 0
            patch.delay = 10

    def check_middle(self, middle_on, delay_on):
        if middle_on != self.middle_prev:
            if middle_on:
                for patch in self.middle_road:
                    patch.set_color(Color("yellow"))
                self.middle_prev = middle_on
                self.check_delay(middle_on, delay_on)
            else:
                if Commuter_World.num_mid == 0:
                    for patch in self.middle_road:
                        patch.set_color(Color("orange"))
                        self.middle_prev = middle_on
                    self.check_delay(middle_on, delay_on)

    def check_delay(self, middle_on, delay_on):
        if delay_on != self.delay_prev:
            # Recreate the road, resetting the delays
            self.create_road()
            for agent in World.agents:
                agent.move_to_patch(agent.current_patch())
            self.delay_prev = delay_on
            self.check_middle(middle_on, delay_on)


class Commuter_World(World):
    top_left = None
    top_right = None
    bot_left = None
    bot_right = None

    top_road = None
    bottom_road = None
    left_road = None
    right_road = None

    travel_time = None
    top = None
    bot = None
    middle = None
    spawn_time = None
    avg = None
    cars_spawned = None

    num_top = None
    num_bot = None
    num_mid = None

    def __init__(self, *args, **kwargs):
        self.patch_class = Road_Patch
        self.fastest_top = 0
        self.fastest_bot = 0
        self.fastest_mid = 0
        self.despawn_list = []
        self.highway = None
        super().__init__(*args, **kwargs)

    def setup_roads(self):
        all_patches = World.patches_array

        # create background
        background = [Color(0, 40, 0), Color(0, 50, 0), Color(0, 60, 0)]
        for patch in World.patches:
            patch.set_color(choice(background))

        World.top_road = all_patches[10, 11:60]
        World.bottom_road = all_patches[60, 11:60]
        World.left_road = all_patches[11:60, 10]
        World.right_road = all_patches[11:60, 60]
        # the outer road is concatenated in this order: top -> left -> right -> bottom
        outer_road = [all_patches[9, 9:62]] + [all_patches[11, 11:58]] + \
                     [all_patches[10:62, 9]] + [all_patches[11:58, 11]] + \
                     [all_patches[13:60, 59]] + [all_patches[10:62, 61]] + \
                     [all_patches[59, 13:60]] + [all_patches[61, 10:61]]

        middle_road = []
        for j in range(11, 60):
            outer_road.append([World.patches_array[j - 2, 70 - j]])
            outer_road.append([World.patches_array[j + 2, 70 - j]])
            middle_road.append(World.patches_array[j - 1, 70 - j])
            middle_road.append(World.patches_array[j, 70 - j])
            middle_road.append(World.patches_array[j + 1, 70 - j])

        # Create all the roads
        self.highway = Highway(World.top_road, World.bottom_road,
                               World.left_road, World.right_road,
                               middle_road, outer_road)
        self.highway.create_road()

        # Make top_left patch
        World.top_left = World.patches_array[10, 10]
        World.top_left.set_color(Color("green"))

        # Make top_right patch
        World.top_right = World.patches_array[10, 60]
        World.top_right.set_color(Color("blue"))

        # Make bot_left patch
        World.bot_left = World.patches_array[60, 10]
        World.bot_left.set_color(Color("blue"))

        # Make bot_right patch
        World.bot_right = World.patches_array[60, 60]
        World.bot_right.set_color(Color("red"))

    def setup(self):
        self.setup_roads()

        World.travel_time = 0
        World.top = 0
        World.bot = 0
        World.middle = 0
        World.spawn_time = 0
        World.avg = 0
        World.cars_spawned = 0
        World.num_top = 0
        World.num_bot = 0
        World.num_mid = 0

    def step(self):
        """
        Update the world by moving the agents.
        """
        spawn_rate = SimEngine.gui_get(SPAWN_RATE)
        middle_on = SimEngine.gui_get(MIDDLE_ON)
        delay_on = SimEngine.gui_get(DELAY_ON)

        # check if the checkboxes have changed (Middle On? and Move by Delay?)
        self.highway.check_delay(middle_on, delay_on)
        self.highway.check_middle(middle_on, delay_on)

        # move the computers
        self.move_commuters()

        # set the patch color and patch delay
        for patch in World.patches:
            if patch.road_type == 1:
                patch.determine_congestion(spawn_rate, self.highway, delay_on)

        # spawn agents
        self.spawn_commuter()

    def new_route(self):
        b = SimEngine.gui_get(SELECTION_ALGORITHM)
        if b == BEST_KNOWN:
            route = self.best_random_route()
        elif b == EMPIRICAL_ANALYTICAl:
            route = self.analytical_route()
        elif b == PROBABILISTIC_GREEDY:
            route = self.probablisitic_greedy_route()
        else:
            route = 0
        return route

    def spawn_commuter(self):
        spawn_rate = SimEngine.gui_get(SPAWN_RATE)
        if World.spawn_time > (250 / spawn_rate):
            World.cars_spawned = len(World.agents)
            a = Commuter(World.ticks, scale=1)
            a.move_to_patch(Commuter_World.top_left)
            a.set_route(self.new_route())
            a.follow_route()
            World.spawn_time = 0
            if a.route == 0:
                World.num_top = World.num_top + 1
            if a.route == 1:
                World.num_bot = World.num_bot + 1
            if a.route == 2:
                World.num_mid = World.num_mid + 1
        else:
            World.spawn_time = World.spawn_time + 1

    def end_commute(self, agent):
        travel_time = (World.ticks - agent.birth_tick) / 450
        smoothing = SimEngine.gui_get('smoothing')
        World.travel_time = travel_time

        if World.avg == 0:
            World.avg = travel_time
        else:
            World.avg = ((len(World.agents) - 1) * World.avg + travel_time) / len(World.agents)
        SimEngine.gui_set(AVERAGE, value=World.avg)

        if agent.route == 0:
            if World.top == 0:
                World.top = travel_time
                self.fastest_top = travel_time
            else:
                World.top = ((travel_time + (smoothing - 1) * World.top) / smoothing)
                if travel_time < self.fastest_top:
                    self.fastest_top = travel_time
            World.num_top = World.num_top - 1

        elif agent.route == 1:
            if World.bot == 0:
                World.bot = travel_time
                self.fastest_bot = travel_time
            else:
                World.bot = ((travel_time + (smoothing - 1) * World.bot) / smoothing)
                if travel_time < self.fastest_bot:
                    self.fastest_bot = travel_time
            World.num_bot = World.num_bot - 1

        else:
            if World.middle == 0:
                World.middle = travel_time
                self.fastest_mid = travel_time
            else:
                World.middle = ((travel_time + (smoothing - 1) * World.middle) / smoothing)
                if travel_time < self.fastest_mid:
                    self.fastest_mid = travel_time
            World.num_mid = World.num_mid - 1

        print(f"Tick:{World.ticks}   T_time:{World.travel_time}   Avg:{World.avg} \n"
              f"Mid_Time:{World.middle}  Top_Time:{World.top} Bot_Time:{World.bot}\n")
        SimEngine.gui_set(FASTEST_TOP, value=self.fastest_top)
        SimEngine.gui_set(FASTEST_BOTTOM, value=self.fastest_bot)
        SimEngine.gui_set(FASTEST_MIDDLE, value=self.fastest_mid)

        self.despawn_list.append(agent)

    def move_commuters(self):
        delay_on = SimEngine.gui_get(DELAY_ON)
        middle_on = SimEngine.gui_get(MIDDLE_ON)

        # delete agents that finished route
        for agent in self.despawn_list:
            if agent in World.agents:
                World.agents.remove(agent)

        for agent in World.agents:

            curr_patch = agent.current_patch()
            if not delay_on:
                curr_patch.delay = -1
            if agent.ticks_here > curr_patch.delay:
                curr_patch.last_here = World.ticks
                agent.move(1, delay_on)
                agent.ticks_here = 1

                if agent.current_patch() is Commuter_World.top_right and agent.route == 0:
                    if not agent.passed_tr:
                        agent.set_center_pixel(Commuter_World.top_right.center_pixel)
                        agent.passed_tr = True
                    agent.face_xy(Commuter_World.bot_right.center_pixel)
                elif agent.current_patch() == Commuter_World.top_right and agent.route == 2:
                    if not agent.passed_tr:
                        agent.set_center_pixel(Commuter_World.top_right.center_pixel)
                        agent.passed_tr = True
                        agent.in_middle = True
                    agent.face_xy(Commuter_World.bot_left.center_pixel)
                elif agent.current_patch() is Commuter_World.bot_left:
                    if not agent.passed_bl:
                        agent.set_center_pixel(Commuter_World.bot_left.center_pixel)
                        agent.passed_bl = True
                        agent.in_middle = False
                    agent.face_xy(Commuter_World.bot_right.center_pixel)
                elif agent.current_patch() is Commuter_World.bot_right:
                    self.end_commute(agent)
            else:
                agent.ticks_here = agent.ticks_here + 1

    def probablisitic_greedy_route(self):
        middle_on = SimEngine.gui_get("middle_on")
        randomness = SimEngine.gui_get("randomness")

        if middle_on:
            if Commuter_World.middle == 0 or Commuter_World.bot == 0 or Commuter_World.top == 0:
                return randint(0, 2)

            t_dif = 2 - Commuter_World.top
            if t_dif < 0:
                t_dif = 0
            t_dif = t_dif ** (randomness / 10)

            b_dif = 2 - Commuter_World.bot
            if b_dif < 0:
                b_dif = 0
            b_dif = b_dif ** (randomness / 10)

            m_dif = 2 - Commuter_World.middle
            if m_dif < 0:
                m_dif = 0
            m_dif = m_dif ** (randomness / 10)

            if not t_dif + b_dif + m_dif == 0:
                sigma1 = t_dif / (t_dif + b_dif + m_dif)
                sigma2 = b_dif / (t_dif + b_dif + m_dif)
            else:
                sigma1 = 0.33
                sigma2 = 0.33

            split1 = 1000 * sigma1
            split2 = 1000 * (sigma1 + sigma2)
            rand = random() * 1000
            if rand < split1:
                return 0
            else:
                if rand < split2:
                    return 1
                else:
                    return 2
        else:
            if Commuter_World.top == 0 or Commuter_World.bot == 0:
                return randint(0, 1)

            t_dif = (2 - Commuter_World.top) ** (randomness / 10)
            b_dif = (2 - Commuter_World.bot) ** (randomness / 10)
            sigma = t_dif / (t_dif + b_dif)
            split = 1000 * sigma
            if (random() * 1000) < split:
                return 0
            else:
                return 1

    def best_random_route(self):
        middle_on = SimEngine.gui_get("middle_on")
        randomness = SimEngine.gui_get("randomness")
        middle = Commuter_World.middle
        bottom = Commuter_World.bot
        top = Commuter_World.top

        if middle_on:
            if middle == 0 or bottom == 0 or top == 0:
                return randint(0, 2)
            elif randint(0, 100) < (100 - randomness):
                if middle < top and middle < bottom:
                    return 2
                elif top < middle and top < bottom:
                    return 0
                else:
                    return 1
            else:
                return randint(0, 2)
        elif top == 0 or bottom == 0:
            return randint(0, 1)
        elif randint(0, 100) < (100 - randomness):
            if top < bottom:
                return 0
            else:
                return 1
        else:
            return randint(0, 1)

    def analytical_route(self):
        middle_on = SimEngine.gui_get("middle_on")
        agents = World.agents
        commuters = len(agents)

        if middle_on:
            if commuters == 0:
                randint(0, 2)
            else:
                top_score = ((self.num_top + self.num_mid) / commuters) * 1 + 1
                bottom_score = ((self.num_bot + self.num_mid) / commuters) * 1 + 1
                middle_score = (self.num_mid / commuters) * 1 + 1
                if top_score < bottom_score and top_score < middle_score:
                    return 0
                elif bottom_score < middle_score and bottom_score < top_score:
                    return 1
                elif top_score == bottom_score and middle_score == top_score:
                    return randint(0, 2)
                else:
                    return 2
        elif commuters == 0:
            return randint(0, 1)
        else:
            top_score = (self.num_top / commuters) * 1 + 1
            bottom_score = (self.num_bot / commuters) * 1 + 1
            if top_score < bottom_score:
                return 0
            else:
                return 1


# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

MIDDLE_ON = 'middle_on'
DELAY_ON = 'delay_on'
SPAWN_RATE = 'spawn rate'
SELECTION_ALGORITHM = 'Selection'
BEST_KNOWN = 'Best Known'
EMPIRICAL_ANALYTICAl = 'Empirical Analytical'
PROBABILISTIC_GREEDY = 'Probabilistic Greedy'
SMOOTHING = 'smoothing'
RANDOMNESS = 'randomness'
AVERAGE = 'average'
FASTEST_TOP = 'fastest top'
FASTEST_MIDDLE = 'fastest middle'
FASTEST_BOTTOM = 'fastest bottom'

gui_left_upper = [[sg.Text('Middle On?', pad=((0, 5), (20, 0))),
                   sg.CB('True', key=MIDDLE_ON, default=True, pad=((0, 5), (20, 0)))],

                  [sg.Text('Move by Delay?', pad=((0, 5), (20, 0))),
                   sg.CB('True', key=DELAY_ON, default=True, pad=((0, 5), (20, 0)))],

                  [sg.Text('Spawn Rate', pad=((0, 5), (20, 0))),
                   sg.Slider(key=SPAWN_RATE, default_value=10, range=(1, 10),
                             pad=((0, 5), (10, 0)), orientation='horizontal', size=(10, 20))],

                  [sg.Text('Smoothing', pad=((0, 5), (20, 0))),
                   sg.Slider(key=SMOOTHING, default_value=10, range=(1, 10), pad=((0, 5), (10, 0)),
                             orientation='horizontal', size=(10, 20))],

                  [sg.Text('Selection', pad=((0, 5), (20, 0))),
                   sg.Combo([BEST_KNOWN, EMPIRICAL_ANALYTICAl, PROBABILISTIC_GREEDY],
                            key=SELECTION_ALGORITHM, default_value=BEST_KNOWN,
                            tooltip='Selection Algorithm', pad=((0, 5), (20, 0)))],

                  [sg.Text('Randomness', pad=((0, 5), (20, 0))),
                   sg.Slider(key=RANDOMNESS, default_value=16, resolution=1,
                             range=(0, 100), pad=((0, 5), (10, 0)),
                             orientation='horizontal', size=(10, 20))],

                  HOR_SEP(pad=((30, 0), (0, 0))),

                  [sg.Text('Average = '), sg.Text('         0', key=AVERAGE)],
                  [sg.Text('Fastest Top Time = '), sg.Text('         0', key=FASTEST_TOP)],
                  [sg.Text('Fastest Middle Time = '), sg.Text('         0', key=FASTEST_MIDDLE)],
                  [sg.Text('Fastest Bottom Time = '), sg.Text('         0', key=FASTEST_BOTTOM)]
                  ]

if __name__ == "__main__":
    from core.agent import PyLogo

    PyLogo(Commuter_World, 'Paradox', gui_left_upper, agent_class=Commuter, patch_class=Road_Patch,
           bounce=True, patch_size=9,
           board_rows_cols=(71, 71))
