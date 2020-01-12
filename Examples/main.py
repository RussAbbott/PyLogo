from PyLogo.core.agent import Turtle
from PyLogo.core.core_elements import Patch, World
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils


def PyLogo(world_class=World, gui_elements=None, caption=None,
           patch_class=Patch, turtle_class=Turtle,
           patch_size=11, bounce=True):
    if gui_elements is None:
        gui_elements = []
    if caption is None:
        caption = utils.extract_class_name(world_class)
    sim_engine = SimEngine(gui_elements, caption=caption, patch_size=patch_size, bounce=bounce)
    sim_engine.start(world_class, patch_class, turtle_class)
