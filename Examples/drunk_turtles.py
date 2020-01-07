


import core_elements as core


class DrunkTurtle_Turtle(core.Turtle):

    def __init__(self):
        super().__init__()
        self.speed = 0


class DrunkTurtle_World(core.World):

    def __init__(self):
        super().__init__()
        self.center_pixels = core.SimEngine.CENTER_PIXELS





    def step(self, event, values):
        for turtle in se.SimEngine.WORLD.turtles:
            turtle.fd(turtle.speed)