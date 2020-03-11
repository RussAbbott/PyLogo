from core.link import Link
from core.pairs import center_pixel
from Examples.forces_and_effects import Force_Layout_Node, Force_Layout_World, force_left_upper, force_right_upper


class Network_Node(Force_Layout_Node):
    pass


class Network_World(Force_Layout_World):

    @staticmethod
    def generate_graph(graph_type, ring_node_list):

        print("\n\nYou're code goes here.")
        pass


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Network_World, 'Force test', gui_left_upper=force_left_upper, gui_right_upper=force_right_upper,
           agent_class=Network_Node,  bounce=True)
