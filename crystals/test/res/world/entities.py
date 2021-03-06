from functools import partial

from crystals.world import Entity
from actions import *


# Define the player entity
PLAYER = partial(Entity, 'player', False, 'human-peasant.png')


# Define some template entities
class Rfloor(Entity):

    def __init__(self, imgend, action=[]):
        Entity.__init__(
            self, 'rough surface', True, 'floor-a-' + imgend, action=action)

class Sfloor(Entity):

    def __init__(self, imgend, action=[]):
        Entity.__init__(
            self, 'smooth surface', True, 'floor-b-' + imgend, action=action)

class Vwall(Entity):

    def __init__(self, imgend, action=[]):
        Entity.__init__(
            self, 'wall', False, 'wall-vert-' + imgend, action=action)

class Hwall(Entity):

    def __init__(self, imgend, action=[]):
        Entity.__init__(
            self, 'wall', False, 'wall-horiz-' + imgend, action=action)


# Define entities for each room
# ----------------------------------------------------------------------
class RedRoom:

    rfloor = partial(Rfloor, 'red.png')
    sfloor = partial(Sfloor, 'red.png')
    vwall = partial(Vwall, 'blue.png')
    hwall = partial(Hwall, 'blue.png')

    troll = partial(Entity,
        id='troll',
        name='troll',
        walkable=False,
        image='troll.png',
        action=troll_action)

class BlueRoom:

    sfloor = partial(Entity, 'smooth surface', True, 'tree-dead.png')
    vwall = partial(Vwall, 'blue.png')
    hwall = partial(Hwall, 'blue.png')
