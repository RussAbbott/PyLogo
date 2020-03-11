from core.link import Link
from core.pairs import center_pixel

from Examples.network_framework import Network_Node, Network_World, network_left_upper, network_right_upper


class Network_Algorithms_Node(Network_Node):
    pass


class Network_Algorithms_World(Network_World):

    @staticmethod
    def generate_graph(graph_type, ring_node_list):

        print("\n\nYour code goes here.")
        pass


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Network_Algorithms_World, 'Network test', gui_left_upper=network_left_upper,
           gui_right_upper=network_right_upper, agent_class=Network_Algorithms_Node,  bounce=True)
