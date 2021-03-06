CRY§TAL§ TODO
=============

Restructure crystals.resource module - BRAINSTORM
.............................................

    * ``crystals.loader`` -- Loads bundled images and API scripts
    * ``api.action`` -- API for defining entity actions
    * ``api.entity`` -- API for defining entities
    * ``api.world`` -- API for defining the world
    * ``api.plot`` -- API for defining the plot sequence

Convert classes to module namespaces (where possible)
.....................................................

    * Restructure package crystals.app:
        
        * ``crystals.app`` -- Gamemode objects

        * ``crystals.app.worldmode`` -- All attributes and methods from
          crystals.app.WorldMode will be adapted to this module object

    * Adapt ``crystals.game.Game`` to a module namespace.

Reexamine unit tests
....................

    * Use mocks for EVERYTHING except the object being tested,
      pyglet objects, and builtins/stdlib.
    * Disentangle tests from each other, making them true "unit"
      tests.
    * Convert test classes with methods to functions anywhere this
      would make things clearer.
    * Decide on testing practices and stick with them:

        * Test class definitions serve as semantic wrappers for test
          definitions, and follow the following format::

            def Test{Object}([bases...]):
                {test definitions}

        * Test definitions are always functions or methods of test
          classes, and follow the following format::

            def Test{Callable}_{Condition}_{ExpectedResult}([self]):
                {test body}

        * Test each input condition separately; however, any number of
          changes resulting from the same condtion may be checked in
          the same test.
        * Tests are completely isolated, uses setup and teardown methods
          for shared code. This will also exemplify D.R.Y. if utilized.
        * Test only public attributes; provide public accessors for
          private attributes if neccesary for good test coverage.

Extend the game's infobox
.........................
    * Text that, after wrapping, doesn't fit vertically prompts the
      user to scroll by pressing space.

Implement complex interactions between PC and NPCs
..................................................
    * Actions can be executed in a given order, a given number of
      times each.
    * 'RequireState' action moves execution back to the previous action
      if given plot state is not found True.
        * This would allow for indefinite repetition of the same action.
    * Write class Interaction in world.entity to coordinate actions.

        * Constructor takes two arguments, on_engage and on_step,
          which specify the actions to execute when engaged with from
          an adjacent entity and when stepped upon, respectively.
            * Each argument is a list of actions. When the corresp.
              call is made, the next action in the list will be executed.
            * Methods engage(actor, reciever) and step(actor, reciever)
              are responsible for executing the actions.

    * Change world.Entity argument 'actions' to 'interaction', which
      takes an Interaction object.
    * (Eventually) write a factory function IndexedInteraction which
      takes a list of indices for each action list and executes the
      actions in the indexed order. This would make it easy to repeat
      actions.
      
Prepare and send the game to Julian Wass
........................................
    * Write a demonstration world.
    * Get everything working on Windows.
    * Create a Windows executable for the game.
    * Email everything to Julian with a verbose explanation.

Implement the pause menu
........................
    * Can be opened anytime in world mode.
    * Lets the user check her party's information, save the game,
      and quit the game.

Implement game saves
....................
    * Use the cpickle module to serialize WorldMode instance game.wmode.
    * Add 'load game' button to main menu that only appears when a pickled
      WorldMode instance exists.

Implement game overs
....................
    * Add a 'GameOver' entry to the plot set to False.
    * At the end of each iteration of the main loop, if 'GameOver'
      is False, end the game.

Implement visual effects
........................
    * Entities smoothly "scroll" between tiles as they move.
    * Entities can have animated images.
    * Entity animations can be repeated in sequence, paused, or set
      to a particular frame.
    * Entities visually rotate to match the direction of their last
      movement.

        * Most will only have right and left rotations.
        * The player and party members will have all four directions.

Beautify interface
..................
    * Add background image to main menu.
    * Replace boring line border panels with graphical panels in all
      gui elements.
