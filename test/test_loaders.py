import os
import sys
import random

import pyglet
from nose.tools import *

import crystals
from crystals import loaders
from crystals import entity
from test.helpers import *

@raises(loaders.DataError)
def test_DataError():
    raise loaders.DataError()


def test_ImageDict():
    for img_dir in ('terrain', 'item', 'character', 'interface'):
        images = loaders.ImageDict(img_dir, res_path=RES_PATH)

        filenames = os.listdir(
            os.path.join(RES_PATH, 'image', img_dir))
        assert len(images) == len(filenames) 
        # Test that each file in img_dir is represented by an entry
        # in `ImageLoader`
        for key, image in images.iteritems():
            assert isinstance(image, pyglet.image.AbstractImage)
            match = False
            for filename in filenames:
                if key == filename.rsplit('.', 1)[0]:
                    match = True
            assert match


class TestWorldLoader(TestCase):

    def setup(self):
        super(TestWorldLoader, self).setup()
        self.loader = loaders.WorldLoader(data_path=DATA_PATH,
                                          res_path=RES_PATH)

    def test_init(self):
        assert self.loader.images == {'terrain': None, 'item': None,
                                      'feature': None, 'character': None}
        assert os.path.join(DATA_PATH, 'world') in sys.path

    def test_load_images(self):
        for atype in loaders.ARCHETYPES:
            self.loader.load_images(atype)
            assert isinstance(self.loader.images[atype], loaders.ImageDict)

    def test_load_archetype_args(self):
        archetype_args = self.loader.load_archetype_args('TestRoom1', 'terrain')
        assert all(type(key) == str for key in archetype_args.iterkeys())
        assert all(type(value) == dict for value in archetype_args.itervalues())

        keys = ('wall-horiz', 'wall-vert', 'floor-rough', 'floor-smooth')
        names = ('a wall', 'towering wall', 'cobbled floor', 'a smooth floor')
        walkables = (False, False, True, True)
                  
        for key, name, walkable in zip(keys, names, walkables):
            entity_ = entity.Entity(**archetype_args[key])
            assert isinstance(entity_, entity.Entity)
            assert isinstance(entity_, pyglet.sprite.Sprite)
            assert entity_.name == name
            assert entity_.walkable == walkable

            entity_.batch = self.batch
            entity_.position = [random.randint(200, 400)] * 2

        #self.run_app()

    def test_load_entity_args_(self):
        entity_args = self.loader.load_entity_args('TestRoom1')
        assert all(type(key) == str for key in entity_args.iterkeys())
        assert all(type(value) == dict for value in entity_args.itervalues())
        archetype_args = self.loader.load_archetype_args('TestRoom1', 'terrain')
        assert len(entity_args) == len(archetype_args)

    @raises(loaders.DataError)
    def test_load_entity_args_raises_exception(self):
        entity_args = self.loader.load_entity_args('NotARoomName')

    def test_load_room(self):
        room1 = self.loader.load_room('TestRoom1')
        assert isinstance(room1, crystals.world.Room)
                
    def test_load_world(self):
        world = self.loader.load_world()
        assert isinstance(world, crystals.world.World)


        # rough integrity test for room.grid ---------------------------
        room1 = world['TestRoom1']
        archetype = 'terrain'
        img = loaders.ImageDict(archetype, RES_PATH)
        vwall = entity.Entity(archetype, 'towering wall', False,
                              img['wall-vert-blue'], room1.batch)
        hwall = entity.Entity(archetype, 'a wall', False,
                              img['wall-horiz-blue'], room1.batch)
        floora = entity.Entity(archetype, 'cobbled floor', True,
                               img['floor-a-red'], room1.batch)
        floorb = entity.Entity(archetype, 'a smooth floor', True,
                               img['floor-b-red'], room1.batch)

        room2 = [
            [[vwall, hwall, vwall],
             [vwall, floorb, vwall],
             [vwall, floorb, floorb]
            ],
            [[floora, floora, floora],
             [floora, None, floora],
             [floora, None, None]]]

        for layer1, layer2 in zip(room1, room2):
            for row1, row2 in zip(layer1, layer2):
                for e1, e2 in zip(row1, row2):
                    if e1 != None and e2 != None:
                        assert e1.name == e2.name
                        assert e1.walkable == e2.walkable
                        assert e1.batch == e2.batch
