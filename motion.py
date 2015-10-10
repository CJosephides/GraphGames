"""
Test moving objects in openGL.
"""

import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import mouse

window = pyglet.window.Window()

# ## Utility functions

# ## Classes
def calc_circle_vertices(x, y, r, n):

    vertices = [x, y]
    for i in range(n+1):
        theta = i*(2*np.pi/n)
        vertices.append(x + (r * np.cos(theta)))
        vertices.append(y + (r * np.sin(theta)))

    return vertices


class Node:

    num_verts = 100
    id = 0

    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.r = r
        self.c = c + (c * (Node.num_verts + 1))

        self.verts = ()
        self.update_verts()

        self.id = Node.id
        Node.id += 1

    def update_center(self, newx, newy):
        self.x = newx
        self.y = newy
        self.update_verts()

    def update_verts(self):
        self.verts = pyglet.graphics.vertex_list(Node.num_verts + 2,
        ('v2f', calc_circle_vertices(self.x, self.y, self.r,Node.num_verts)),
        ('c4B', self.c))

    def draw(self):
        self.verts.draw(GL_TRIANGLE_FAN)


    def is_clicked(self, mx, my):
        if (((my - self.y)**2) + ((mx - self.x)**2))**(0.5) <= self.r:
            return True
        else:
            return False


# ## Setup
glEnable(GL_BLEND)
glEnable(GL_LINE_SMOOTH)
glEnable(GL_POINT_SMOOTH)
glLineWidth(5)
glClearColor(200, 200, 200, 255)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


# ## Instantiate objects
NODES = []
for i in range(4):
    NODES.append(Node(np.random.randint(50, 400),
                 np.random.randint(50, 400),
                 np.random.randint(25, 50),
                 tuple(np.random.randint(0, 255, 3)) + (255,)))

ACTIVE_NODE = None

@window.event
def on_draw():
    window.clear()

    # Draw edges to connect all nodes
    for node_source in NODES:
        for node_target in NODES:
            if node_source == node_target:
                continue
            pyglet.graphics.draw(2, GL_LINE_STRIP,
                                 ('v2f', (node_source.x, node_source.y,
                                  node_target.x, node_target.y)),
                                 ('c4B', (50, 50, 50, 255) * 2))

    # Render nodes
    for node in NODES:
        node.draw()

@window.event
def on_mouse_press(mx, my, button, modifiers):
    global ACTIVE_NODE
    for node in NODES:
        if node.is_clicked(mx, my):
            ACTIVE_NODE = node
            break

@window.event
def on_mouse_release(mx, my, button, modifiers):
    global ACTIVE_NODE
    if isinstance(ACTIVE_NODE, Node):
        ACTIVE_NODE.update_center(mx, my)
        ACTIVE_NODE = None

@window.event
def on_mouse_drag(mx, my, dx, dy, buttons, modifiers):
    global ACTIVE_NODE
    if isinstance(ACTIVE_NODE, Node):
        ACTIVE_NODE.update_center(mx, my)

pyglet.app.run()
