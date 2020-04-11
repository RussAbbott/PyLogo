# Import the string constants you need (mainly keys) as well as classes and gui elements
import math
from random import sample

from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                  graph_right_upper)

from core.world_patch_block import World
from core.sim_engine import SimEngine
from core.link import Link, link_exists
from random import choice, randint, sample, uniform, random


class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        nbr_nodes = len(World.agents)
        dist_mat = [[100 for r in range(nbr_nodes)] for c in range(nbr_nodes)]
        # create the zero diagonal
        for x in range(nbr_nodes):
            dist_mat[x][x] = 0

        # Set each link to 1 in corresponding position in matrix, row and col are to keep position
        row = 0
        for node1 in World.agents:
            col = 0
            for node2 in World.agents:
                if node2 is not node1:
                    if link_exists(node1, node2):
                        dist_mat[row][col] = 1
                col = col + 1
            row = row + 1

        # Main loop
        for k in range(nbr_nodes):
            for i in range(nbr_nodes):
                for j in range(nbr_nodes):
                    if dist_mat[i][j] > dist_mat[i][k] + dist_mat[k][j]:
                        dist_mat[i][j] = dist_mat[i][k] + dist_mat[k][j]

        # print the matrix to console
        for row in dist_mat:
            print(row)
        print("\n\n")

        # keep track of the 100s so they can be left out of average calculation
        hundred_count = sum(x.count(100) for x in dist_mat)
        print(hundred_count)

        # calculate the average of the elements in the matrix
        mat_sum = sum(map(sum, dist_mat)) - hundred_count*100
        div_coef = ((nbr_nodes*nbr_nodes)-(nbr_nodes+hundred_count))
        if div_coef == 0:
            return "NA"
        dist_avg = mat_sum/div_coef
        return dist_avg

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        nbr_nodes = SimEngine.gui_get("nbr_nodes")
        clusters = []
        for agent in World.agents:
            connections = agent.lnk_nbrs()
            agent_cluster = []
            checked_nodes = []
            # calculate the number of links between neighbors of the agent
            for lnk, child_node1 in connections:
                neighbor_links = 0
                for link, child_node2 in connections:
                    if child_node1 is not child_node2:
                        if link_exists(child_node1, child_node2) and child_node2 not in checked_nodes:
                            neighbor_links = neighbor_links + 1
                            checked_nodes.append(child_node1)
                agent_cluster.append(neighbor_links)
            if len(connections) > 1:
                agent_cluster_coef = (2 * sum(agent_cluster)) / (len(connections) * (len(connections) - 1))
            else:
                agent_cluster_coef = 0
            print(f"Agent Id: {agent.id}, clustering coefficient: {agent_cluster_coef}")
            clusters.append(agent_cluster_coef)
        cluster_coefficient = sum(clusters) / nbr_nodes
        print("\n")
        return cluster_coefficient

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

        if graph_type == "ring":
            # need list to check whether or not a node has been connected
            checked_nodes = []

            # main loop, links each node to the first at it's right (iteratively).
            for root in ring_node_list:
                for node in ring_node_list:
                    if root is not node and node not in checked_nodes:
                        Link(root, node)
                        checked_nodes.append(root)
                        break

        if graph_type == "wheel":
            # need list to check whether or not a node has been connected
            checked_nodes = []

            # main loop, links each node to the first at it's right (iteratively).
            for root in ring_node_list:
                for node in ring_node_list:
                    if root is not node and node not in checked_nodes:
                        Link(root, node)
                        checked_nodes.append(root)
                        break

        if graph_type == "random":
            link_coef = SimEngine.gui_get('link_prob') / 100
            for node in ring_node_list:
                for agent in ring_node_list:
                    if random() < link_coef \
                            and not link_exists(node, agent)\
                            and agent is not node:
                        Link(node, agent)

        if graph_type == "pref attachment":
            old_nodes = [ring_node_list[0], ring_node_list[1]]
            Link(ring_node_list[0], ring_node_list[1])
            for node in ring_node_list[2:]:
                Link(node, choice(old_nodes))
                old_nodes.append(node)

        if graph_type == "small world":
            # beta = SimEngine.gui_get('link_prob') / 100
            n_size = SimEngine.gui_get('n_size')
            # if the neighborhood size is too large, lower it to the first available size
            if n_size >= (nbr_nodes/2-1):
                n_size = int(math.ceil(nbr_nodes/2)-2)
                print(f"NEIGHBORHOOD TOO LARGE, LOWERING NEIGHBORHOOD SIZE TO {n_size}\n")

            # main loop, links each node to the first at it's right (iteratively).
            for i in range(nbr_nodes):
                for j in range(n_size):
                    next_ind = i+j+1
                    if next_ind >= nbr_nodes:
                        next_ind = next_ind - nbr_nodes
                    Link(ring_node_list[i], ring_node_list[next_ind])

            # new chance for each link
            new_chance = SimEngine.gui_get("link_prob")/100.0
            past_links = []
            # deep copy links
            for l in World.links:
                past_links.append(l)
            for l in past_links:
                # generate random # to see if it gets rewired
                if random() < new_chance:
                    # pick the first node in the link
                    # find all neighbors & consider self a neighbor
                    neighbors = [l.agent_1]
                    for n_link in l.agent_1.all_links():
                        neighbors.append(n_link.other_side(l.agent_1))

                    # check to see if there exits any agent not considered a neighbor
                    if len(neighbors) < len(World.agents):
                        new_neighbor = choice(list(World.agents - set(neighbors)))
                        # remove the current link
                        World.links.remove(l)
                        # create the new link and add it to the list of links to ignore
                        Link(l.agent_1, new_neighbor)



if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=False)