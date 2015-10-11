"""
Graph games prototype.
"""

import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
from config import *

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
    scale = TOKEN_SIZE 

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

        elif self.shape == 2:
            # Circle
            self.vertices = pyglet.graphics.vertex_list(
                100 + 2,
                ('v2f', get_circle_vertices(self.x, self.y, TOKEN_SIZE, 100)),
                ('c4B', self.c + (self.c * 101)))

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
            self.c = (min(255, self.c[0] + 25),
                      min(255, self.c[1] + 25),
                      min(255, self.c[2] + 25),
                      self.c[3])
            self.update_vertices()

    def deselect(self):
        if self.selected:
            self.selected = False
            print('Token %d: selected = %s.' % (self.id, self.selected))
            # Slightly change color and update vertices.
            self.c = (self.c[0] - 25,
                      self.c[1] - 25,
                      self.c[2] - 25,
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

        self.tokens = []

    def update_vertices(self):
        """
        Update the vertices for this node.
        """
        self.vertices = pyglet.graphics.vertex_list(
            GraphNode.num_vertices + 2,
            ('v2f', get_circle_vertices(self.x,
                                        self.y,
                                        self.r - NODE_THICKNESS,
                                        GraphNode.num_vertices)),
            ('c4B', (220, 220, 220, 255) * (GraphNode.num_vertices + 2)))

        self.vertices_outline = pyglet.graphics.vertex_list(
            GraphNode.num_vertices + 2,
            ('v2f', get_circle_vertices(self.x, self.y, self.r,
                                        GraphNode.num_vertices)),
            ('c4B', self.c * (GraphNode.num_vertices + 2)))

    # # ----------
    # # Tokens ---

    def add_token(self, token):
        self.tokens.append(token)
        self.update_tokens()

    def update_tokens(self):
        c = 0
        for token in self.tokens:
            token.x = self.x + (0.75*self.r) * np.sin(c*2*np.pi /
                                                     len(self.tokens))
            token.y = self.y + (0.75*self.r) * np.cos(c*2*np.pi /
                                                     len(self.tokens))
            token.update_vertices()
            c += 1

    def remove_token(self, token):
        self.tokens.remove(token)
        self.update_tokens()

    def draw(self):
        """
        OpenGL draws self.
        """
        # Stroke
        self.vertices_outline.draw(GL_TRIANGLE_FAN)
        # Fill
        self.vertices.draw(GL_TRIANGLE_FAN)
        # Tokens
        for token in self.tokens:
            token.draw()


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
        for center in self.node_centers:
            # WARNING: Some networkx implementations fail to respect the
            # graph_layout scaling requirement. The code below works only for
            # those cases where the scaling is correct!

            # x = ws[0]*(0.5*(center[0] + 1))
            # y = ws[1]*(0.5*(center[1] + 1))
            x = ws[0]*center[0]
            y = ws[1]*center[1]

            x = BORDER + (x/ws[0]) * (ws[0] - 2*BORDER)
            y = BORDER + (y/ws[1]) * (ws[1] - 2*BORDER)

            self.node_positions.append((x, y))

    def make_nodes(self):
        self.nodes = dict()
        for n in range(len(self.node_ids)):
            self.nodes[self.node_ids[n]] = \
                GraphNode(self.node_positions[n][0],
                          self.node_positions[n][1],
                          NODE_RADIUS,
                          self.node_colors[n]
                          )

    def update_edges(self):
        """
        Makes list of vertices for the edges.
        """
        edge_vertices = []
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
        glLineWidth(1)
        self.edge_vertices.draw(GL_LINE_STRIP)
        # Then draw vertices.
        for node in self.nodes.values():
            node.draw()
