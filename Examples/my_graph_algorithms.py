from random import randint

from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, LINK_PROB, PATH_LENGTH, RANDOM, RING,
                                  TBD, WHEEL, graph_left_upper, graph_right_upper)
from core.gui import STAR
from core.link import Link
from core.pairs import center_pixel
from core.sim_engine import SimEngine


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

    @staticmethod
    def build_ring_star_or_wheel_graph(graph_type, ring_node_list):
        # Create a center_node variable if a STAR and WHEEL graph.
        center_node = None
        if graph_type in [STAR, WHEEL]:
            center_node = Graph_Node()
            center_node.move_to_xy(center_pixel())

        # If ring_node_list is empty, do nothing more.
        if not ring_node_list:
            return

        # If ring_node_list contains exactly one node and the graph type is STAR or WHEEL,
        # link the center node to the one ring node and return.
        if len(ring_node_list) == 1:
            if graph_type in [STAR, WHEEL]:
                Link(center_node, ring_node_list[0])
            return

        # Otherwise (2 or more ring nodes), create the outer ring and spokes as appropriate.
        for (node_a, node_b) in zip(ring_node_list, ring_node_list[1:] + [ring_node_list[0]]):
            if graph_type in [RING, WHEEL]:
                Link(node_a, node_b)

            if graph_type in [STAR, WHEEL]:
                Link(center_node, node_a)

        # Complete the ring if a ring or wheel graph
        if graph_type in [RING, WHEEL]:
            Link(ring_node_list[-1], ring_node_list[0])

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        return TBD

    def compute_metrics(self):
        cluster_coefficient = self.clustering_coefficient()
        SimEngine.gui_set(CLUSTER_COEFF, value=cluster_coefficient)
        avg_path_length = self.average_path_length()
        SimEngine.gui_set(PATH_LENGTH, value=avg_path_length)

    @staticmethod
    def link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested.
                       (Will be > 0 or this method won't be called.)
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        Overrides this function in network_framework.
        """
        # Treat random graphs as a separate case.
        if graph_type == RANDOM:
            link_prob = SimEngine.gui_get(LINK_PROB)
            # A generator for the links
            link_generator = (Link(ring_node_list[i], ring_node_list[j]) for i in range(nbr_nodes - 1)
                                                                         for j in range(i + 1, nbr_nodes)
                                                                         if randint(1, 100) <= link_prob)
            # Run the generator to generate the links
            for _ in link_generator:
                pass
            return

        if graph_type in [RING, STAR, WHEEL]:
            Graph_Algorithms_World.build_ring_star_or_wheel_graph(graph_type, ring_node_list)

        # Preferential attachment and small worlds are TBD.


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node, clear=True, bounce=True, auto_setup=True)
