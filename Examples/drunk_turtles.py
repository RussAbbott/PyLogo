


import sim_engine as se


class DrunkTurtle_Turtle(se.Turtle):

    def __init__(self):
        super().__init__()
        self.speed = 0


class DrunkTurtle_World(se.BasicWorld):

    def __init__(self):
        super().__init__()
        self.center_pixels = se.SimEngine.CENTER_PIXELS





    def step(self, event, values):
        for turtle in se.SimEngine.WORLD.turtles:
            turtle.fd(turtle.speed)
