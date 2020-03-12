
from copy import copy
from random import randint

from core.link import Link
from core.pairs import center_pixel
from core.sim_engine import SimEngine
from core.world_patch_block import World

from Examples.network_framework import Network_Node, Network_World, network_left_upper, network_right_upper


class Network_Algorithms_Node(Network_Node):
    pass


class Network_Algorithms_World(Network_World):

    def __init__(self, *args):
        super().__init__(*args)
        self.node_cache = set()
        self.link_cache = set()

    @staticmethod
    def create_random_links(node_list, link_prob):
        nbr_nodes = len(node_list)
        for i in range(nbr_nodes - 1):
            for j in range(i+1, nbr_nodes):
                if randint(1, 100) <= link_prob:
                    Link(node_list[i], node_list[j])

    @staticmethod
    def generate_graph(graph_type, ring_node_list):

        # Create the variable center_node. The graph generating algorithms for 'star' and 'wheel' need it.
        center_node = None
        if graph_type in ['star', 'wheel']:
            center_node = Network_Algorithms_Node()
            center_node.move_to_xy(center_pixel())

        for (node_a, node_b) in zip(ring_node_list, ring_node_list[1:] + [ring_node_list[0]]):
            if graph_type in ['ring', 'wheel']:
                Link(node_a, node_b)

            if graph_type in ['star', 'wheel']:
                Link(center_node, node_a)

        # Complete the ring if a ring or wheel graph
        if graph_type in ['ring', 'wheel']:
            Link(ring_node_list[-1], ring_node_list[0])

        # Treat random graphs as its own case.
        if graph_type == 'random':
            link_prob = SimEngine.gui_get('link_prob')
            Network_Algorithms_World.create_random_links(ring_node_list, link_prob)


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Network_Algorithms_World, 'Network test', gui_left_upper=network_left_upper,
           gui_right_upper=network_right_upper, agent_class=Network_Algorithms_Node, bounce=True)
