import networkx as nx
import numpy as np

# --------------------
# Graph generators ---


def random_symmetric_graph(num_nodes, num_joints, num_colors, rewiring_p=0.4):
    """
    random_symmetric_graph(num_nodes, num_joints, num_colors, rewiring_p=0.4):
    makes a symmetric (newman-watts-strogatz) graph.

    Returns:
    nodes, node_centers (in [-1, 1] x [-1, 1]), node_colors, edges
    """

    # Make the first graph
    connected_graph = False
    while not connected_graph:
        g = nx.newman_watts_strogatz_graph(num_nodes, 3, rewiring_p)
        connected_graph = nx.is_connected(g)

    # Make a copy, which we will join to the first graph.
    g2 = g.copy()

    # Rename all vertices in the second graph except the joints
    mapping = dict()
    for i in range(num_joints, num_nodes):
        mapping[i] = (num_nodes + 1) + i
    nx.relabel_nodes(g2, mapping, copy=False)

    # Get the composition of the two graphs
    g = nx.compose(g, g2)

    # Force-directed graph layout
    g_layout = nx.spring_layout(g, k=5/np.sqrt(g.number_of_nodes()),
                                iterations=10000,
                                scale=1.0)

    node_centers = []
    for k, v in g_layout.items():
        node_centers.append((v[0], v[1]))

    # Choose node colors
    colors = np.array(
        [('red', 'blue', 'gray')[0:num_colors] for i in range(
            np.int(np.ceil(g.number_of_nodes() / num_colors)))]
    )
    colors = colors.flatten()
    color_choices = np.random.choice(colors, g.number_of_nodes(),
                                     replace=False)

    node_colors = []
    # Replace string with rgba value.
    for i in range(len(color_choices)):
        if color_choices[i] == 'red':
            node_colors.append((200, 50, 50, 255))
        elif color_choices[i] == 'blue':
            node_colors.append((50, 50, 200, 255))
        elif color_choices[i] == 'gray':
            node_colors.append((50, 50, 50, 255))

    return g.nodes(), node_centers, node_colors, g.edges()
