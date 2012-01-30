"""creation and mutation of the game world"""
from pyglet.graphics import OrderedGroup

import action

__all__ = ['Room', 'World', 'action']

TILE_SIZE = 24 # Width and height of each tile, in pixels
ORIGIN_X = 10  # X and Y coordinates of the bottom left corner
ORIGIN_Y = 124 # of room display, in pixels


class WorldError(Exception):
    pass


class Room(list):

    def __init__(self, name, batch, layers):
        super(Room, self).__init__(layers)
        self.name = name
        self.batch = batch
        self.groups = [OrderedGroup(z) for z in range(len(self))]

    def _update_entity(self, entity, x, y, z):
        entity.batch = self.batch
        entity.group = self.groups[z]
        newx = x * TILE_SIZE + ORIGIN_X
        newy = y * TILE_SIZE + ORIGIN_Y
        entity.set_position(newx, newy)

    def iswalkable(self, x, y):
        """Return True if, for every layer, (x, y) is in bounds and is
        either None or a walkable entity, else return False.
        """
        if (x < 0 or x >= len(self[0][0])) or (y < 0 or y >= len(self[0])):
            return False
        for layer in self:
            e = layer[y][x]
            if e != None and not e.walkable:
                return False
        return True

    def focus(self):
        """Focus the room, preparing it for rendering."""
        for z in range(len(self)):
            for y in range(len(self[z])):
                for x in range(len(self[z][y])):
                    entity = self[z][y][x]
                    if entity is not None:
                        self._update_entity(entity, x, y, z)

    def get_coords(self, entity):
        """Return x, y, and z coordinates of the given entity in the room."""
        x = (entity.x - ORIGIN_X) / TILE_SIZE
        y = (entity.y - ORIGIN_Y) / TILE_SIZE
        if entity.group is None:
            z = None
        else:
            z = entity.group.order
        return x, y, z

    def add_layer(self, z=None):
        """If z is None or too large, append a blank layer at the top.
        If z is an integer, insert a blank layer at z. 
        """
        layer = [[None for x in range(len(self[0][0]))]
                 for y in range(len(self[0]))]
        if z is None or z >= len(self):
            self.append(layer)
            self.groups.append(OrderedGroup(len(self.groups)))
        else:
            self.insert(z, layer)
            self.groups.insert(z, OrderedGroup(z))
            for group in self.groups[z + 1:]:
                group.order += 1

    def replace_entity(self, entity, x, y, z):
        """Place 'entity' at (x, y, z), replacing an existing entity if
        neccesary.
        """
        self[z][y][x] = entity
        self._update_entity(entity, x, y, z)

    def add_entity(self, entity, x, y, z):
        """Attempt to place 'entity' at (x, y, z), but raise a
        WorldError if an entity already exists there.
        """
        if self[z][y][x] is not None:
            raise WorldError(
                'Entity already exists in room {}[{}][{}][{}]'.format(
                self.name, z, y, x))
        self.replace_entity(entity, x, y, z)


class Portal(object):
    """A two-way portal between two rooms."""

    def __init__(self, x, y, from_room, to_room):
        self.x = x
        self.y = y
        self.from_room = from_room
        self.to_room = to_room


class World(dict):
    """A collection of rooms linked by portals."""

    def __init__(self, rooms, portals, current_room):
        dict.__init__(self, rooms)
        self.portals = portals
        self.focus = None
        self.set_focus(current_room)

    def set_focus(self, room_name):
        self.focus = self[room_name]
        self.focus.focus()

    def get_portal(self, x, y, room=None):
        """If a portal exists at (x, y) in the given room, return that
        portal. Else, return None.

        If room is None, use the focused room.
        """
        if room is None:
            room = self.focus
        for portal in self.portals:
            if portal.from_room is room and portal.x is x and portal.y is y:
                return portal
        return None
    
    def add_entity(self, entity, x, y, z=None, room=None):
        """Add the given entity to the given room at (x, y, z).
        
        If z is None, or out of range, add a layer to the top and put the
        entity there. Otherwise, if no entity exists at [z][y][x],
        place it there, else insert a new layer at z + 1 and place it there.

        If room is None, add the entity to the focused room.
        """
        if room is None:
            room = self.focus
        if z is None or z >= len(room):
            z = -1
            room.add_layer()
            room.replace_entity(entity, x, y, -1)
            return
        try:
            room.add_entity(entity, x, y, z)
        except WorldError:
            z += 1
            room.add_layer(z)
            room.replace_entity(entity, x, y, z)

    def pop_entity(self, x, y, z, room=None):
        if room is None:
            room = self.focus
        entity = room[z][y][x]
        room[z][y][x] = None
        return entity
    
    def step_entity(self, entity, xstep, ystep):
        """Move entity from its current position by (xstep, ystep),
        changing the position of the entity to reflect the direction of
        the attempted move. 
        
        Return True if the move was successful, else False.
        """
        entity.pos = (xstep / abs(xstep) if xstep else 0,
                      ystep / abs(ystep) if ystep else 0)

        x, y, z = self.focus.get_coords(entity)
        newx = x + xstep
        newy = y + ystep
        if not self.focus.iswalkable(newx, newy):
            return False

        self.pop_entity(x, y, z)
        self.add_entity(entity, newx, newy, z)
        return True

    def portal_entity(self, entity, portal):
        """Transfer entity from its current room to the portal's
        destination.
        """
        x, y, z = self.focus.get_coords(entity)
        self.pop_entity(x, y, z)

        for portal1 in self.portals:
            if portal1.from_room == portal.to_room:
                x = portal1.x
                y = portal1.y
        self.add_entity(entity, x, y, z, portal.to_room)