import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
from model import *


# ---------
# Setup ---

window = pyglet.window.Window()

glEnable(GL_BLEND)
glEnable(GL_LINE_SMOOTH)
glEnable(GL_POINT_SMOOTH)
glLineWidth(5)
glClearColor(200, 200, 200, 255)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


# -----------
# Objects ---

NODES = []
NODES.append(GraphNode(200, 200, 50, (200, 50, 50, 255)))

TOKENS = []
TOKENS.append(Token(200, 200, (50, 50, 200, 255), shape=1))


# -----------------
# Window events ---


@window.event
def on_draw():
    window.clear()

    for node in NODES:
        node.draw()

    for token in TOKENS:
        token.draw()

pyglet.app.run()
