import numpy as np
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
from model import *
from generators import random_symmetric_graph
from config import *


# ---------
# Setup ---

window = pyglet.window.Window(WINDOW_X, WINDOW_Y)

glEnable(GL_BLEND)
glEnable(GL_LINE_SMOOTH)
glEnable(GL_POINT_SMOOTH)
glLineWidth(2)
glClearColor(200, 200, 200, 255)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


# -----------
# Objects ---

GRAPH = Graph(*random_symmetric_graph(10, 2, 3, rewiring_p=0.5), window=window)

NODES = []
# NODES.append(GraphNode(200, 200, 50, (200, 50, 50, 255)))

TOKENS = []
TOKENS.append(Token(200, 200, COLOR_RED, shape=2))
TOKENS.append(Token(100, 100, (200, 100, 100, 255), shape=1))

ACTIVE_TOKEN = None

# ------------------------------
# Window events (controller) ---


@window.event
def on_draw():
    window.clear()

    # Draw the graph (edges, nodes)
    GRAPH.draw()

    # Overlay tokens.
    for token in TOKENS:
        token.draw()


@window.event
def on_mouse_press(mx, my, button, modifiers):
    # Clicking selects/deselects tokens.
    global ACTIVE_TOKEN
    print("\nController: mouse pressed. ACTIVE_TOKEN = %s" % ACTIVE_TOKEN)
    for token in TOKENS:
        if token.is_clicked(mx, my):
            print("Controller: token %d clicked." % token.id)
            # Deselect previous active token, if any.
            if isinstance(ACTIVE_TOKEN, Token):
                print("Controller: deselecting token %d." % ACTIVE_TOKEN.id)
                ACTIVE_TOKEN.deselect()
            # Set clicked token as active, and select.
            ACTIVE_TOKEN = token
            print("Controller: selecting token %d." % ACTIVE_TOKEN.id)
            token.select()
            break
    else:
        print('Controller: click received, nothing clicked.')
        # If no token has been clicked, deselect the current one (if any).
        if isinstance(ACTIVE_TOKEN, Token):
            print("Controller: attempting to deselect token %d." %
                  ACTIVE_TOKEN.id)
            ACTIVE_TOKEN.deselect()
            ACTIVE_TOKEN = None


@window.event
def on_mouse_drag(mx, my, dx, dy, buttons, modifiers):
    global ACTIVE_TOKEN
    if isinstance(ACTIVE_TOKEN, Token):
        ACTIVE_TOKEN.update_center(mx, my)

pyglet.app.run()
