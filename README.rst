CRY§TAL§
========
A top-down RPG/Adventure based on the album CRYSTALS by `Julian Wass <http://julianwass.bandcamp.com>`_
-------------------------------------------------------------------------------------------------------

Crystals is currently under active development by me, Dustin Rohde, and
is considered to be in alpha. Active development is currently taking
place in the branch 'master'.

You must have `python <http://python.org>`_ 2.7.2 and `pyglet <http://pyglet.org>`_ >= 1.1.4
installed to run crystals. It is not yet known whether crystals runs
properly on any operating system other than Linux, or with any previous
versions of pyglet.

To run the game::
    
    python run.py

At this stage in development, click 'new game' after running and you will be presented with a
small test world that tests some of the game's features. To see a more cohesive game world,
give python the `-O` option::

    python -O run.py

This will present whatever I've done towards creating a cohesive world. This does
not reflect what the finished game will be like.

To run the test suite, you must have `nose <http://pypi.python.org/pypi/nose>`_ >= 1.1.2
installed, then::

    nosetests test

Nose is configured in 'setup.cfg'.
