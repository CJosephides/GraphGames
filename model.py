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

    def __init__(self, x, y, c, shape=0):
        self.x = x
        self.y = y
        self.c = c
        self.shape = shape
        self.update_vertices()

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
