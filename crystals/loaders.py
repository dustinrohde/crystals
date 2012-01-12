"""tools for loading game resources"""
import os
import sys

import pyglet

import world
from crystals import entity
from crystals.world import Room

__all__ = ['world']

RES_PATH = os.path.join('crystals', 'res') # default path to game resources
DATA_PATH = os.path.join('crystals', 'data') # default path to game data
ENTITY_TYPES = ('terrain', 'feature', 'item', 'character') # entity categories

class ImageDict(dict):
    """Loads game images."""

    def __init__(self, img_dir, res_path=RES_PATH):
        """Load all images in RES_PATH/img_dir.

        Images can then be accessed dict-style, where each key is an
        image's filename without the extension, e.g. 'goblin.png' --> 'goblin'.
        """
        path = os.path.join(res_path, 'image', img_dir)
        for filename in os.listdir(path):
            key = filename.rsplit('.', 1)[0]
            image = pyglet.image.load(os.path.join(path, filename))
            self[key] = image


class WorldLoader(object):
    """Loads the game world."""

    def __init__(self, batch, data_path=DATA_PATH, res_path=RES_PATH):
        self.batch = batch
        self.res_path = res_path
        self.world_path = os.path.join(self.res_path, 'world')
        self.room_path = os.path.join(self.world_path, 'rooms')
        self.rooms = {}
        self.images = dict.fromkeys(ENTITY_TYPES)
        self.ignore_char = '.' # char to ignore when reading room maps

        # add data_path to PYTHON_PATH and import world data
        sys.path.insert(0, os.path.join(data_path, 'world'))
        self.config = dict((e, __import__(e)) for e in ENTITY_TYPES)
        self.config['maps'] = __import__('maps')

    def load_images(self, entity_type):
        """Load all images for the given entity type."""
        self.images[entity_type] = ImageDict(entity_type, self.res_path)

    def load_entity_args(self, room_name, entity_type):
        """Load the arguments for each entity for a given room and type.
        
        Return a dict object mapping the entity symbols to the argument
        tuples. If no data is found, return None.
        """
        images = ImageDict(entity_type)
        # load config object from DATA_PATH/world
        config = getattr(self.config[entity_type], room_name)

        entity_args = {}
        for archetype_name, archetype in config.entities.iteritems():
            default_params = config.defaults[archetype_name].copy()
            for entity_name, params in archetype.iteritems():
                params = params.copy() # Leave module data intact
                # If name is not given in any params, generate one
                if 'name' not in params and 'name' not in default_params:
                    params['name'] = archetype_name + '-' + entity_name
                # Replace missing entries from params with entries from
                # default_params
                for key in ('name', 'walkable', 'image', 'color', 'symbol'):
                    if key not in params:
                        params[key] = default_params[key]
                # Combine image and color params to get the image name
                params['image'] += '-' + params.pop('color')
                # Replace the image name with the actual image object
                params['image'] = images[params['image']]
                
                # Map the symbol to a corresponding Entity instance
                symbol = params.pop('symbol')
                entity_args[symbol] = params

        return entity_args

    def load_room(self, room_name):
        """Load and return a Room instance, given a room name."""
        atlas = getattr(self.config['maps'], room_name)

        grid = []
        for entity_type in ENTITY_TYPES:
            if not hasattr(atlas, entity_type):
                continue
            entity_args = self.load_entity_args(room_name, entity_type)
            symbols = getattr(atlas, entity_type)
            for layer in symbols:
                grid.append([])
                for row in layer.strip().split('\n'):
                    grid[-1].append([])
                    for symbol in row.strip():
                        if symbol == '.':
                            # append None when a '.' (period) is encountered
                            grid[-1][-1].append(None)
                        else:
                            entity_ = entity.Entity(**entity_args[symbol])
                            grid[-1][-1].append(entity_)

        return Room(grid, self.batch)

    def load_world(self):
        pass
