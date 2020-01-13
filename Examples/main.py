from PyLogo.core.agent import Agent
from PyLogo.core.sim_engine import SimEngine
import PyLogo.core.utils as utils
from PyLogo.core.world_patch_block import Patch, World


def PyLogo(world_class=World, caption=None, gui_elements=None,
           agent_class=Agent, patch_class=Patch,
           patch_size=11, bounce=True):
    if gui_elements is None:
        gui_elements = []
    if caption is None:
        caption = utils.extract_class_name(world_class)
    sim_engine = SimEngine(gui_elements, caption=caption, patch_size=patch_size, bounce=bounce)
    sim_engine.start(world_class, patch_class, agent_class)
