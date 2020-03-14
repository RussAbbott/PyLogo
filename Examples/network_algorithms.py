
from copy import copy
from random import randint

from core.link import Link
from core.pairs import center_pixel
from core.sim_engine import SimEngine
from core.world_patch_block import World

# Import the string constants you will need (mainly keys but also values such as the graph types)
# as well as the classes and gui elements
from Examples.network_framework import CLUSTER_COEFF, LINK_PROB, PATH_LENGTH, TBD, \
                                       PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, STAR, WHEEL, \
                                       Network_Node, Network_World, network_left_upper, network_right_upper


class Network_Algorithms_Node(Network_Node):
    pass


class Network_Algorithms_World(Network_World):

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        return TBD

    def compute_metrics(self):
        clust_coeff = self.clustering_coefficient()
        SimEngine.gui_set(CLUSTER_COEFF, value=clust_coeff)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set(PATH_LENGTH, value=avg_path_length)

    @staticmethod
    def link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        Overriding this function in network_framework.
        """
        print("\n\nYour code goes here.")


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Network_Algorithms_World, 'Network test', gui_left_upper=network_left_upper,
           gui_right_upper=network_right_upper, agent_class=Network_Algorithms_Node, clear=True, bounce=True)
