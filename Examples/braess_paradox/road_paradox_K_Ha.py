
# Kit Ha, Micky Chan, Noah Castro
# Goal is create a simulator for Braess Road
# We will be basing our design off the NetLogo model equivalent
# as well as using PyLogo's framework developed by Russ Abbot

from __future__ import annotations

import random

from pygame.color import Color

from core.agent import Agent
from core.gui import SCREEN_PIXEL_WIDTH
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World

#  Variables
CORNERS = {'UP_LEFT':(4,4), 'BOT_LEFT':(46,4),'UP_RIGHT':(4,46), 'BOT_RIGHT':(46,46)}

class global_vars():
    ticks = World.ticks
    spawn_rate = 15
    smoothing = 1
    middle_on = False
    mode = None
    randomness = 0

    travel_time = 0
    top = 0
    bottom = 0
    middle = 0
    spawn_time = 0
    middle_prev = False
    avg = 0
    cars_spawned = 0
    top_prob = 0
    bottom_prob = 0
    middle_prob = 0
    top_left = None
    top_right = None
    bottom_right = None
    bottom_left = None

class Braess_Patch(Patch):
    delay = 0
    base_delay = 0
    road_type = 0
    last_here = 0

    def determine_congestion(self):
        if gb.last_here == 0:
            self.delay = self.base_delay // 2
        else:
            self.delay = int(((250 / gb.spawn_rate) / (gb.ticks - self.last_here + 1)) * self.base_delay)

class Commuter(Agent):
    birth_tick = 0
    ticks_here = 0
    route = 0
    patch = None

    kill = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch = self.current_patch()

    def move_commuter(self):
        if self.ticks_here > self.current_patch().delay:
            self.current_patch().last_here = gb.ticks
            nxt = self.next_patch()
            self.move_to_patch(nxt)
            self.ticks_here = 1
        else:
            self.ticks_here = self.ticks_here + 1

        if self.current_patch() == gb.top_right and self.route == 0:
            self.heading = self.heading_toward(gb.bottom_right)
        if self.current_patch() == gb.top_right and self.route == 2:
            self.heading = self.heading_toward(gb.bottom_left)
        if self.current_patch() == gb.bottom_left:
            self.heading = self.heading_toward(gb.bottom_right)
        if self.current_patch() == gb.bottom_right:
            self.heading = self.end_commute()
        # print(self.heading)
        # print(f"route: {self.route}")

    def next_patch(self):
        (row, col) = self.current_patch().row_col

        if self.heading == 90:
            return World.patches_array[row, col + 1]
        elif self.heading == 180:
            return World.patches_array[row + 1, col]
        elif self.heading == 225:
            return World.patches_array[row + 1, col - 1]

    def end_commute(self):
        self.kill = True

        gb.travel_time = (gb.ticks - self.birth_tick)/450
        if gb.avg == 0:
            gb.avg = gb.travel_time
        else:
            gb.avg = ((19*gb.avg + gb.travel_time) / 20)

        if self.route == 0:
            if gb.top == 0:
                gb.top = gb.travel_time
            else:
                gb.top = (gb.travel_time + ((gb.smoothing - 1) * gb.top)) / gb.smoothing

        if self.route == 1:
            if gb.bottom == 0:
                gb.bot = gb.travel_time
            else:
                gb.bot = (gb.travel_time + ((gb.smoothing - 1) * gb.bottom)) / gb.smoothing
        else:
            if gb.middle == 0:
                gb.middle = gb.travel_time
            else:
                gb.middle = (gb.travel_time + ((gb.smoothing - 1) * gb.middle)) / gb.smoothing


class Braess_World(World):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = int(SCREEN_PIXEL_WIDTH() / 2)
        self.x_offset = 20

        self.init_globals()

        self.commuters = []
        self.setup()

    def check_middle(self):
        if gb.middle_on != gb.middle_prev:
            if gb.middle_on:
                self.close_middle(False)
                gb.middle_prev = gb.middle_on
            else:
                count = self.count_route(2)
                if count == 0:
                    self.close_middle(True)
                    gb.middle_prev = gb.middle_on

    def count_route(self, route):
        count = 0
        for commuter in World.agents:
            if commuter.route == route:
                count += 1
        return count

    def draw_roads(self):
        # Sets up roads
        for i in range(5,46):
            up = 4
            left = 4
            bot = 46
            right = 46
            World.patches_array[up, i].set_color(Color('White'))
            World.patches_array[bot, i].set_color(Color('White'))
            World.patches_array[i, left].set_color(Color('White'))
            World.patches_array[i, right].set_color(Color('White'))

            World.patches_array[i, 50 - i].set_color(Color('Green'))
            World.patches_array[i, 49 - i].set_color(Color('White'))
            World.patches_array[i, 51 - i].set_color(Color('White'))

    def close_middle(self, yes):
        if yes:
            for i in range(5,46):
                World.patches_array[i, 50 - i].set_color(Color('Black'))
                if i < 45:
                    World.patches_array[i, 49 - i].set_color(Color('Black'))
                if i > 5:
                    World.patches_array[i, 51 - i].set_color(Color('Black'))
        else:
            for i in range(5,46):
                World.patches_array[i, 50 - i].set_color(Color('Green'))
                World.patches_array[i, 49 - i].set_color(Color('White'))
                World.patches_array[i, 51 - i].set_color(Color('White'))

    def draw_corners(self):
        for (row, col) in CORNERS.values():
            patch = World.patches_array[row, col]
            patch.set_color(Color('Red'))

    def handle_event(self, event):
        super().handle_event(event)

        # print('event:', event)
        if event in ['Randomness', 'Algorithm', 'Middle', 'Spawn Rate', 'Smoothing']:
            self.init_globals()
            self.check_middle()

    def init_globals(self):
        gb.randomness = SimEngine.gui_get('Randomness')
        gb.mode = SimEngine.gui_get('Algorithm')
        gb.middle_on = SimEngine.gui_get('Middle')
        gb.spawn_rate = SimEngine.gui_get('Spawn Rate')
        gb.smoothing = SimEngine.gui_get('Smoothing')
        gb.top_left = World.patches_array[4, 4]
        gb.top_right = World.patches_array[4, 46]
        gb.bottom_right = World.patches_array[46, 46]
        gb.bottom_left = World.patches_array[46, 4]

    def new_route(self):
        if gb.mode == 'Analytical':
            # print('analysis')
            return self.analytical_route()
        elif gb.mode == 'Random':
            # print('random')
            return self.best_random_route()
        elif gb.mode == 'Probabilistic Greedy':
            # print('greedy')
            return self.probablistic_greedy_route()

    def analytical_route(self):
        other = len(World.agents) - 1
        if gb.middle_on:
            if other == 0:
                return random.choice(range(3))
            else:
                top_score = 1 + (self.count_route(0) + self.count_route(2)) / other
                bot_score = 1 + (self.count_route(1) + self.count_route(2)) / other
                mid_score = 2 * self.count_route(2) / other

                if top_score == bot_score and mid_score == top_score:
                    return random.choice(range(3))

                scores = [top_score, bot_score, mid_score]
                if min(scores) == top_score:
                    return 0
                elif min(scores) == bot_score:
                    return 1
                else:
                    return 2
        else:
            if other == 0:
                return random.choice(range(2))
            else:
                top_score = 1 + (self.count_route(0)/other)
                bot_score = 1 + (self.count_route(1)/other)
                return 0 if top_score < bot_score else 1

    def best_random_route(self):
        if gb.middle_on:
            if gb.middle == 0 or gb.top == 0 or gb.bottom == 0:
                return random.choice(range(3))
            else:
                if random.choice(range(100)) < 100 - gb.randomness:
                    if min([gb.middle, gb.top, gb.bottom]) == gb.middle:
                        return 2
                    elif min([gb.middle, gb.top, gb.bottom]) == gb.top:
                        return 0
                    else:
                        return 1
                else:
                    return random.choice(range(3))
        else:
            if gb.top == 0 or gb.bottom == 0:
                return random.choice(range(2))
            else:
                if random.choice(range(100)) < 100 - gb.randomness:
                    return 0 if min([gb.top, gb.bot]) == gb.top else 1
                else:
                    return random.choice(range(2))

    def probablistic_greedy_route(self):
        if gb.middle_on:
            if gb.middle == 0 or gb.top == 0 or gb.bottom == 0:
                return random.choice(range(3))
            else:
                t_dif = max(2 - gb.top, 0)
                t_dif = pow(t_dif, gb.randomness/10)

                b_dif = max(2 - gb.bottom)
                b_dif = pow(b_dif, gb.randomness / 10)

                m_dif = max(2 - gb.middle)
                m_dif = pow(m_dif, gb.randomness / 10)

                if not (t_dif + b_dif + m_dif):
                    sigma1 = t_dif/ (t_dif + b_dif + m_dif)
                    sigma2 = b_dif/ (t_dif + b_dif + m_dif)
                else:
                    sigma1 = 0.33
                    sigma2 = 0.33

                gb.top_prob = sigma1
                gb.bottom_prob = sigma2
                gb.middle_prob = 1 - sigma1 - sigma2
                split1 = 1000 * sigma1
                split2 = 1000 * (sigma1 + sigma2)
                rand = random.choice(range(1000))
                if rand < split1:
                    return 0
                elif rand < split2:
                    return 1
                else:
                    return 2
        else:
            if gb.top == 0 or gb.bottom == 0:
                return random.choice(range(2))
            else:
                t_dif = pow((2 - gb.top), gb.randomness/10)
                b_dif = pow((2 - gb.bottom), gb.randomness / 10)
                sigma = t_dif/(t_dif + b_dif)
                gb.top_prob = sigma
                gb.bottom_prob = 1 - sigma
                split = 1000 * sigma
                if random.choice(range(1000)) < split:
                    return 0
                else:
                    return 1

    def setup(self):
        self.draw_corners()
        self.draw_roads()
        self.spawn_commuters()
        self.init_globals()
        self.close_middle(not gb.middle_on)

    def spawn_commuters(self):
        if gb.spawn_time > (250 / gb.spawn_rate):
            self.sprout_commuters(1)
            gb.spawn_time = 0
        else:
            gb.spawn_time += 1
        # self.commuters.append(self.agent_class())
        # self.commuters[-1].move_to_patch(World.patches_array[4, 4])
        # self.commuters[-1].set_heading(90)
        # self.commuters[-1].set_velocity((Velocity((1,0))))
        # self.commuters[-1].set_velocity(Velocity((0,1)))

    def sprout_commuters(self, n):
        for i in range(n):
            commuter = self.agent_class()
            commuter.move_to_patch(gb.top_left)
            commuter.birth_tick = 1
            commuter.ticks_here = 1
            commuter.set_color(Color('Blue'))

            commuter.route = self.new_route()
            if commuter.route == 0 or commuter.route == 2:
                commuter.heading = commuter.heading_toward(gb.top_right)
            elif commuter.route == 1:
                commuter.heading = commuter.heading_toward(gb.bottom_left)

    def step(self):
        self.check_middle()
        self.spawn_commuters()

        end = []
        for commuter in World.agents:
            commuter.move_commuter()
            if commuter.kill:
                end.append(commuter)

        for commuter in end:
            World.agents.remove(commuter)

        for patch in World.patches:
            if patch.road_type == 1:
                patch.determine_congestion()


        gb.ticks = World.ticks

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. There is only one model-specific gui widget.
"""
braess_left_upper = [
    [sg.Checkbox('Middle Road On', key='Middle', default=True, enable_events=True, pad=((20, 0), (20, 0)))],

    [sg.Text('Algorithm', pad=((0,5), (20, 0))),
     sg.Combo(['Analytical','Random','Probabilistic Greedy'], size=(20, 25),key='Algorithm', enable_events=True, pad=((5, 0), (20, 0)),
              default_value='Probabilistic Greedy', tooltip='Algorithm')],

    [sg.Text('Spawn Rate', pad=((0,5), (20,0))),
     sg.Slider(key='Spawn Rate', range=(1,100), resolution=1.0,default_value=20, enable_events=True,
               orientation='horizontal', size=(10,20),
               tooltip='Set the spawn rate for commuters.')],

    [sg.Text('Random    ', pad=((0,5), (20,0))),
     sg.Slider(key='Randomness', range=(0,100), resolution=1,default_value=0, enable_events=True,
               orientation='horizontal', size=(10,20),
               tooltip='Set the randomness of being optimal.')],

    [sg.Text('Smoothing ', pad=((0, 5), (20, 0))),
     sg.Slider(key='Smoothing', range=(1, 20), resolution=0.5, default_value=10, enable_events=True,
               orientation='horizontal', size=(10, 20),
               tooltip='Set the smoothing rate. Higher means put more weight in history.')]
]

if __name__ == '__main__':
    from core.agent import PyLogo

    gb = global_vars()
    PyLogo(Braess_World, "Braess' Road", gui_left_upper=braess_left_upper, agent_class=Commuter, patch_class=Braess_Patch)