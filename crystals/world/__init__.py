"""creation and mutation of the game world"""
from pyglet.graphics import OrderedGroup

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

    def _iter_entities(self, startz=0, endz=None):
        """Iterate over each entity in the room from z-levels `startz`
        to `endz`, yielding the next entity and its x, y, and z
        coordinates in the room each iteration.
        """
        if not endz:
            endz = len(self)
        for z in range(startz, endz):
            for y in range(len(self[z])):
                for x in range(len(self[z][y])):
                    entity = self[z][y][x]
                    if entity is not None:
                        yield entity, x, y, z

    def _update_group_order(self, entity, z):
        """Update the entity's OrderedGroup to match `z`."""
        entity.group = OrderedGroup(z)

    def _update_entity(self, entity, x, y, z):
        """Update the entity's position to reflect (x, y, z). Must only
        be called after at least one call to _focus_entity.
        """
        newx = x * TILE_SIZE + ORIGIN_X
        newy = y * TILE_SIZE + ORIGIN_Y
        entity.set_position(newx, newy)
        self._update_group_order(entity, z)

    def _focus_entity(self, entity, x, y, z):
        entity.batch = self.batch
        self._update_entity(entity, x, y, z)

    def focus(self):
        """Focus the room, preparing it for rendering."""
        for entity, x, y, z in self._iter_entities(): 
            self._focus_entity(entity, x, y, z)

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
        else:
            self.insert(z, layer)
            for entity, x, y, z in self._iter_entities(z + 1):
                self._update_group_order(entity, z)

    def replace_entity(self, entity, x, y, z):
        """Place 'entity' at (x, y, z), replacing an existing entity if
        neccesary.
        """
        self[z][y][x] = entity
        self._focus_entity(entity, x, y, z)

    def add_entity(self, entity, x, y, z):
        """Attempt to place 'entity' at (x, y, z), but raise a
        WorldError if an entity already exists there.
        """
        if self[z][y][x] is not None:
            raise WorldError(
                'Entity already exists in room {}[{}][{}][{}]'.format(
                self.name, z, y, x))
        self.replace_entity(entity, x, y, z)


class World(dict):
    """A collection of rooms linked by portals."""

    def __init__(self, rooms, portals, start):
        dict.__init__(self, rooms)
        self.portals = portals
        self.focus = None
        self.set_focus(start)

    def set_focus(self, room_name):
        self.focus = self[room_name]
        self.focus.focus()

    def get_portal_dest_from_xy(self, x, y, room=''):
        """If a portal exists at (x, y) in the given room, return that
        portal's destination room. Else, return None.

        If room tests False, use the focused room.
        """
        if not room:
            room = self.focus.name
        destname = self.portals[room][y][x]
        if not destname:
            return None
        return destname

    def get_dest_portal_xy(self, to_room, from_room=''):
        """If a portal from room named `from_room` to room named
        `to_room` exists, return its x and y coordinates.
        
        If `from_room` tests False, use the focused room.
        """
        if not from_room:
            from_room = self.focus.name
        portals = self.portals[to_room]
        for y in range(len(portals)):
            for x in range(len(portals[y])):
                p = portals[y][x]
                if not p:
                    continue
                if p == from_room:
                    return x, y
    
    def add_entity(self, entity, x, y, z=None, room=''):
        """Add the given entity to the given room at (x, y, z).
        
        If z is None, or out of range, add a layer to the top and put the
        entity there. Otherwise, if no entity exists at [z][y][x], place
        it there, else insert a new layer at z + 1 and place it there.

        If room tests False, add the entity to the focused room.
        """
        room = self[room] if room else self.focus

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

    def pop_entity(self, x, y, z, room=''):
        """Remove and return the entity at (x, y, z)."""
        room = self[room] if room else self.focus
        
        entity = room[z][y][x]
        room[z][y][x] = None
        return entity
    
    def step_entity(self, entity, xstep, ystep):
        """Move entity from its current position by (xstep, ystep),
        changing the direction of the entity to reflect the direction of
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

    def portal_entity(self, entity, x, y):
        """If a portal exists at (x, y), transfer entity from its
        current room to the destination room of the portal.
        """
        destname = self.portals[self.focus.name][y][x]
        z = self.focus.get_coords(entity)[2]
        self.pop_entity(x, y, z)
        x, y = self.get_dest_portal_xy(destname)
        self.add_entity(entity, x, y, z, destname)
