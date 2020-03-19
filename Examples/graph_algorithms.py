# Import the string constants you need (mainly keys) as well as classes and gui elements
# Import the string constants you need (mainly keys) as well as classes and gui elements
from Examples.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                      graph_right_upper)
from core.sim_engine import SimEngine


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

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

        Overrides this function from graph_framework.
        """
        print("\n\nYour code goes here.")


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=True)
