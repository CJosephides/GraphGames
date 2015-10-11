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
# TOKENS.append(Token(200, 200, COLOR_RED, shape=2))
# TOKENS.append(Token(100, 100, (200, 100, 100, 255), shape=1))

# Add some power units to the nodes.
GRAPH.nodes[0].add_token(Token(200, 200, COLOR_RED, shape=2))
GRAPH.nodes[0].add_token(Token(200, 200, COLOR_RED, shape=2))
GRAPH.nodes[0].add_token(Token(200, 200, COLOR_BLUE, shape=2))
GRAPH.nodes[0].add_token(Token(200, 200, COLOR_BLUE, shape=2))

# Add two 'flows'
GRAPH.nodes[1].add_token(Token(220, 220, COLOR_RED, shape=1, flow=True))
GRAPH.nodes[2].add_token(Token(220, 220, COLOR_BLUE, shape=1, flow=True))

ACTIVE_TOKEN = None

# --------------
# Controller ---


def get_clicked_token(mx, my, button, modifiers):
    # For each node
    for node in GRAPH.nodes.values():
        # For each token
        for token in node.tokens:
            if token.is_clicked(mx, my):
                return token

        # Check flow
        if isinstance(node.flow, Token):
            if node.flow.is_clicked(mx, my):
                return node.flow

    else:
        return None


def control_selection(clicked_token):
    global ACTIVE_TOKEN
    print("\nController: mouse pressed. ACTIVE_TOKEN = %s" % ACTIVE_TOKEN)

    if isinstance(clicked_token, Token):
        print("Controller: token %d clicked." % clicked_token.id)

        # Deselect previous active token, if any.
        if isinstance(ACTIVE_TOKEN, Token):
            print("Controller: deselecting token %d." % ACTIVE_TOKEN.id)
            ACTIVE_TOKEN.deselect()

        # Set clicked token as active, and select.
        ACTIVE_TOKEN = clicked_token
        print("Controller: selecting token %d." % ACTIVE_TOKEN.id)
        clicked_token.select()

    else:
        print('Controller: click received, nothing clicked.')
        # If no token has been clicked, deselect the current one (if any).
        if isinstance(ACTIVE_TOKEN, Token):
            print("Controller: attempting to deselect token %d." %
                  ACTIVE_TOKEN.id)
            ACTIVE_TOKEN.deselect()
            ACTIVE_TOKEN = None


def control_finish_drag():
    global ACTIVE_TOKEN

    # Check if the token was dragged to a new node.
    for node in GRAPH.nodes.values():
        if (ACTIVE_TOKEN.x - node.x)**2 + (ACTIVE_TOKEN.y - node.y)**2 \
           <= node.r**2:
            if node != ACTIVE_TOKEN.parent:
                # Assign token to this node and remove from previous node.
                ACTIVE_TOKEN.parent.remove_token(ACTIVE_TOKEN)
                node.add_token(ACTIVE_TOKEN)
                break
    else:
        # Otherwise, return to original node
        ACTIVE_TOKEN.parent.update_tokens()

# ------------------------------
# Window events (interface?) ---


@window.event
def on_draw():
    window.clear()

    # Draw the graph (edges, nodes, tokens, flows)
    GRAPH.draw()


@window.event
def on_mouse_press(mx, my, button, modifiers):

    global ACTIVE_TOKEN
    print("\nController: mouse pressed. ACTIVE_TOKEN = %s" % ACTIVE_TOKEN)

    # Clicking selects/deselects tokens.
    clicked_token = get_clicked_token(mx, my, button, modifiers)
    control_selection(clicked_token)


@window.event
def on_mouse_drag(mx, my, dx, dy, buttons, modifiers):
    global ACTIVE_TOKEN
    if isinstance(ACTIVE_TOKEN, Token):
        ACTIVE_TOKEN.update_center(mx, my)


@window.event
def on_mouse_release(mx, my, button, modifiers):
    global ACTIVE_TOKEN
    if isinstance(ACTIVE_TOKEN, Token):
        control_finish_drag()

pyglet.app.run()
