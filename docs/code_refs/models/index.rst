Enumerations and Data Models
============================

.. autoclass:: models.puzzle_module.PuzzleModule
   :members: new, load

.. autoclass:: models.grid_model.AbstractGrid
   :members: new, shape, colors, reset, _tighten, gravitize, is_hidden, adjacent

.. autoclass:: models.grid_model.MoveGrid
   :show-inheritance:
   :members: new, reorient, finalize

.. autoclass:: models.grid_model.BoardGrid
   :show-inheritance:
   :members: applyMove, revertMove, revert

.. autoclass:: models.grid_model.HoverGrid
   :show-inheritance:
   :members: new, fit_move, assign_move
             
.. autoclass:: models.grid_model.Move

.. autoclass:: models.puyo_model.Puyo
   :show-inheritance:

.. autoclass:: models.puyo_model.Direc
   :show-inheritance:
   :members:

.. autoclass:: models.puyo_model.EnumCycle
   :show-inheritance:
   :members:
