"""
Graph games prototype.
"""

import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import mouse

# ---------------------
# Utility functions ---


def get_circle_vertices(x, y, r, n):
    """
    Return list of (n) vertices comprising a circle with center (x, y) and
    radius r.
    """

    vertices = [x, y]
    for i in range(n + 1):
        theta = i*(2*np.pi/n)
        vertices.append(x + (r * np.cos(theta)))
        vertices.append(y + (r * np.sin(theta)))

    return vertices

# -----------
# Classes ---


class Token:
    """
    A generic game token. Can be one of several pre-set shapes.
    """

    id = 0
    scale = 25

    def __init__(self, x, y, c, shape=1):
        self.x = x
        self.y = y
        self.c = c
        self.shape = shape
        self.update_vertices()
        self.selected = False

        self.id = Token.id
        Token.id += 1

    def update_vertices(self):
        """
        Recalculates vertices.
        """
        if self.shape == 0:
            # Triangle
            self.vertices = pyglet.graphics.vertex_list(
                3, ('v2f', [self.x - 1*Token.scale, self.y - 1*Token.scale,
                            self.x, self.y + 1*Token.scale,
                            self.x + 1*Token.scale, self.y - 1*Token.scale]),
                ('c4B', self.c * 3))

        elif self.shape == 1:
            # Rhombus
            self.vertices = pyglet.graphics.vertex_list(
                4, ('v2f', [self.x - 1*Token.scale, self.y,
                            self.x, self.y + 1*Token.scale,
                            self.x + 1*Token.scale, self.y,
                            self.x, self.y - 1*Token.scale]),
                ('c4B', self.c * 4))

    def is_clicked(self, mx, my):
        """
        is_clicked(mx, my): determine if the object has been clicked.
        """

        # We will use a circular bounding box.
        if (((my - self.y)**2) + ((mx - self.x)**2))**(0.5) <= Token.scale:
            print("Token %d: clicked." % self.id)
            return True
        else:
            return False

    def select(self):
        if not self.selected:
            self.selected = True
            print('Token %d: selected = %s.' % (self.id, self.selected))
            # Slightly change color and update vertices.
            self.c = (self.c[0] + 25, self.c[1] + 25, self.c[2] + 25,
                      self.c[3])
            self.update_vertices()

    def deselect(self):
        if self.selected:
            self.selected = False
            print('Token %d: selected = %s.' % (self.id, self.selected))
            # Slightly change color and update vertices.
            self.c = (self.c[0] - 25, self.c[1] - 25, self.c[2] - 25,
                      self.c[3])
            self.update_vertices()

    def update_center(self, x, y):
        """
        update_center(x, y): set new center and recalculate vertices.
        """
        self.x = x
        self.y = y
        self.update_vertices()

    def draw(self):
        """
        Draws self.
        """
        self.vertices.draw(GL_TRIANGLE_FAN)


class GraphNode:
    """
    GraphNode(x, y, r, c). Represents a graph node (vertex).
    """

    num_vertices = 100
    id = 0

    def __init__(self, x, y, r, c):
        """
        x: x-center
        y: y-center
        r: radius (pixels)
        c: color
        """
        self.x = x
        self.y = y
        self.r = r
        self.c = c
        self.update_vertices()

        self.id = GraphNode.id
        GraphNode.id += 1

    def update_vertices(self):
        """
        Update the vertices for this node.
        """
        self.vertices = pyglet.graphics.vertex_list(
            GraphNode.num_vertices + 2,
            ('v2f', get_circle_vertices(self.x, self.y, self.r,
                                        GraphNode.num_vertices)),
            ('c4B', self.c + (self.c * (GraphNode.num_vertices + 1))))

    def draw(self):
        """
        OpenGL draws self.
        """
        self.vertices.draw(GL_TRIANGLE_FAN)


class Graph:
    """
    A collection of nodes and edges.
    """

    def __init__(self, node_ids, node_centers, node_colors, edges, window):
        self.window = window
        self.node_ids = node_ids
        self.node_centers = node_centers  # relative positions in [-1,1]x[-1,1]
        self.update_node_positions()  # get window-relative node positions
        self.node_colors = node_colors
        self.make_nodes()
        self.edges = edges
        self.update_edges()

    def update_node_positions(self):
        """
        Updates node centers relative to the window.
        """
        ws = self.window.get_size()
        self.node_positions = []
        # TODO: Need bounding box.
        BORDER = 100
        for center in self.node_centers:
            x = ws[0]*(0.5*(center[0] + 1))
            y = ws[1]*(0.5*(center[1] + 1))

            x = BORDER + (x/ws[0]) * (ws[0] - 2*BORDER)
            y = BORDER + (y/ws[1]) * (ws[1] - 2*BORDER)

            self.node_positions.append((x, y))

    def make_nodes(self):
        self.nodes = dict()
        # TODO: Correct node naming!
        for n in range(len(self.node_ids)):
            self.nodes[self.node_ids[n]] = \
                GraphNode(self.node_positions[n][0],
                          self.node_positions[n][1],
                          25,
                          self.node_colors[n]
                          )

    def update_edges(self):
        """
        Makes list of vertices for the edges.
        """
        edge_vertices = []
        # TODO: Correct node naming!
        for i in range(len(self.edges)):
            start_node = self.nodes[self.edges[i][0]]
            end_node = self.nodes[self.edges[i][1]]
            start_position = (start_node.x,
                              start_node.y)
            end_position = (end_node.x,
                            end_node.y)
            edge_vertices.append(start_position[0])
            edge_vertices.append(start_position[1])
            edge_vertices.append(end_position[0])
            edge_vertices.append(end_position[1])

        self.edge_vertices = pyglet.graphics.vertex_list(
            int(len(edge_vertices) / 2),
            ('v2f', edge_vertices),
            ('c4B', (0, 0, 0, 255) * int(len(edge_vertices) / 2))
            )

    def draw(self):
        # Draw edges first.
        self.edge_vertices.draw(GL_LINE_STRIP)
        # Then draw vertices.
        for node in self.nodes.values():
            node.draw()
